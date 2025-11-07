"""SQLite-backed database service for the ClashBot project."""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

try:
    import aiosqlite
except ImportError as exc:  # pragma: no cover - environment specific
    raise RuntimeError(
        "Пакет 'aiosqlite' обязателен для работы с локальной базой данных. Установите его командой 'pip install aiosqlite'."
    ) from exc

from config.config import config
from src.models.building import BuildingSnapshot, BuildingTracker
from src.models.linked_clan import LinkedClan
from src.models.subscription import Subscription
from src.models.user import User
from src.models.user_profile import UserProfile
from src.models.war import WarToSave

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Вспомогательные функции преобразования дат
# ---------------------------------------------------------------------------

def _timestamp_to_iso(value: Optional[datetime | str]) -> Optional[str]:
    if isinstance(value, datetime):
        return value.isoformat()
    if value is None:
        return None
    return str(value)


def _parse_iso(value: Optional[Any]) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


class DatabaseService:
    """Асинхронный слой работы с базой данных на основе SQLite."""

    def __init__(self, database_path: Optional[str] = None):
        db_path = database_path or getattr(config, "DATABASE_PATH", "")
        if not db_path:
            raise RuntimeError("DATABASE_PATH не настроен в конфигурации")
        self.database_path = self._normalise_path(db_path)
        self._conn: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()
        self._lock_owner: Optional[asyncio.Task] = None
        self._lock_depth = 0

    @staticmethod
    def _normalise_path(raw_path: str) -> str:
        path = Path(raw_path)
        if not path.is_absolute():
            project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            path = project_root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    async def _ensure_connection(self) -> aiosqlite.Connection:
        if self._conn is None:
            self._conn = await aiosqlite.connect(self.database_path)
            self._conn.row_factory = aiosqlite.Row
            await self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    async def close(self):
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def ping(self) -> bool:
        row = await self._fetchone("SELECT 1")
        return row is not None

    async def init_db(self):
        conn = await self._ensure_connection()
        async with self._lock:
            await conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    player_tag TEXT
                );

                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    player_tag TEXT NOT NULL,
                    profile_name TEXT,
                    is_primary INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    UNIQUE (telegram_id, player_tag)
                );
                CREATE INDEX IF NOT EXISTS idx_user_profiles_telegram ON user_profiles(telegram_id);

                CREATE TABLE IF NOT EXISTS wars (
                    end_time TEXT PRIMARY KEY,
                    opponent_name TEXT,
                    team_size INTEGER,
                    clan_stars INTEGER,
                    opponent_stars INTEGER,
                    clan_destruction REAL,
                    opponent_destruction REAL,
                    clan_attacks_used INTEGER,
                    result TEXT,
                    is_cwl_war INTEGER DEFAULT 0,
                    total_violations INTEGER,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS war_attacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    war_end_time TEXT NOT NULL,
                    attacker_tag TEXT,
                    attacker_name TEXT,
                    defender_tag TEXT,
                    stars INTEGER,
                    destruction REAL,
                    attack_order INTEGER,
                    timestamp INTEGER,
                    is_violation INTEGER,
                    FOREIGN KEY (war_end_time) REFERENCES wars(end_time) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_war_attacks_war ON war_attacks(war_end_time);

                CREATE TABLE IF NOT EXISTS subscriptions (
                    telegram_id INTEGER PRIMARY KEY,
                    subscription_type TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    is_active INTEGER,
                    payment_id TEXT,
                    amount REAL,
                    currency TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS notifications (
                    telegram_id INTEGER PRIMARY KEY,
                    enabled_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS building_trackers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    player_tag TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    last_check TEXT,
                    UNIQUE (telegram_id, player_tag)
                );
                CREATE INDEX IF NOT EXISTS idx_building_trackers_active ON building_trackers(is_active);

                CREATE TABLE IF NOT EXISTS building_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_tag TEXT NOT NULL,
                    snapshot_time TEXT NOT NULL,
                    buildings_data TEXT,
                    UNIQUE (player_tag, snapshot_time)
                );

                CREATE TABLE IF NOT EXISTS player_stats_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_tag TEXT NOT NULL,
                    snapshot_time TEXT NOT NULL,
                    donations INTEGER,
                    UNIQUE (player_tag, snapshot_time)
                );

                CREATE TABLE IF NOT EXISTS linked_clans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    clan_tag TEXT NOT NULL,
                    clan_name TEXT,
                    slot_number INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    UNIQUE (telegram_id, slot_number),
                    UNIQUE (telegram_id, clan_tag)
                );

                CREATE TABLE IF NOT EXISTS cwl_seasons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    season_date TEXT UNIQUE,
                    bonus_results_json TEXT
                );
                """
            )
            await conn.commit()
        logger.info("✅ SQLite схема инициализирована")
        await self._grant_permanent_proplus_subscription(5545099444)

    async def _grant_permanent_proplus_subscription(self, telegram_id: int):
        try:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=36500)
            subscription = Subscription(
                telegram_id=telegram_id,
                subscription_type="proplus_permanent",
                start_date=start_date,
                end_date=end_date,
                is_active=True,
                payment_id="PERMANENT_GRANT",
                amount=0.0,
            )
            await self.save_subscription(subscription)
            logger.info("🎁 Permanent PRO PLUS subscription ensured for %s", telegram_id)
        except Exception as exc:  # pragma: no cover - safety net
            logger.error("Ошибка при предоставлении вечной подписки: %s", exc)

    # ------------------------------------------------------------------
    # Низкоуровневые операции
    # ------------------------------------------------------------------
    async def _acquire_lock(self):
        current = asyncio.current_task()
        if self._lock_owner is current:
            self._lock_depth += 1
            return
        await self._lock.acquire()
        self._lock_owner = current
        self._lock_depth = 1

    async def _release_lock(self):
        current = asyncio.current_task()
        if self._lock_owner is not current:
            raise RuntimeError("Попытка освободить блокировку не владельцем")
        self._lock_depth -= 1
        if self._lock_depth == 0:
            self._lock_owner = None
            self._lock.release()

    async def _execute(
        self,
        query: str,
        params: Sequence[Any] | Iterable[Any] = (),
        *,
        commit: bool = False,
    ) -> None:
        conn = await self._ensure_connection()
        await self._acquire_lock()
        try:
            await conn.execute(query, tuple(params))
            if commit:
                await conn.commit()
        finally:
            await self._release_lock()

    async def _fetchone(self, query: str, params: Sequence[Any] = ()):
        conn = await self._ensure_connection()
        await self._acquire_lock()
        try:
            cursor = await conn.execute(query, tuple(params))
            row = await cursor.fetchone()
            await cursor.close()
            return row
        finally:
            await self._release_lock()

    async def _fetchall(self, query: str, params: Sequence[Any] = ()):
        conn = await self._ensure_connection()
        await self._acquire_lock()
        try:
            cursor = await conn.execute(query, tuple(params))
            rows = await cursor.fetchall()
            await cursor.close()
            return rows
        finally:
            await self._release_lock()

    # ------------------------------------------------------------------
    # Пользователи
    # ------------------------------------------------------------------
    async def find_user(self, telegram_id: int) -> Optional[User]:
        row = await self._fetchone(
            "SELECT telegram_id, COALESCE(player_tag, '') AS player_tag FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        if row:
            return User(telegram_id=row["telegram_id"], player_tag=row["player_tag"] or "")
        return None

    async def save_user(self, user: User) -> bool:
        await self._execute(
            """
            INSERT INTO users (telegram_id, player_tag)
            VALUES (?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET player_tag=excluded.player_tag
            """,
            (user.telegram_id, user.player_tag),
            commit=True,
        )
        return True

    async def delete_user(self, telegram_id: int) -> bool:
        await self._execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,), commit=True)
        return True

    async def get_all_users(self) -> List[Dict[str, Any]]:
        rows = await self._fetchall("SELECT telegram_id, player_tag FROM users ORDER BY telegram_id ASC")
        return [{"telegram_id": row["telegram_id"], "player_tag": row["player_tag"]} for row in rows]

    # ------------------------------------------------------------------
    # Профили пользователей
    # ------------------------------------------------------------------
    async def save_user_profile(self, profile: UserProfile) -> bool:
        conn = await self._ensure_connection()
        await self._acquire_lock()
        try:
            await conn.execute("BEGIN")
            if profile.is_primary:
                await conn.execute(
                    "UPDATE user_profiles SET is_primary = 0 WHERE telegram_id = ?",
                    (profile.telegram_id,),
                )
            await conn.execute(
                """
                INSERT INTO user_profiles (telegram_id, player_tag, profile_name, is_primary, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(telegram_id, player_tag) DO UPDATE SET
                    profile_name=excluded.profile_name,
                    is_primary=excluded.is_primary,
                    created_at=excluded.created_at
                """,
                (
                    profile.telegram_id,
                    profile.player_tag,
                    profile.profile_name,
                    1 if profile.is_primary else 0,
                    _timestamp_to_iso(profile.created_at) or datetime.now().isoformat(),
                ),
            )
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            await self._release_lock()
        return True

    async def get_user_profiles(self, telegram_id: int) -> List[UserProfile]:
        rows = await self._fetchall(
            """
            SELECT id, telegram_id, player_tag, profile_name, is_primary, created_at
            FROM user_profiles
            WHERE telegram_id = ?
            ORDER BY is_primary DESC, created_at ASC
            """,
            (telegram_id,),
        )
        profiles: List[UserProfile] = []
        for row in rows:
            profiles.append(
                UserProfile(
                    telegram_id=row["telegram_id"],
                    player_tag=row["player_tag"],
                    profile_name=row["profile_name"],
                    is_primary=bool(row["is_primary"]),
                    created_at=_timestamp_to_iso(row["created_at"]),
                    profile_id=row["id"],
                )
            )
        return profiles

    async def delete_user_profile(self, telegram_id: int, player_tag: str) -> bool:
        await self._execute(
            "DELETE FROM user_profiles WHERE telegram_id = ? AND player_tag = ?",
            (telegram_id, player_tag),
            commit=True,
        )
        return True

    async def get_user_profile_count(self, telegram_id: int) -> int:
        row = await self._fetchone(
            "SELECT COUNT(*) AS cnt FROM user_profiles WHERE telegram_id = ?",
            (telegram_id,),
        )
        return int(row["cnt"]) if row else 0

    async def set_primary_profile(self, telegram_id: int, player_tag: str) -> bool:
        conn = await self._ensure_connection()
        await self._acquire_lock()
        try:
            await conn.execute("BEGIN")
            await conn.execute(
                "UPDATE user_profiles SET is_primary = 0 WHERE telegram_id = ?",
                (telegram_id,),
            )
            await conn.execute(
                "UPDATE user_profiles SET is_primary = 1 WHERE telegram_id = ? AND player_tag = ?",
                (telegram_id, player_tag),
            )
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            await self._release_lock()
        row = await self._fetchone(
            "SELECT is_primary FROM user_profiles WHERE telegram_id = ? AND player_tag = ?",
            (telegram_id, player_tag),
        )
        return bool(row and row["is_primary"])

    async def get_primary_profile(self, telegram_id: int) -> Optional[UserProfile]:
        row = await self._fetchone(
            """
            SELECT id, telegram_id, player_tag, profile_name, is_primary, created_at
            FROM user_profiles
            WHERE telegram_id = ? AND is_primary = 1
            ORDER BY created_at ASC
            LIMIT 1
            """,
            (telegram_id,),
        )
        if row:
            return UserProfile(
                telegram_id=row["telegram_id"],
                player_tag=row["player_tag"],
                profile_name=row["profile_name"],
                is_primary=True,
                created_at=_timestamp_to_iso(row["created_at"]),
                profile_id=row["id"],
            )
        return None

    # ------------------------------------------------------------------
    # Войны
    # ------------------------------------------------------------------
    async def save_war(self, war: WarToSave) -> bool:
        now_iso = datetime.now().isoformat()
        conn = await self._ensure_connection()
        await self._acquire_lock()
        try:
            await conn.execute("BEGIN")
            await conn.execute(
                """
                INSERT INTO wars (
                    end_time, opponent_name, team_size, clan_stars, opponent_stars,
                    clan_destruction, opponent_destruction, clan_attacks_used, result,
                    is_cwl_war, total_violations, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(end_time) DO UPDATE SET
                    opponent_name=excluded.opponent_name,
                    team_size=excluded.team_size,
                    clan_stars=excluded.clan_stars,
                    opponent_stars=excluded.opponent_stars,
                    clan_destruction=excluded.clan_destruction,
                    opponent_destruction=excluded.opponent_destruction,
                    clan_attacks_used=excluded.clan_attacks_used,
                    result=excluded.result,
                    is_cwl_war=excluded.is_cwl_war,
                    total_violations=excluded.total_violations,
                    updated_at=excluded.updated_at
                """,
                (
                    war.end_time,
                    war.opponent_name,
                    war.team_size,
                    war.clan_stars,
                    war.opponent_stars,
                    war.clan_destruction,
                    war.opponent_destruction,
                    war.clan_attacks_used,
                    war.result,
                    1 if war.is_cwl_war else 0,
                    war.total_violations,
                    now_iso,
                    now_iso,
                ),
            )
            await conn.execute("DELETE FROM war_attacks WHERE war_end_time = ?", (war.end_time,))
            attack_order = 0
            attacks: List[Sequence[Any]] = []
            for member_tag, attack_list in (war.attacks_by_member or {}).items():
                for attack in attack_list:
                    attack_order += 1
                    attacks.append(
                        (
                            war.end_time,
                            member_tag,
                            attack.get("attacker_name", ""),
                            attack.get("defender_tag", ""),
                            attack.get("stars", 0),
                            attack.get("destruction", 0.0),
                            attack.get("order", attack_order),
                            attack.get("timestamp", 0),
                            1 if attack.get("is_violation", False) else 0,
                        )
                    )
            if attacks:
                await conn.executemany(
                    """
                    INSERT INTO war_attacks (
                        war_end_time, attacker_tag, attacker_name, defender_tag,
                        stars, destruction, attack_order, timestamp, is_violation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    attacks,
                )
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            await self._release_lock()
        return True

    async def war_exists(self, end_time: str) -> bool:
        row = await self._fetchone("SELECT 1 FROM wars WHERE end_time = ?", (end_time,))
        return row is not None

    async def get_subscribed_users(self) -> List[int]:
        rows = await self._fetchall("SELECT telegram_id FROM notifications")
        return [row["telegram_id"] for row in rows]

    async def toggle_notifications(self, telegram_id: int) -> bool:
        if await self.is_notifications_enabled(telegram_id):
            await self.disable_notifications(telegram_id)
            return False
        await self.enable_notifications(telegram_id)
        return True

    async def save_donation_snapshot(self, members: List[Dict], snapshot_time: str = None):
        if not members:
            return
        snapshot_time = snapshot_time or datetime.now().isoformat()
        entries: List[Sequence[Any]] = []
        for member in members:
            player_tag = member.get("tag")
            if not player_tag:
                continue
            entries.append((player_tag, snapshot_time, member.get("donations", 0)))
        if not entries:
            return
        conn = await self._ensure_connection()
        await self._acquire_lock()
        try:
            await conn.executemany(
                """
                INSERT INTO player_stats_snapshots (player_tag, snapshot_time, donations)
                VALUES (?, ?, ?)
                ON CONFLICT(player_tag, snapshot_time) DO UPDATE SET donations=excluded.donations
                """,
                entries,
            )
            await conn.commit()
        finally:
            await self._release_lock()

    async def get_war_list(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        rows = await self._fetchall(
            """
            SELECT end_time, opponent_name, team_size, clan_stars, opponent_stars, result, is_cwl_war
            FROM wars
            ORDER BY end_time DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        return [
            {
                "end_time": row["end_time"],
                "opponent_name": row["opponent_name"],
                "team_size": row["team_size"],
                "clan_stars": row["clan_stars"],
                "opponent_stars": row["opponent_stars"],
                "result": row["result"],
                "is_cwl_war": bool(row["is_cwl_war"]),
            }
            for row in rows
        ]

    async def get_cwl_bonus_data(self, year_month: str) -> List[Dict]:
        row = await self._fetchone(
            "SELECT bonus_results_json FROM cwl_seasons WHERE season_date LIKE ? || '%' LIMIT 1",
            (year_month,),
        )
        if not row:
            return []
        bonus_data = row["bonus_results_json"]
        if not bonus_data:
            return []
        if isinstance(bonus_data, list):
            return bonus_data
        if isinstance(bonus_data, str):
            try:
                parsed = json.loads(bonus_data)
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                logger.error("Ошибка декодирования бонусов CWL за %s", year_month)
        return []

    async def get_cwl_season_donation_stats(self, season_start: str, season_end: str) -> Dict[str, int]:
        rows = await self._fetchall(
            """
            SELECT player_tag, snapshot_time, donations
            FROM player_stats_snapshots
            WHERE snapshot_time BETWEEN ? AND ?
            ORDER BY player_tag ASC, snapshot_time ASC
            """,
            (season_start, season_end),
        )
        stats: Dict[str, int] = {}
        snapshots: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            snapshots.setdefault(row["player_tag"], []).append(
                {
                    "snapshot_time": row["snapshot_time"],
                    "donations": row["donations"],
                }
            )
        for player_tag, entries in snapshots.items():
            if len(entries) >= 2:
                stats[player_tag] = max(0, entries[-1]["donations"] - entries[0]["donations"])
            elif entries:
                stats[player_tag] = entries[0]["donations"]
        return stats

    async def get_cwl_season_attack_stats(self, season_start: str, season_end: str) -> Dict[str, Dict]:
        rows = await self._fetchall(
            """
            SELECT w.end_time, w.is_cwl_war, a.attacker_tag
            FROM wars w
            LEFT JOIN war_attacks a ON a.war_end_time = w.end_time
            WHERE w.end_time BETWEEN ? AND ?
            ORDER BY w.end_time ASC, a.attack_order ASC
            """,
            (season_start, season_end),
        )
        war_attack_counts: Dict[str, Dict[str, int]] = {}
        war_types: Dict[str, bool] = {}
        for row in rows:
            end_time = row["end_time"]
            war_types[end_time] = bool(row["is_cwl_war"])
            attacker_tag = row["attacker_tag"]
            if not attacker_tag:
                continue
            counter = war_attack_counts.setdefault(end_time, {})
            counter[attacker_tag] = counter.get(attacker_tag, 0) + 1

        player_stats: Dict[str, Dict[str, int]] = {}
        for end_time, counter in war_attack_counts.items():
            is_cwl = war_types.get(end_time, False)
            for tag, count in counter.items():
                stats_entry = player_stats.setdefault(
                    tag,
                    {"cwl_attacks": 0, "regular_attacks": 0, "cwl_wars": 0, "regular_wars": 0},
                )
                if is_cwl:
                    stats_entry["cwl_attacks"] += count
                    stats_entry["cwl_wars"] += 1
                else:
                    stats_entry["regular_attacks"] += count
                    stats_entry["regular_wars"] += 1
        return player_stats

    async def get_war_details(self, end_time: str) -> Optional[Dict]:
        war_row = await self._fetchone("SELECT * FROM wars WHERE end_time = ?", (end_time,))
        if not war_row:
            return None
        attack_rows = await self._fetchall(
            """
            SELECT attacker_tag, attacker_name, defender_tag, stars, destruction, attack_order, timestamp, is_violation
            FROM war_attacks
            WHERE war_end_time = ?
            ORDER BY attack_order ASC
            """,
            (end_time,),
        )
        attacks = [
            {
                "attacker_tag": row["attacker_tag"],
                "attacker_name": row["attacker_name"],
                "defender_tag": row["defender_tag"],
                "stars": row["stars"],
                "destruction": row["destruction"],
                "order": row["attack_order"],
                "timestamp": row["timestamp"],
                "is_violation": bool(row["is_violation"]),
            }
            for row in attack_rows
        ]
        return {
            "end_time": war_row["end_time"],
            "opponent_name": war_row["opponent_name"],
            "team_size": war_row["team_size"],
            "clan_stars": war_row["clan_stars"],
            "opponent_stars": war_row["opponent_stars"],
            "clan_destruction": war_row["clan_destruction"],
            "opponent_destruction": war_row["opponent_destruction"],
            "clan_attacks_used": war_row["clan_attacks_used"],
            "result": war_row["result"],
            "is_cwl_war": bool(war_row["is_cwl_war"]),
            "total_violations": war_row["total_violations"],
            "created_at": _timestamp_to_iso(war_row["created_at"]),
            "updated_at": _timestamp_to_iso(war_row["updated_at"]),
            "attacks": attacks,
        }

    # ------------------------------------------------------------------
    # Подписки
    # ------------------------------------------------------------------
    async def save_subscription(self, subscription: Subscription) -> bool:
        now_iso = datetime.now().isoformat()
        await self._execute(
            """
            INSERT INTO subscriptions (
                telegram_id, subscription_type, start_date, end_date,
                is_active, payment_id, amount, currency, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                subscription_type=excluded.subscription_type,
                start_date=excluded.start_date,
                end_date=excluded.end_date,
                is_active=excluded.is_active,
                payment_id=excluded.payment_id,
                amount=excluded.amount,
                currency=excluded.currency,
                updated_at=excluded.updated_at
            """,
            (
                subscription.telegram_id,
                subscription.subscription_type,
                _timestamp_to_iso(subscription.start_date),
                _timestamp_to_iso(subscription.end_date),
                1 if subscription.is_active else 0,
                subscription.payment_id,
                subscription.amount,
                subscription.currency or "RUB",
                now_iso,
                now_iso,
            ),
            commit=True,
        )
        return True

    async def get_subscription(self, telegram_id: int) -> Optional[Subscription]:
        row = await self._fetchone(
            """
            SELECT telegram_id, subscription_type, start_date, end_date, is_active,
                   payment_id, amount, currency
            FROM subscriptions WHERE telegram_id = ?
            """,
            (telegram_id,),
        )
        if not row:
            return None
        return Subscription(
            telegram_id=row["telegram_id"],
            subscription_type=row["subscription_type"] or "",
            start_date=_parse_iso(row["start_date"]) or datetime.now(),
            end_date=_parse_iso(row["end_date"]) or datetime.now(),
            is_active=bool(row["is_active"]),
            payment_id=row["payment_id"],
            amount=float(row["amount"]) if row["amount"] is not None else None,
            currency=row["currency"] or "RUB",
        )

    async def extend_subscription(self, telegram_id: int, additional_days: int) -> bool:
        subscription = await self.get_subscription(telegram_id)
        if not subscription:
            return False
        subscription.end_date = subscription.end_date + timedelta(days=additional_days)
        subscription.is_active = True
        return await self.save_subscription(subscription)

    async def deactivate_subscription(self, telegram_id: int) -> bool:
        await self._execute(
            "UPDATE subscriptions SET is_active = 0, updated_at = ? WHERE telegram_id = ?",
            (datetime.now().isoformat(), telegram_id),
            commit=True,
        )
        return True

    async def get_expired_subscriptions(self) -> List[Subscription]:
        rows = await self._fetchall("SELECT * FROM subscriptions WHERE is_active = 1")
        now = datetime.now()
        results: List[Subscription] = []
        for row in rows:
            end_date = _parse_iso(row["end_date"]) or now
            if end_date < now:
                results.append(
                    Subscription(
                        telegram_id=row["telegram_id"],
                        subscription_type=row["subscription_type"] or "",
                        start_date=_parse_iso(row["start_date"]) or now,
                        end_date=end_date,
                        is_active=True,
                        payment_id=row["payment_id"],
                        amount=float(row["amount"]) if row["amount"] is not None else None,
                        currency=row["currency"] or "RUB",
                    )
                )
        return results

    async def is_notifications_enabled(self, telegram_id: int) -> bool:
        row = await self._fetchone("SELECT 1 FROM notifications WHERE telegram_id = ?", (telegram_id,))
        return row is not None

    async def enable_notifications(self, telegram_id: int) -> bool:
        await self._execute(
            """
            INSERT INTO notifications (telegram_id, enabled_at)
            VALUES (?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET enabled_at=excluded.enabled_at
            """,
            (telegram_id, datetime.now().isoformat()),
            commit=True,
        )
        return True

    async def disable_notifications(self, telegram_id: int) -> bool:
        await self._execute("DELETE FROM notifications WHERE telegram_id = ?", (telegram_id,), commit=True)
        return True

    async def get_notification_users(self) -> List[int]:
        return await self.get_subscribed_users()

    # ------------------------------------------------------------------
    # Отслеживание строений
    # ------------------------------------------------------------------
    async def save_building_tracker(self, tracker: BuildingTracker) -> bool:
        await self._execute(
            """
            INSERT INTO building_trackers (
                telegram_id, player_tag, is_active, created_at, last_check
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id, player_tag) DO UPDATE SET
                is_active=excluded.is_active,
                created_at=excluded.created_at,
                last_check=excluded.last_check
            """,
            (
                tracker.telegram_id,
                tracker.player_tag,
                1 if tracker.is_active else 0,
                _timestamp_to_iso(tracker.created_at) or datetime.now().isoformat(),
                _timestamp_to_iso(tracker.last_check),
            ),
            commit=True,
        )
        return True

    async def get_building_tracker(self, telegram_id: int) -> Optional[BuildingTracker]:
        trackers = await self.get_user_building_trackers(telegram_id)
        return trackers[0] if trackers else None

    async def get_user_building_trackers(self, telegram_id: int) -> List[BuildingTracker]:
        rows = await self._fetchall(
            "SELECT telegram_id, player_tag, is_active, created_at, last_check FROM building_trackers WHERE telegram_id = ?",
            (telegram_id,),
        )
        trackers: List[BuildingTracker] = []
        for row in rows:
            trackers.append(
                BuildingTracker(
                    telegram_id=row["telegram_id"],
                    player_tag=row["player_tag"],
                    is_active=bool(row["is_active"]),
                    created_at=_timestamp_to_iso(row["created_at"]),
                    last_check=_timestamp_to_iso(row["last_check"]),
                )
            )
        return trackers

    async def get_building_tracker_for_profile(self, telegram_id: int, player_tag: str) -> Optional[BuildingTracker]:
        row = await self._fetchone(
            """
            SELECT telegram_id, player_tag, is_active, created_at, last_check
            FROM building_trackers
            WHERE telegram_id = ? AND player_tag = ?
            """,
            (telegram_id, player_tag),
        )
        if row:
            return BuildingTracker(
                telegram_id=row["telegram_id"],
                player_tag=row["player_tag"],
                is_active=bool(row["is_active"]),
                created_at=_timestamp_to_iso(row["created_at"]),
                last_check=_timestamp_to_iso(row["last_check"]),
            )
        return None

    async def toggle_building_tracker_for_profile(self, telegram_id: int, player_tag: str) -> bool:
        tracker = await self.get_building_tracker_for_profile(telegram_id, player_tag)
        if tracker:
            await self._execute(
                "UPDATE building_trackers SET is_active = CASE is_active WHEN 1 THEN 0 ELSE 1 END WHERE telegram_id = ? AND player_tag = ?",
                (telegram_id, player_tag),
                commit=True,
            )
            return True
        tracker = BuildingTracker(
            telegram_id=telegram_id,
            player_tag=player_tag,
            is_active=True,
            created_at=datetime.now().isoformat(),
        )
        return await self.save_building_tracker(tracker)

    async def get_active_building_trackers(self) -> List[BuildingTracker]:
        rows = await self._fetchall(
            """
            SELECT telegram_id, player_tag, is_active, created_at, last_check
            FROM building_trackers
            WHERE is_active = 1
            """
        )
        trackers: List[BuildingTracker] = []
        for row in rows:
            trackers.append(
                BuildingTracker(
                    telegram_id=row["telegram_id"],
                    player_tag=row["player_tag"],
                    is_active=bool(row["is_active"]),
                    created_at=_timestamp_to_iso(row["created_at"]),
                    last_check=_timestamp_to_iso(row["last_check"]),
                )
            )
        return trackers

    async def save_building_snapshot(self, snapshot: BuildingSnapshot) -> bool:
        await self._execute(
            """
            INSERT INTO building_snapshots (player_tag, snapshot_time, buildings_data)
            VALUES (?, ?, ?)
            ON CONFLICT(player_tag, snapshot_time) DO UPDATE SET buildings_data=excluded.buildings_data
            """,
            (snapshot.player_tag, snapshot.snapshot_time, snapshot.buildings_data),
            commit=True,
        )
        return True

    async def get_latest_building_snapshot(self, player_tag: str) -> Optional[BuildingSnapshot]:
        row = await self._fetchone(
            """
            SELECT player_tag, snapshot_time, buildings_data
            FROM building_snapshots
            WHERE player_tag = ?
            ORDER BY snapshot_time DESC
            LIMIT 1
            """,
            (player_tag,),
        )
        if row:
            return BuildingSnapshot(
                player_tag=row["player_tag"],
                snapshot_time=row["snapshot_time"],
                buildings_data=row["buildings_data"] or "",
            )
        return None

    async def update_tracker_last_check(self, telegram_id: int, last_check: str, player_tag: str = None) -> bool:
        params: List[Any] = [_timestamp_to_iso(last_check) or datetime.now().isoformat(), telegram_id]
        if player_tag:
            query = "UPDATE building_trackers SET last_check = ? WHERE telegram_id = ? AND player_tag = ?"
            params.append(player_tag)
        else:
            query = "UPDATE building_trackers SET last_check = ? WHERE telegram_id = ?"
        await self._execute(query, params, commit=True)
        return True

    # ------------------------------------------------------------------
    # Привязанные кланы
    # ------------------------------------------------------------------
    async def get_linked_clans(self, telegram_id: int) -> List[LinkedClan]:
        rows = await self._fetchall(
            """
            SELECT id, telegram_id, clan_tag, clan_name, slot_number, created_at
            FROM linked_clans
            WHERE telegram_id = ?
            ORDER BY slot_number ASC
            """,
            (telegram_id,),
        )
        clans: List[LinkedClan] = []
        for row in rows:
            clans.append(
                LinkedClan(
                    telegram_id=row["telegram_id"],
                    clan_tag=row["clan_tag"],
                    clan_name=row["clan_name"],
                    slot_number=row["slot_number"],
                    created_at=_timestamp_to_iso(row["created_at"]),
                    id=str(row["id"]),
                )
            )
        return clans

    async def save_linked_clan(self, linked_clan: LinkedClan) -> bool:
        await self._execute(
            """
            INSERT INTO linked_clans (telegram_id, clan_tag, clan_name, slot_number, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id, slot_number) DO UPDATE SET
                clan_tag=excluded.clan_tag,
                clan_name=excluded.clan_name,
                created_at=excluded.created_at
            """,
            (
                linked_clan.telegram_id,
                linked_clan.clan_tag,
                linked_clan.clan_name,
                linked_clan.slot_number,
                _timestamp_to_iso(linked_clan.created_at) or datetime.now().isoformat(),
            ),
            commit=True,
        )
        return True

    async def delete_linked_clan(self, telegram_id: int, slot_number: int) -> bool:
        await self._execute(
            "DELETE FROM linked_clans WHERE telegram_id = ? AND slot_number = ?",
            (telegram_id, slot_number),
            commit=True,
        )
        return True

    async def get_max_linked_clans_for_user(self, telegram_id: int) -> int:
        try:
            subscription = await self.get_subscription(telegram_id)
            if subscription and subscription.is_active and not subscription.is_expired():
                if subscription.subscription_type in {"proplus", "proplus_permanent"}:
                    return 5
                if subscription.subscription_type in {"premium"}:
                    return 3
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Ошибка при получении лимита привязанных кланов: %s", exc)
        return 1

__all__ = ["DatabaseService"]
