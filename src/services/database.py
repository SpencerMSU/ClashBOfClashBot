"""PostgreSQL-backed database service for the ClashBot project."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    import asyncpg
except ImportError as exc:  # pragma: no cover - environment specific
    raise RuntimeError(
        "Пакет 'asyncpg' обязателен для работы с PostgreSQL. Установите его командой 'pip install asyncpg'."
    ) from exc

from config.config import config
from src.models.building import BuildingSnapshot, BuildingTracker
from src.models.linked_clan import LinkedClan
from src.models.subscription import Subscription
from src.models.user import User
from src.models.user_profile import UserProfile
from src.models.war import WarToSave

logger = logging.getLogger(__name__)


def _timestamp_to_iso(value: Optional[datetime]) -> Optional[str]:


    if isinstance(value, datetime):
        return value.isoformat()
    if value is None:
        return None
    return str(value)


class DatabaseService:
    """Database abstraction layer implemented on top of PostgreSQL."""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or getattr(config, "DATABASE_URL", "")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL не настроен в конфигурации")
        self.pool: Optional[asyncpg.pool.Pool] = None

    async def _ensure_pool(self) -> asyncpg.pool.Pool:
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(self.database_url, min_size=1, max_size=5)
            except Exception as exc:  # pragma: no cover - depends on environment
                logger.error("❌ Не удалось подключиться к PostgreSQL: %s", exc)
                raise
        return self.pool

    async def close(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def ping(self) -> bool:
        """Ping the PostgreSQL deployment to ensure the connection works."""
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            try:
                await conn.execute("SELECT 1")
                return True
            except Exception as exc:  # pragma: no cover - network failure specific
                logger.error("❌ PostgreSQL ping failed: %s", exc)
                raise

    async def init_db(self):
        """Initialise PostgreSQL tables used by the bot."""
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id BIGINT PRIMARY KEY,
                    player_tag TEXT
                )
                """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT NOT NULL,
                    player_tag TEXT NOT NULL,
                    profile_name TEXT,
                    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    UNIQUE (telegram_id, player_tag)
                )
                """
            )
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_profiles_telegram ON user_profiles(telegram_id)")

            await conn.execute(
                """
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
                    is_cwl_war BOOLEAN DEFAULT FALSE,
                    total_violations INTEGER,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
                """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS war_attacks (
                    id SERIAL PRIMARY KEY,
                    war_end_time TEXT NOT NULL REFERENCES wars(end_time) ON DELETE CASCADE,
                    attacker_tag TEXT,
                    attacker_name TEXT,
                    defender_tag TEXT,
                    stars INTEGER,
                    destruction REAL,
                    attack_order INTEGER,
                    timestamp BIGINT,
                    is_violation BOOLEAN
                )
                """
            )
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_war_attacks_war ON war_attacks(war_end_time)")

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS subscriptions (
                    telegram_id BIGINT PRIMARY KEY,
                    subscription_type TEXT,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    is_active BOOLEAN,
                    payment_id TEXT,
                    amount NUMERIC,
                    currency TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
                """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    telegram_id BIGINT PRIMARY KEY,
                    enabled_at TIMESTAMP NOT NULL
                )
                """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS building_trackers (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT NOT NULL,
                    player_tag TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    last_check TIMESTAMP,
                    UNIQUE (telegram_id, player_tag)
                )
                """
            )
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_building_trackers_active ON building_trackers(is_active)")

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS building_snapshots (
                    id SERIAL PRIMARY KEY,
                    player_tag TEXT NOT NULL,
                    snapshot_time TEXT NOT NULL,
                    buildings_data TEXT,
                    UNIQUE (player_tag, snapshot_time)
                )
                """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS player_stats_snapshots (
                    id SERIAL PRIMARY KEY,
                    player_tag TEXT NOT NULL,
                    snapshot_time TEXT NOT NULL,
                    donations INTEGER,
                    UNIQUE (player_tag, snapshot_time)
                )
                """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS linked_clans (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT NOT NULL,
                    clan_tag TEXT NOT NULL,
                    clan_name TEXT,
                    slot_number INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    UNIQUE (telegram_id, slot_number),
                    UNIQUE (telegram_id, clan_tag)
                )
                """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cwl_seasons (
                    id SERIAL PRIMARY KEY,
                    season_date TEXT UNIQUE,
                    bonus_results_json TEXT
                )
                """
            )

        logger.info("✅ PostgreSQL schema ensured")
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
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT telegram_id, COALESCE(player_tag, '') AS player_tag FROM users WHERE telegram_id=$1",
                telegram_id,
            )
        if row:
            return User(telegram_id=row["telegram_id"], player_tag=row["player_tag"] or "")
        return None

    async def save_user(self, user: User) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (telegram_id, player_tag)
                VALUES ($1, $2)
                ON CONFLICT (telegram_id) DO UPDATE SET player_tag=EXCLUDED.player_tag
                """,
                user.telegram_id,
                user.player_tag,
            )
        return True

    async def delete_user(self, telegram_id: int) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM users WHERE telegram_id=$1", telegram_id)
        return True

    async def get_all_users(self) -> List[Dict[str, Any]]:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT telegram_id, player_tag FROM users ORDER BY telegram_id ASC")
        return [{"telegram_id": row["telegram_id"], "player_tag": row["player_tag"]} for row in rows]

    # ------------------------------------------------------------------
    # User profiles
    # ------------------------------------------------------------------
    async def save_user_profile(self, profile: UserProfile) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                if profile.is_primary:
                    await conn.execute(
                        "UPDATE user_profiles SET is_primary=FALSE WHERE telegram_id=$1",
                        profile.telegram_id,
                    )
                await conn.execute(
                    """
                    INSERT INTO user_profiles (telegram_id, player_tag, profile_name, is_primary, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (telegram_id, player_tag) DO UPDATE SET
                        profile_name=EXCLUDED.profile_name,
                        is_primary=EXCLUDED.is_primary,
                        created_at=EXCLUDED.created_at
                    """,
                    profile.telegram_id,
                    profile.player_tag,
                    profile.profile_name,
                    bool(profile.is_primary),
                    _parse_iso(profile.created_at) or datetime.now(),
                )
        return True

    async def get_user_profiles(self, telegram_id: int) -> List[UserProfile]:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, telegram_id, player_tag, profile_name, is_primary, created_at
                FROM user_profiles
                WHERE telegram_id=$1
                ORDER BY is_primary DESC, created_at ASC
                """,
                telegram_id,
            )
        profiles: List[UserProfile] = []
        for row in rows:
            profile = UserProfile(
                telegram_id=row["telegram_id"],
                player_tag=row["player_tag"],
                profile_name=row["profile_name"],
                is_primary=bool(row["is_primary"]),
                created_at=_timestamp_to_iso(row["created_at"]),
                profile_id=row["id"],
            )
            profiles.append(profile)
        return profiles

    async def delete_user_profile(self, telegram_id: int, player_tag: str) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM user_profiles WHERE telegram_id=$1 AND player_tag=$2",
                telegram_id,
                player_tag,
            )
        return True

    async def get_user_profile_count(self, telegram_id: int) -> int:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT COUNT(*) AS cnt FROM user_profiles WHERE telegram_id=$1",
                telegram_id,
            )
        return int(row["cnt"]) if row else 0

    async def set_primary_profile(self, telegram_id: int, player_tag: str) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("UPDATE user_profiles SET is_primary=FALSE WHERE telegram_id=$1", telegram_id)
                result = await conn.execute(
                    "UPDATE user_profiles SET is_primary=TRUE WHERE telegram_id=$1 AND player_tag=$2",
                    telegram_id,
                    player_tag,
                )
        return result.upper().startswith("UPDATE") and "0" not in result.split()

    async def get_primary_profile(self, telegram_id: int) -> Optional[UserProfile]:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, telegram_id, player_tag, profile_name, is_primary, created_at
                FROM user_profiles
                WHERE telegram_id=$1 AND is_primary=TRUE
                ORDER BY created_at ASC
                LIMIT 1
                """,
                telegram_id,
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
    # Wars
    # ------------------------------------------------------------------
    async def save_war(self, war: WarToSave) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO wars (
                        end_time, opponent_name, team_size, clan_stars, opponent_stars,
                        clan_destruction, opponent_destruction, clan_attacks_used, result,
                        is_cwl_war, total_violations, created_at, updated_at
                    )
                    VALUES (
                        $1, $2, $3, $4, $5,
                        $6, $7, $8, $9,
                        $10, $11, NOW(), NOW()
                    )
                    ON CONFLICT (end_time) DO UPDATE SET
                        opponent_name=EXCLUDED.opponent_name,
                        team_size=EXCLUDED.team_size,
                        clan_stars=EXCLUDED.clan_stars,
                        opponent_stars=EXCLUDED.opponent_stars,
                        clan_destruction=EXCLUDED.clan_destruction,
                        opponent_destruction=EXCLUDED.opponent_destruction,
                        clan_attacks_used=EXCLUDED.clan_attacks_used,
                        result=EXCLUDED.result,
                        is_cwl_war=EXCLUDED.is_cwl_war,
                        total_violations=EXCLUDED.total_violations,
                        updated_at=NOW()
                    """,
                    war.end_time,
                    war.opponent_name,
                    war.team_size,
                    war.clan_stars,
                    war.opponent_stars,
                    war.clan_destruction,
                    war.opponent_destruction,
                    war.clan_attacks_used,
                    war.result,
                    bool(war.is_cwl_war),
                    war.total_violations,
                )

                await conn.execute("DELETE FROM war_attacks WHERE war_end_time=$1", war.end_time)

                attack_order = 0
                for member_tag, attack_list in (war.attacks_by_member or {}).items():
                    for attack in attack_list:
                        attack_order += 1
                        await conn.execute(
                            """
                            INSERT INTO war_attacks (
                                war_end_time, attacker_tag, attacker_name, defender_tag,
                                stars, destruction, attack_order, timestamp, is_violation
                            )
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                            """,
                            war.end_time,
                            member_tag,
                            attack.get("attacker_name", ""),
                            attack.get("defender_tag", ""),
                            attack.get("stars", 0),
                            attack.get("destruction", 0.0),
                            attack.get("order", attack_order),
                            attack.get("timestamp", 0),
                            bool(attack.get("is_violation", False)),
                        )
        return True

    async def war_exists(self, end_time: str) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT 1 FROM wars WHERE end_time=$1", end_time)
        return row is not None

    async def get_subscribed_users(self) -> List[int]:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT telegram_id FROM notifications")
        return [row["telegram_id"] for row in rows]

    async def toggle_notifications(self, telegram_id: int) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT 1 FROM notifications WHERE telegram_id=$1", telegram_id)
            if row:
                await conn.execute("DELETE FROM notifications WHERE telegram_id=$1", telegram_id)
                return False
            await conn.execute(
                """
                INSERT INTO notifications (telegram_id, enabled_at)
                VALUES ($1, NOW())
                ON CONFLICT (telegram_id) DO UPDATE SET enabled_at=EXCLUDED.enabled_at
                """,
                telegram_id,
            )
        return True

    async def save_donation_snapshot(self, members: List[Dict], snapshot_time: str = None):
        if not members:
            return
        pool = await self._ensure_pool()
        snapshot_time = snapshot_time or datetime.now().isoformat()
        async with pool.acquire() as conn:
            async with conn.transaction():
                for member in members:
                    player_tag = member.get("tag")
                    if not player_tag:
                        continue
                    await conn.execute(
                        """
                        INSERT INTO player_stats_snapshots (player_tag, snapshot_time, donations)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (player_tag, snapshot_time) DO UPDATE SET donations=EXCLUDED.donations
                        """,
                        player_tag,
                        snapshot_time,
                        member.get("donations", 0),
                    )

    async def get_war_list(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT end_time, opponent_name, team_size, clan_stars, opponent_stars, result, is_cwl_war
                FROM wars
                ORDER BY end_time DESC
                LIMIT $1 OFFSET $2
                """,
                limit,
                offset,
            )
        wars: List[Dict[str, Any]] = []
        for row in rows:
            wars.append(
                {
                    "end_time": row["end_time"],
                    "opponent_name": row["opponent_name"],
                    "team_size": row["team_size"],
                    "clan_stars": row["clan_stars"],
                    "opponent_stars": row["opponent_stars"],
                    "result": row["result"],
                    "is_cwl_war": bool(row["is_cwl_war"]),
                }
            )
        return wars

    async def get_cwl_bonus_data(self, year_month: str) -> List[Dict]:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT bonus_results_json FROM cwl_seasons WHERE season_date LIKE $1 || '%' LIMIT 1",
                year_month,
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
                import json

                parsed = json.loads(bonus_data)
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                logger.error("Ошибка декодирования бонусов CWL за %s", year_month)
        return []

    async def get_cwl_season_donation_stats(self, season_start: str, season_end: str) -> Dict[str, int]:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT player_tag, snapshot_time, donations
                FROM player_stats_snapshots
                WHERE snapshot_time BETWEEN $1 AND $2
                ORDER BY player_tag ASC, snapshot_time ASC
                """,
                season_start,
                season_end,
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
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT w.end_time, w.is_cwl_war, a.attacker_tag
                FROM wars w
                LEFT JOIN war_attacks a ON a.war_end_time = w.end_time
                WHERE w.end_time BETWEEN $1 AND $2
                ORDER BY w.end_time ASC, a.attack_order ASC
                """,
                season_start,
                season_end,
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
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            war_row = await conn.fetchrow(
                """
                SELECT end_time, opponent_name, team_size, clan_stars, opponent_stars,
                       clan_destruction, opponent_destruction, clan_attacks_used, result,
                       is_cwl_war, total_violations, created_at, updated_at
                FROM wars WHERE end_time=$1
                """,
                end_time,
            )
            if not war_row:
                return None
            attack_rows = await conn.fetch(
                """
                SELECT attacker_tag, attacker_name, defender_tag, stars, destruction,
                       attack_order, timestamp, is_violation
                FROM war_attacks
                WHERE war_end_time=$1
                ORDER BY attack_order ASC
                """,
                end_time,
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
    # Subscriptions
    # ------------------------------------------------------------------
    async def save_subscription(self, subscription: Subscription) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO subscriptions (
                    telegram_id, subscription_type, start_date, end_date,
                    is_active, payment_id, amount, currency, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
                ON CONFLICT (telegram_id) DO UPDATE SET
                    subscription_type=EXCLUDED.subscription_type,
                    start_date=EXCLUDED.start_date,
                    end_date=EXCLUDED.end_date,
                    is_active=EXCLUDED.is_active,
                    payment_id=EXCLUDED.payment_id,
                    amount=EXCLUDED.amount,
                    currency=EXCLUDED.currency,
                    updated_at=NOW()
                """,
                subscription.telegram_id,
                subscription.subscription_type,
                subscription.start_date,
                subscription.end_date,
                bool(subscription.is_active),
                subscription.payment_id,
                subscription.amount,
                subscription.currency or "RUB",
            )
        return True

    async def get_subscription(self, telegram_id: int) -> Optional[Subscription]:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT telegram_id, subscription_type, start_date, end_date, is_active,
                       payment_id, amount, currency
                FROM subscriptions WHERE telegram_id=$1
                """,
                telegram_id,
            )
        if not row:
            return None
        return Subscription(
            telegram_id=row["telegram_id"],
            subscription_type=row["subscription_type"] or "",
            start_date=row["start_date"] or datetime.now(),
            end_date=row["end_date"] or datetime.now(),
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
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE subscriptions SET is_active=FALSE, updated_at=NOW() WHERE telegram_id=$1",
                telegram_id,
            )
        return True

    async def get_expired_subscriptions(self) -> List[Subscription]:
        pool = await self._ensure_pool()
        now = datetime.now()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM subscriptions WHERE is_active=TRUE AND end_date < $1",
                now,
            )
        results: List[Subscription] = []
        for row in rows:
            results.append(
                Subscription(
                    telegram_id=row["telegram_id"],
                    subscription_type=row["subscription_type"] or "",
                    start_date=row["start_date"] or now,
                    end_date=row["end_date"] or now,
                    is_active=True,
                    payment_id=row["payment_id"],
                    amount=float(row["amount"]) if row["amount"] is not None else None,
                    currency=row["currency"] or "RUB",
                )
            )
        return results

    async def is_notifications_enabled(self, telegram_id: int) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT 1 FROM notifications WHERE telegram_id=$1", telegram_id)
        return row is not None

    async def enable_notifications(self, telegram_id: int) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO notifications (telegram_id, enabled_at)
                VALUES ($1, NOW())
                ON CONFLICT (telegram_id) DO UPDATE SET enabled_at=EXCLUDED.enabled_at
                """,
                telegram_id,
            )
        return True

    async def disable_notifications(self, telegram_id: int) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM notifications WHERE telegram_id=$1", telegram_id)
        return True

    async def get_notification_users(self) -> List[int]:
        return await self.get_subscribed_users()

    # ------------------------------------------------------------------
    # Building tracking
    # ------------------------------------------------------------------
    async def save_building_tracker(self, tracker: BuildingTracker) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO building_trackers (
                    telegram_id, player_tag, is_active, created_at, last_check
                )
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (telegram_id, player_tag) DO UPDATE SET
                    is_active=EXCLUDED.is_active,
                    created_at=EXCLUDED.created_at,
                    last_check=EXCLUDED.last_check
                """,
                tracker.telegram_id,
                tracker.player_tag,
                bool(tracker.is_active),
                _parse_iso(tracker.created_at) or datetime.now(),
                _parse_iso(tracker.last_check),
            )
        return True

    async def get_building_tracker(self, telegram_id: int) -> Optional[BuildingTracker]:
        trackers = await self.get_user_building_trackers(telegram_id)
        return trackers[0] if trackers else None

    async def get_user_building_trackers(self, telegram_id: int) -> List[BuildingTracker]:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT telegram_id, player_tag, is_active, created_at, last_check FROM building_trackers WHERE telegram_id=$1",
                telegram_id,
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
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT telegram_id, player_tag, is_active, created_at, last_check
                FROM building_trackers
                WHERE telegram_id=$1 AND player_tag=$2
                """,
                telegram_id,
                player_tag,
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
            pool = await self._ensure_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE building_trackers SET is_active=NOT is_active WHERE telegram_id=$1 AND player_tag=$2",
                    telegram_id,
                    player_tag,
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
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT telegram_id, player_tag, is_active, created_at, last_check FROM building_trackers WHERE is_active=TRUE"
            )
        trackers: List[BuildingTracker] = []
        for row in rows:
            trackers.append(
                BuildingTracker(
                    telegram_id=row["telegram_id"],
                    player_tag=row["player_tag"],
                    is_active=True,
                    created_at=_timestamp_to_iso(row["created_at"]),
                    last_check=_timestamp_to_iso(row["last_check"]),
                )
            )
        return trackers

    async def save_building_snapshot(self, snapshot: BuildingSnapshot) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO building_snapshots (player_tag, snapshot_time, buildings_data)
                VALUES ($1, $2, $3)
                ON CONFLICT (player_tag, snapshot_time) DO UPDATE SET buildings_data=EXCLUDED.buildings_data
                """,
                snapshot.player_tag,
                snapshot.snapshot_time,
                snapshot.buildings_data,
            )
        return True

    async def get_latest_building_snapshot(self, player_tag: str) -> Optional[BuildingSnapshot]:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT player_tag, snapshot_time, buildings_data
                FROM building_snapshots
                WHERE player_tag=$1
                ORDER BY snapshot_time DESC
                LIMIT 1
                """,
                player_tag,
            )
        if row:
            return BuildingSnapshot(
                player_tag=row["player_tag"],
                snapshot_time=row["snapshot_time"],
                buildings_data=row["buildings_data"] or "",
            )
        return None

    async def update_tracker_last_check(self, telegram_id: int, last_check: str, player_tag: str = None) -> bool:
        pool = await self._ensure_pool()
        params: List[Any] = [_parse_iso(last_check) or datetime.now(), telegram_id]
        if player_tag:
            query = "UPDATE building_trackers SET last_check=$1 WHERE telegram_id=$2 AND player_tag=$3"
            params.append(player_tag)
        else:
            query = "UPDATE building_trackers SET last_check=$1 WHERE telegram_id=$2"
        async with pool.acquire() as conn:
            await conn.execute(query, *params)
        return True

    # ------------------------------------------------------------------
    # Linked clans
    # ------------------------------------------------------------------
    async def get_linked_clans(self, telegram_id: int) -> List[LinkedClan]:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, telegram_id, clan_tag, clan_name, slot_number, created_at
                FROM linked_clans
                WHERE telegram_id=$1
                ORDER BY slot_number ASC
                """,
                telegram_id,
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
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO linked_clans (telegram_id, clan_tag, clan_name, slot_number, created_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (telegram_id, slot_number) DO UPDATE SET
                    clan_tag=EXCLUDED.clan_tag,
                    clan_name=EXCLUDED.clan_name,
                    created_at=EXCLUDED.created_at
                """,
                linked_clan.telegram_id,
                linked_clan.clan_tag,
                linked_clan.clan_name,
                linked_clan.slot_number,
                _parse_iso(linked_clan.created_at) or datetime.now(),
            )
        return True

    async def delete_linked_clan(self, telegram_id: int, slot_number: int) -> bool:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM linked_clans WHERE telegram_id=$1 AND slot_number=$2",
                telegram_id,
                slot_number,
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
