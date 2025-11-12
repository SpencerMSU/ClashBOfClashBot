"""Asynchronous scanner that iterates over every possible clan tag and archives wars."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Sequence, Set

from config.config import config
from src.models.war import WarToSave
from src.services.coc_api import CocApiClient, determine_war_result
from src.services.database import DatabaseService
from src.utils.war_processing import analyze_attacks

logger = logging.getLogger(__name__)


class ClanTagEnumerator:
    """Iterate over the Clash of Clans tag space (base-14 alphabet)."""

    ALPHABET: Sequence[str] = tuple("0289PYLQGRJCUV")

    def __init__(self, min_length: int = 8, max_length: int = 10):
        self.min_length = min_length
        self.max_length = max_length

    def _clean(self, tag: Optional[str]) -> Optional[str]:
        if not tag:
            return None
        return tag.replace("#", "").strip().upper()

    def next_after(self, last_tag: Optional[str]) -> Optional[str]:
        clean_tag = self._clean(last_tag)
        if not clean_tag:
            return "#" + self.ALPHABET[0] * self.min_length

        digits: List[int] = []
        for char in clean_tag:
            if char not in self.ALPHABET:
                # Unknown symbol -> restart from smallest combination.
                return "#" + self.ALPHABET[0] * self.min_length
            digits.append(self.ALPHABET.index(char))

        idx = len(digits) - 1
        while idx >= 0:
            digits[idx] += 1
            if digits[idx] < len(self.ALPHABET):
                break
            digits[idx] = 0
            idx -= 1

        if idx < 0:
            if len(digits) >= self.max_length:
                return None
            digits = [0] * (len(digits) + 1)

        return "#" + "".join(self.ALPHABET[d] for d in digits)


class GlobalWarScanner:
    """Brute-force scanner that walks over clan tags and stores every available war."""

    CURSOR_KEY = "global_scan_cursor"
    SENTINEL = object()

    def __init__(
        self,
        db_service: DatabaseService,
        coc_client: CocApiClient,
        *,
        concurrency: int = 3,
        queue_prefill: int = 60,
    ):
        self.db_service = db_service
        self.coc_client = coc_client
        self.concurrency = max(1, concurrency)
        self.queue_prefill = max(self.concurrency * 2, queue_prefill)

        self.tag_queue: asyncio.Queue[object] = asyncio.Queue(maxsize=self.queue_prefill)
        self.stop_event = asyncio.Event()
        self.enumerator = ClanTagEnumerator()
        self.cursor: Optional[str] = None
        self._stats_lock = asyncio.Lock()
        self._processed_tags = 0
        self._saved_wars = 0

    async def run(self, max_tags: Optional[int] = None):
        """Start the scanning loop. Runs until cancelled or all tags are exhausted."""
        await self._seed_known_tags()
        self.cursor = await self.db_service.get_scan_state(self.CURSOR_KEY)
        manager_task = asyncio.create_task(self._queue_manager(max_tags))
        worker_tasks = [asyncio.create_task(self._worker(worker_id, max_tags)) for worker_id in range(self.concurrency)]

        try:
            await asyncio.gather(*worker_tasks)
        finally:
            self.stop_event.set()
            await manager_task
            logger.info(
                "[scanner] Finished. Processed %s clan tags, saved %s wars.",
                self._processed_tags,
                self._saved_wars,
            )

    async def _queue_manager(self, max_tags: Optional[int]):
        """Continuously keep the internal queue filled with tags to scan."""
        try:
            while not self.stop_event.is_set():
                if await self._should_stop(max_tags):
                    break

                if self.tag_queue.full():
                    await asyncio.sleep(0.05)
                    continue

                needed = self.queue_prefill - self.tag_queue.qsize()
                if needed <= 0:
                    await asyncio.sleep(0.05)
                    continue

                reserved = await self.db_service.reserve_global_scan_candidates(needed)
                if reserved:
                    for tag in reserved:
                        await self.tag_queue.put(tag)
                    continue

                next_tag = await self._generate_next_tag()
                if not next_tag:
                    logger.info("[scanner] Tag space exhausted.")
                    break

                await self.db_service.enqueue_global_clan_tag(next_tag, "bruteforce")
                # Next loop iteration will pick it via reserve().
        finally:
            for _ in range(self.concurrency):
                await self.tag_queue.put(self.SENTINEL)

    async def _generate_next_tag(self) -> Optional[str]:
        next_tag = self.enumerator.next_after(self.cursor)
        if not next_tag:
            return None
        self.cursor = next_tag
        await self.db_service.set_scan_state(self.CURSOR_KEY, next_tag)
        return next_tag

    async def _worker(self, worker_id: int, max_tags: Optional[int]):
        while True:
            tag_obj = await self.tag_queue.get()
            if tag_obj is self.SENTINEL:
                self.tag_queue.task_done()
                break

            clan_tag = str(tag_obj)
            try:
                await self._process_clan(clan_tag)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("[scanner] Worker %s failed on %s: %s", worker_id, clan_tag, exc)
                await self.db_service.update_global_scan_result(clan_tag, "failed", str(exc))
            finally:
                await self._increment_processed(max_tags)
                self.tag_queue.task_done()

    async def _increment_processed(self, max_tags: Optional[int]):
        async with self._stats_lock:
            self._processed_tags += 1
            if max_tags and self._processed_tags >= max_tags:
                self.stop_event.set()

    async def _should_stop(self, max_tags: Optional[int]) -> bool:
        if self.stop_event.is_set():
            return True
        if not max_tags:
            return False
        async with self._stats_lock:
            return self._processed_tags >= max_tags

    async def _process_clan(self, clan_tag: str):
        logger.debug("[scanner] Processing clan %s", clan_tag)
        async with self.coc_client as client:
            war_log = await client.get_clan_war_log(clan_tag)

        if not war_log or "items" not in war_log:
            note = "war log not available or clan does not exist"
            await self.db_service.update_global_scan_result(clan_tag, "skipped", note)
            return

        wars = war_log.get("items", [])
        wars_saved = 0
        for war_entry in wars:
            war_model = self._war_entry_to_model(war_entry)
            if not war_model:
                continue
            if await self.db_service.war_exists(war_model.end_time):
                continue
            await self.db_service.save_war(war_model)
            wars_saved += 1
            async with self._stats_lock:
                self._saved_wars += 1
            await self._discover_tags(clan_tag, war_entry)

        note = f"{wars_saved} wars saved" if wars_saved else "no new wars"
        await self.db_service.update_global_scan_result(clan_tag, "done", note)

    def _war_entry_to_model(self, war_entry: Dict[str, Any]) -> Optional[WarToSave]:
        result = war_entry.get("result")
        if result not in {"win", "lose", "tie"}:
            return None

        end_time = war_entry.get("endTime")
        clan_data = war_entry.get("clan", {}) or {}
        opponent_data = war_entry.get("opponent", {}) or {}
        if not end_time or not clan_data or not opponent_data:
            return None

        team_size = war_entry.get("teamSize", len(clan_data.get("members", [])))
        clan_stars = clan_data.get("stars", 0)
        opponent_stars = opponent_data.get("stars", 0)
        clan_destruction = clan_data.get("destructionPercentage", 0.0)
        opponent_destruction = opponent_data.get("destructionPercentage", 0.0)
        clan_attacks_used, total_violations, attacks_by_member = analyze_attacks(clan_data)

        resolved_result = result or determine_war_result(clan_stars, opponent_stars)

        return WarToSave(
            end_time=end_time,
            opponent_name=opponent_data.get("name", "Unknown opponent"),
            team_size=team_size,
            clan_stars=clan_stars,
            opponent_stars=opponent_stars,
            clan_destruction=clan_destruction,
            opponent_destruction=opponent_destruction,
            clan_attacks_used=clan_attacks_used,
            result=resolved_result,
            is_cwl_war=bool(war_entry.get("isCwlWar", False)),
            total_violations=total_violations,
            attacks_by_member=attacks_by_member,
        )

    async def _discover_tags(self, source_tag: str, war_entry: Dict[str, Any]):
        discovered: Set[str] = set()
        for side in ("clan", "opponent"):
            tag = war_entry.get(side, {}).get("tag")
            if tag:
                discovered.add(self._normalise_tag(tag))

        source = self._normalise_tag(source_tag)
        for tag in discovered:
            if not tag or tag == source:
                continue
            await self.db_service.enqueue_global_clan_tag(tag, source)

    async def _seed_known_tags(self):
        seeds = set(await self.db_service.get_all_known_clan_tags())
        if config.OUR_CLAN_TAG:
            seeds.add(self._normalise_tag(config.OUR_CLAN_TAG))
        for tag in seeds:
            if tag:
                await self.db_service.enqueue_global_clan_tag(tag, "seed")

    @staticmethod
    def _normalise_tag(tag: Optional[str]) -> str:
        if not tag:
            return ""
        tag = tag.strip().upper()
        return tag if tag.startswith("#") else f"#{tag}"


__all__ = ["GlobalWarScanner"]
