"""MongoDB-backed database service for the ClashBot project."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError as exc:  # pragma: no cover - environment specific
    raise RuntimeError(
        "The 'motor' package is required to use the MongoDB database service. "
        "Install it with 'pip install motor'."
    ) from exc

from pymongo import ASCENDING, DESCENDING, UpdateOne
from pymongo.errors import PyMongoError

from config.config import config
from src.models.building import BuildingSnapshot, BuildingTracker
from src.models.linked_clan import LinkedClan
from src.models.subscription import Subscription
from src.models.user import User
from src.models.user_profile import UserProfile
from src.models.war import WarToSave

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database abstraction layer implemented on top of MongoDB."""

    def __init__(self, mongo_uri: str = None, db_name: str = None):
        self.mongo_uri = mongo_uri or getattr(config, "MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name or getattr(config, "MONGODB_DB_NAME", "clashbot")

        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.db_name]

        # Shortcuts for frequently used collections
        self.users = self.db["users"]
        self.user_profiles = self.db["user_profiles"]
        self.wars = self.db["wars"]
        self.subscriptions = self.db["subscriptions"]
        self.notifications = self.db["notifications"]
        self.building_trackers = self.db["building_trackers"]
        self.building_snapshots = self.db["building_snapshots"]
        self.player_stats_snapshots = self.db["player_stats_snapshots"]
        self.linked_clans = self.db["linked_clans"]
        self.war_scan_requests = self.db["war_scan_requests"]
        self.cwl_seasons = self.db["cwl_seasons"]

        logger.info("🔗 DatabaseService initialised for MongoDB URI %s, database '%s'", self.mongo_uri, self.db_name)

    async def ping(self) -> bool:
        """Ping the MongoDB deployment to ensure the connection works."""
        try:
            await self.client.admin.command("ping")
            return True
        except Exception as exc:  # pragma: no cover - network failure specific
            logger.error("❌ MongoDB ping failed: %s", exc)
            raise

    async def init_db(self):
        """Initialise MongoDB collections and indexes used by the bot."""
        logger.info("🛠️ Ensuring MongoDB indexes are created")
        try:
            await self.ping()

            await self.users.create_index("telegram_id", unique=True)
            await self.users.create_index("player_tag", unique=True, sparse=True)

            await self.user_profiles.create_index([("telegram_id", ASCENDING), ("player_tag", ASCENDING)], unique=True)
            await self.user_profiles.create_index([("telegram_id", ASCENDING), ("is_primary", DESCENDING), ("created_at", ASCENDING)])

            await self.wars.create_index("end_time", unique=True)
            await self.wars.create_index("is_cwl_war")
            await self.wars.create_index("created_at")

            await self.subscriptions.create_index("telegram_id", unique=True)
            await self.subscriptions.create_index("end_date")
            await self.subscriptions.create_index("is_active")

            await self.notifications.create_index("telegram_id", unique=True)

            await self.building_trackers.create_index([("telegram_id", ASCENDING), ("player_tag", ASCENDING)], unique=True)
            await self.building_trackers.create_index("is_active")

            await self.building_snapshots.create_index([("player_tag", ASCENDING), ("snapshot_time", DESCENDING)], unique=True)

            await self.player_stats_snapshots.create_index([("player_tag", ASCENDING), ("snapshot_time", ASCENDING)])

            await self.linked_clans.create_index([("telegram_id", ASCENDING), ("slot_number", ASCENDING)], unique=True)
            await self.linked_clans.create_index([("telegram_id", ASCENDING), ("clan_tag", ASCENDING)], unique=True)

            await self.war_scan_requests.create_index("telegram_id")
            await self.war_scan_requests.create_index("request_date")
            await self.war_scan_requests.create_index("status")

            await self.cwl_seasons.create_index("season_date", unique=True)

            logger.info("✅ MongoDB collections are ready")
        except Exception as exc:
            logger.error("❌ Failed to initialise MongoDB: %s", exc)
            raise

        await self._grant_permanent_proplus_subscription(5545099444)

    async def _grant_permanent_proplus_subscription(self, telegram_id: int):
        """Ensure the specified Telegram user always has a PRO PLUS subscription."""
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
    # User management
    # ------------------------------------------------------------------
    async def find_user(self, telegram_id: int) -> Optional[User]:
        doc = await self.users.find_one({"telegram_id": telegram_id})
        if doc:
            return User(telegram_id=doc["telegram_id"], player_tag=doc.get("player_tag", ""))
        return None

    async def save_user(self, user: User) -> bool:
        try:
            await self.users.update_one(
                {"telegram_id": user.telegram_id},
                {"$set": {"telegram_id": user.telegram_id, "player_tag": user.player_tag}},
                upsert=True,
            )
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при сохранении пользователя: %s", exc)
            return False

    async def delete_user(self, telegram_id: int) -> bool:
        try:
            await self.users.delete_one({"telegram_id": telegram_id})
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при удалении пользователя: %s", exc)
            return False

    async def get_all_users(self) -> List[Dict[str, Any]]:
        users: List[Dict[str, Any]] = []
        async for doc in self.users.find({}, {"_id": 0}).sort("telegram_id", ASCENDING):
            users.append({"telegram_id": doc["telegram_id"], "player_tag": doc.get("player_tag")})
        return users

    # ------------------------------------------------------------------
    # User profiles
    # ------------------------------------------------------------------
    async def save_user_profile(self, profile: UserProfile) -> bool:
        try:
            if profile.is_primary:
                await self.user_profiles.update_many({"telegram_id": profile.telegram_id}, {"$set": {"is_primary": False}})

            await self.user_profiles.update_one(
                {"telegram_id": profile.telegram_id, "player_tag": profile.player_tag},
                {
                    "$set": {
                        "telegram_id": profile.telegram_id,
                        "player_tag": profile.player_tag,
                        "profile_name": profile.profile_name,
                        "is_primary": bool(profile.is_primary),
                        "created_at": profile.created_at,
                    }
                },
                upsert=True,
            )
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при сохранении профиля: %s", exc)
            return False

    async def get_user_profiles(self, telegram_id: int) -> List[UserProfile]:
        profiles: List[UserProfile] = []
        cursor = self.user_profiles.find({"telegram_id": telegram_id}).sort(
            [("is_primary", DESCENDING), ("created_at", ASCENDING)]
        )
        async for doc in cursor:
            profile = UserProfile(
                telegram_id=doc["telegram_id"],
                player_tag=doc["player_tag"],
                profile_name=doc.get("profile_name"),
                is_primary=bool(doc.get("is_primary", False)),
                created_at=doc.get("created_at"),
            )
            profile.profile_id = str(doc.get("_id"))
            profiles.append(profile)
        return profiles

    async def delete_user_profile(self, telegram_id: int, player_tag: str) -> bool:
        try:
            await self.user_profiles.delete_one({"telegram_id": telegram_id, "player_tag": player_tag})
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при удалении профиля: %s", exc)
            return False

    async def get_user_profile_count(self, telegram_id: int) -> int:
        return await self.user_profiles.count_documents({"telegram_id": telegram_id})

    async def set_primary_profile(self, telegram_id: int, player_tag: str) -> bool:
        try:
            await self.user_profiles.update_many({"telegram_id": telegram_id}, {"$set": {"is_primary": False}})
            result = await self.user_profiles.update_one(
                {"telegram_id": telegram_id, "player_tag": player_tag},
                {"$set": {"is_primary": True}},
            )
            return result.matched_count > 0
        except PyMongoError as exc:
            logger.error("Ошибка при установке основного профиля: %s", exc)
            return False

    async def get_primary_profile(self, telegram_id: int) -> Optional[UserProfile]:
        doc = await self.user_profiles.find_one({"telegram_id": telegram_id, "is_primary": True})
        if doc:
            profile = UserProfile(
                telegram_id=doc["telegram_id"],
                player_tag=doc["player_tag"],
                profile_name=doc.get("profile_name"),
                is_primary=True,
                created_at=doc.get("created_at"),
            )
            profile.profile_id = str(doc.get("_id"))
            return profile
        return None

    # ------------------------------------------------------------------
    # Wars
    # ------------------------------------------------------------------
    async def save_war(self, war: WarToSave) -> bool:
        attacks: List[Dict[str, Any]] = []
        for member_tag, attack_list in (war.attacks_by_member or {}).items():
            for attack in attack_list:
                attacks.append(
                    {
                        "attacker_tag": member_tag,
                        "attacker_name": attack.get("attacker_name", ""),
                        "defender_tag": attack.get("defender_tag", ""),
                        "stars": attack.get("stars", 0),
                        "destruction": attack.get("destruction", 0.0),
                        "order": attack.get("order", 0),
                        "timestamp": attack.get("timestamp", 0),
                        "is_violation": bool(attack.get("is_violation", False)),
                    }
                )
        try:
            await self.wars.update_one(
                {"end_time": war.end_time},
                {
                    "$set": {
                        "end_time": war.end_time,
                        "opponent_name": war.opponent_name,
                        "team_size": war.team_size,
                        "clan_stars": war.clan_stars,
                        "opponent_stars": war.opponent_stars,
                        "clan_destruction": war.clan_destruction,
                        "opponent_destruction": war.opponent_destruction,
                        "clan_attacks_used": war.clan_attacks_used,
                        "result": war.result,
                        "is_cwl_war": bool(war.is_cwl_war),
                        "total_violations": war.total_violations,
                        "attacks": attacks,
                        "updated_at": datetime.now(),
                    },
                    "$setOnInsert": {"created_at": datetime.now()},
                },
                upsert=True,
            )
            return True
        except PyMongoError as exc:
            logger.error("❌ Ошибка при сохранении войны %s: %s", war.end_time, exc)
            return False

    async def war_exists(self, end_time: str) -> bool:
        doc = await self.wars.find_one({"end_time": end_time}, {"_id": 1})
        return doc is not None

    async def get_subscribed_users(self) -> List[int]:
        return [doc["telegram_id"] async for doc in self.notifications.find({}, {"_id": 0, "telegram_id": 1})]

    async def toggle_notifications(self, telegram_id: int) -> bool:
        if await self.notifications.find_one({"telegram_id": telegram_id}):
            await self.notifications.delete_one({"telegram_id": telegram_id})
            return False
        await self.notifications.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"telegram_id": telegram_id, "enabled_at": datetime.now()}},
            upsert=True,
        )
        return True

    async def save_donation_snapshot(self, members: List[Dict], snapshot_time: str = None):
        snapshot_time = snapshot_time or datetime.now().isoformat()
        operations: List[UpdateOne] = []
        for member in members:
            player_tag = member.get("tag")
            if not player_tag:
                continue
            operations.append(
                UpdateOne(
                    {"player_tag": player_tag, "snapshot_time": snapshot_time},
                    {
                        "$set": {
                            "player_tag": player_tag,
                            "snapshot_time": snapshot_time,
                            "donations": member.get("donations", 0),
                        }
                    },
                    upsert=True,
                )
            )
        if operations:
            await self.player_stats_snapshots.bulk_write(operations, ordered=False)

    async def get_war_list(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        wars: List[Dict[str, Any]] = []
        cursor = self.wars.find({}, {
            "_id": 0,
            "end_time": 1,
            "opponent_name": 1,
            "team_size": 1,
            "clan_stars": 1,
            "opponent_stars": 1,
            "result": 1,
            "is_cwl_war": 1,
        }).sort("end_time", DESCENDING).skip(offset).limit(limit)
        async for doc in cursor:
            wars.append({
                "end_time": doc.get("end_time"),
                "opponent_name": doc.get("opponent_name"),
                "team_size": doc.get("team_size"),
                "clan_stars": doc.get("clan_stars"),
                "opponent_stars": doc.get("opponent_stars"),
                "result": doc.get("result"),
                "is_cwl_war": bool(doc.get("is_cwl_war", False)),
            })
        return wars

    async def get_cwl_bonus_data(self, year_month: str) -> List[Dict]:
        doc = await self.cwl_seasons.find_one({"season_date": {"$regex": f"^{year_month}"}})
        if not doc:
            return []
        bonus_data = doc.get("bonus_results_json")
        if isinstance(bonus_data, list):
            return bonus_data
        if isinstance(bonus_data, str):
            try:
                import json

                parsed = json.loads(bonus_data)
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                logger.error("Ошибка декодирования бонусов CWL за %s", year_month)
        return []

    async def get_cwl_season_donation_stats(self, season_start: str, season_end: str) -> Dict[str, int]:
        stats: Dict[str, int] = {}
        cursor = self.player_stats_snapshots.find(
            {"snapshot_time": {"$gte": season_start, "$lte": season_end}}
        ).sort([("player_tag", ASCENDING), ("snapshot_time", ASCENDING)])

        snapshots: Dict[str, List[Dict[str, Any]]] = {}
        async for doc in cursor:
            snapshots.setdefault(doc["player_tag"], []).append(doc)

        for player_tag, entries in snapshots.items():
            if len(entries) >= 2:
                stats[player_tag] = max(0, entries[-1].get("donations", 0) - entries[0].get("donations", 0))
            elif entries:
                stats[player_tag] = entries[0].get("donations", 0)
        return stats

    async def get_cwl_season_attack_stats(self, season_start: str, season_end: str) -> Dict[str, Dict]:
        player_stats: Dict[str, Dict[str, int]] = {}
        cursor = self.wars.find(
            {"end_time": {"$gte": season_start, "$lte": season_end}},
            {"end_time": 1, "is_cwl_war": 1, "attacks": 1},
        ).sort("end_time", ASCENDING)

        async for war_doc in cursor:
            is_cwl = bool(war_doc.get("is_cwl_war", False))
            per_war_counts: Dict[str, int] = {}
            for attack in war_doc.get("attacks", []):
                tag = attack.get("attacker_tag")
                if not tag:
                    continue
                per_war_counts[tag] = per_war_counts.get(tag, 0) + 1

            for tag, count in per_war_counts.items():
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
        doc = await self.wars.find_one({"end_time": end_time}, {"_id": 0})
        if not doc:
            return None
        doc.setdefault("attacks", [])
        return doc

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------
    async def save_subscription(self, subscription: Subscription) -> bool:
        try:
            now = datetime.now()
            await self.subscriptions.update_one(
                {"telegram_id": subscription.telegram_id},
                {
                    "$set": {
                        "telegram_id": subscription.telegram_id,
                        "subscription_type": subscription.subscription_type,
                        "start_date": subscription.start_date,
                        "end_date": subscription.end_date,
                        "is_active": bool(subscription.is_active),
                        "payment_id": subscription.payment_id,
                        "amount": subscription.amount,
                        "currency": subscription.currency or "RUB",
                        "updated_at": now,
                    },
                    "$setOnInsert": {"created_at": now},
                },
                upsert=True,
            )
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при сохранении подписки: %s", exc)
            return False

    async def get_subscription(self, telegram_id: int) -> Optional[Subscription]:
        doc = await self.subscriptions.find_one({"telegram_id": telegram_id})
        if not doc:
            return None
        return Subscription(
            telegram_id=doc["telegram_id"],
            subscription_type=doc.get("subscription_type", ""),
            start_date=doc.get("start_date", datetime.now()),
            end_date=doc.get("end_date", datetime.now()),
            is_active=bool(doc.get("is_active", False)),
            payment_id=doc.get("payment_id"),
            amount=doc.get("amount"),
            currency=doc.get("currency", "RUB"),
        )

    async def extend_subscription(self, telegram_id: int, additional_days: int) -> bool:
        subscription = await self.get_subscription(telegram_id)
        if not subscription:
            return False
        subscription.end_date = subscription.end_date + timedelta(days=additional_days)
        subscription.is_active = True
        return await self.save_subscription(subscription)

    async def deactivate_subscription(self, telegram_id: int) -> bool:
        try:
            await self.subscriptions.update_one(
                {"telegram_id": telegram_id},
                {"$set": {"is_active": False, "updated_at": datetime.now()}},
            )
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при деактивации подписки: %s", exc)
            return False

    async def get_expired_subscriptions(self) -> List[Subscription]:
        now = datetime.now()
        cursor = self.subscriptions.find({"is_active": True, "end_date": {"$lt": now}})
        results: List[Subscription] = []
        async for doc in cursor:
            results.append(
                Subscription(
                    telegram_id=doc["telegram_id"],
                    subscription_type=doc.get("subscription_type", ""),
                    start_date=doc.get("start_date", now),
                    end_date=doc.get("end_date", now),
                    is_active=True,
                    payment_id=doc.get("payment_id"),
                    amount=doc.get("amount"),
                    currency=doc.get("currency", "RUB"),
                )
            )
        return results

    async def is_notifications_enabled(self, telegram_id: int) -> bool:
        return await self.notifications.find_one({"telegram_id": telegram_id}) is not None

    async def enable_notifications(self, telegram_id: int) -> bool:
        await self.notifications.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"telegram_id": telegram_id, "enabled_at": datetime.now()}},
            upsert=True,
        )
        return True

    async def disable_notifications(self, telegram_id: int) -> bool:
        await self.notifications.delete_one({"telegram_id": telegram_id})
        return True

    async def get_notification_users(self) -> List[int]:
        return await self.get_subscribed_users()

    # ------------------------------------------------------------------
    # Building tracking
    # ------------------------------------------------------------------
    async def save_building_tracker(self, tracker: BuildingTracker) -> bool:
        try:
            await self.building_trackers.update_one(
                {"telegram_id": tracker.telegram_id, "player_tag": tracker.player_tag},
                {
                    "$set": {
                        "telegram_id": tracker.telegram_id,
                        "player_tag": tracker.player_tag,
                        "is_active": bool(tracker.is_active),
                        "created_at": tracker.created_at,
                        "last_check": tracker.last_check,
                    }
                },
                upsert=True,
            )
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при сохранении настроек отслеживания: %s", exc)
            return False

    async def get_building_tracker(self, telegram_id: int) -> Optional[BuildingTracker]:
        trackers = await self.get_user_building_trackers(telegram_id)
        return trackers[0] if trackers else None

    async def get_user_building_trackers(self, telegram_id: int) -> List[BuildingTracker]:
        trackers: List[BuildingTracker] = []
        cursor = self.building_trackers.find({"telegram_id": telegram_id})
        async for doc in cursor:
            trackers.append(
                BuildingTracker(
                    telegram_id=doc["telegram_id"],
                    player_tag=doc.get("player_tag", ""),
                    is_active=bool(doc.get("is_active", False)),
                    created_at=doc.get("created_at"),
                    last_check=doc.get("last_check"),
                )
            )
        return trackers

    async def get_building_tracker_for_profile(self, telegram_id: int, player_tag: str) -> Optional[BuildingTracker]:
        doc = await self.building_trackers.find_one({"telegram_id": telegram_id, "player_tag": player_tag})
        if doc:
            return BuildingTracker(
                telegram_id=doc["telegram_id"],
                player_tag=doc.get("player_tag", ""),
                is_active=bool(doc.get("is_active", False)),
                created_at=doc.get("created_at"),
                last_check=doc.get("last_check"),
            )
        return None

    async def toggle_building_tracker_for_profile(self, telegram_id: int, player_tag: str) -> bool:
        tracker = await self.get_building_tracker_for_profile(telegram_id, player_tag)
        if tracker:
            await self.building_trackers.update_one(
                {"telegram_id": telegram_id, "player_tag": player_tag},
                {"$set": {"is_active": not tracker.is_active}},
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
        trackers: List[BuildingTracker] = []
        async for doc in self.building_trackers.find({"is_active": True}):
            trackers.append(
                BuildingTracker(
                    telegram_id=doc["telegram_id"],
                    player_tag=doc.get("player_tag", ""),
                    is_active=True,
                    created_at=doc.get("created_at"),
                    last_check=doc.get("last_check"),
                )
            )
        return trackers

    async def save_building_snapshot(self, snapshot: BuildingSnapshot) -> bool:
        try:
            await self.building_snapshots.update_one(
                {"player_tag": snapshot.player_tag, "snapshot_time": snapshot.snapshot_time},
                {
                    "$set": {
                        "player_tag": snapshot.player_tag,
                        "snapshot_time": snapshot.snapshot_time,
                        "buildings_data": snapshot.buildings_data,
                    }
                },
                upsert=True,
            )
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при сохранении снимка зданий: %s", exc)
            return False

    async def get_latest_building_snapshot(self, player_tag: str) -> Optional[BuildingSnapshot]:
        doc = await self.building_snapshots.find_one(
            {"player_tag": player_tag},
            sort=[("snapshot_time", DESCENDING)],
        )
        if doc:
            return BuildingSnapshot(
                player_tag=doc.get("player_tag", ""),
                snapshot_time=doc.get("snapshot_time", ""),
                buildings_data=doc.get("buildings_data", ""),
            )
        return None

    async def update_tracker_last_check(self, telegram_id: int, last_check: str, player_tag: str = None) -> bool:
        query: Dict[str, Any] = {"telegram_id": telegram_id}
        if player_tag:
            query["player_tag"] = player_tag
        try:
            await self.building_trackers.update_many(query, {"$set": {"last_check": last_check}})
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при обновлении времени проверки: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Linked clans
    # ------------------------------------------------------------------
    async def get_linked_clans(self, telegram_id: int) -> List[LinkedClan]:
        clans: List[LinkedClan] = []
        cursor = self.linked_clans.find({"telegram_id": telegram_id}).sort("slot_number", ASCENDING)
        async for doc in cursor:
            clans.append(
                LinkedClan(
                    telegram_id=doc["telegram_id"],
                    clan_tag=doc.get("clan_tag", ""),
                    clan_name=doc.get("clan_name", ""),
                    slot_number=doc.get("slot_number", 0),
                    created_at=doc.get("created_at"),
                    id=str(doc.get("_id")),
                )
            )
        return clans

    async def save_linked_clan(self, linked_clan: LinkedClan) -> bool:
        try:
            await self.linked_clans.update_one(
                {"telegram_id": linked_clan.telegram_id, "slot_number": linked_clan.slot_number},
                {
                    "$set": {
                        "telegram_id": linked_clan.telegram_id,
                        "clan_tag": linked_clan.clan_tag,
                        "clan_name": linked_clan.clan_name,
                        "slot_number": linked_clan.slot_number,
                        "created_at": linked_clan.created_at,
                    }
                },
                upsert=True,
            )
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при сохранении привязанного клана: %s", exc)
            return False

    async def delete_linked_clan(self, telegram_id: int, slot_number: int) -> bool:
        try:
            await self.linked_clans.delete_one({"telegram_id": telegram_id, "slot_number": slot_number})
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при удалении привязанного клана: %s", exc)
            return False

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

    # ------------------------------------------------------------------
    # War scan requests
    # ------------------------------------------------------------------
    async def can_request_war_scan(self, telegram_id: int) -> bool:
        today = datetime.now().date().isoformat()
        count = await self.war_scan_requests.count_documents(
            {"telegram_id": telegram_id, "request_date": today, "status": "success"}
        )
        return count == 0

    async def save_war_scan_request(
        self,
        telegram_id: int,
        clan_tag: str,
        status: str,
        wars_added: int = 0,
        request_type: str = "manual",
    ) -> bool:
        try:
            await self.war_scan_requests.insert_one(
                {
                    "telegram_id": telegram_id,
                    "clan_tag": clan_tag,
                    "request_type": request_type,
                    "request_date": datetime.now().date().isoformat(),
                    "status": status,
                    "wars_added": wars_added,
                    "created_at": datetime.now(),
                }
            )
            return True
        except PyMongoError as exc:
            logger.error("Ошибка при сохранении запроса сканирования: %s", exc)
            return False

    async def get_war_scan_requests_today(self, telegram_id: int) -> int:
        today = datetime.now().date().isoformat()
        return await self.war_scan_requests.count_documents(
            {"telegram_id": telegram_id, "request_date": today, "status": "success"}
        )


__all__ = ["DatabaseService"]
