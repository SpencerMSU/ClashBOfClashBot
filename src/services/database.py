"""
Сервис для работы с базой данных - аналог Java DatabaseService
"""
import aiosqlite
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from src.models.user import User
from src.models.user_profile import UserProfile
from src.models.war import WarToSave, AttackData
from src.models.subscription import Subscription
from src.models.building import BuildingSnapshot, BuildingUpgrade, BuildingTracker
from src.models.linked_clan import LinkedClan
from config.config import config

logger = logging.getLogger(__name__)


class DatabaseService:
    """Сервис для работы с SQLite базой данных"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
    
    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Создание таблицы пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    player_tag TEXT NOT NULL UNIQUE
                )
            """)
            
            # Создание таблицы профилей для премиум пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    player_tag TEXT NOT NULL,
                    profile_name TEXT,
                    is_primary INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    UNIQUE(telegram_id, player_tag)
                )
            """)
            
            # Создание индекса для профилей
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_profiles_telegram_id 
                ON user_profiles(telegram_id)
            """)
            
            # Создание таблицы войн
            await db.execute("""
                CREATE TABLE IF NOT EXISTS wars (
                    end_time TEXT PRIMARY KEY,
                    opponent_name TEXT NOT NULL,
                    team_size INTEGER NOT NULL,
                    clan_stars INTEGER NOT NULL,
                    opponent_stars INTEGER NOT NULL,
                    clan_destruction REAL NOT NULL,
                    opponent_destruction REAL NOT NULL,
                    clan_attacks_used INTEGER NOT NULL,
                    result TEXT NOT NULL,
                    is_cwl_war INTEGER NOT NULL DEFAULT 0,
                    total_violations INTEGER DEFAULT 0
                )
            """)
            
            # Создание таблицы атак
            await db.execute("""
                CREATE TABLE IF NOT EXISTS attacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    war_id TEXT NOT NULL,
                    attacker_tag TEXT,
                    attacker_name TEXT NOT NULL,
                    defender_tag TEXT,
                    stars INTEGER NOT NULL,
                    destruction REAL NOT NULL,
                    attack_order INTEGER,
                    attack_timestamp INTEGER,
                    is_rule_violation INTEGER,
                    FOREIGN KEY (war_id) REFERENCES wars(end_time)
                )
            """)
            
            # Создание таблицы сезонов ЛВК
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cwl_seasons (
                    season_date TEXT PRIMARY KEY,
                    participants_json TEXT,
                    bonus_results_json TEXT
                )
            """)
            
            # Создание таблицы снимков статистики игроков
            await db.execute("""
                CREATE TABLE IF NOT EXISTS player_stats_snapshots (
                    snapshot_time TEXT NOT NULL,
                    player_tag TEXT NOT NULL,
                    donations INTEGER NOT NULL,
                    PRIMARY KEY (snapshot_time, player_tag)
                )
            """)
            
            # Создание таблицы уведомлений
            await db.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    telegram_id INTEGER PRIMARY KEY
                )
            """)
            
            # Создание таблицы подписок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    telegram_id INTEGER PRIMARY KEY,
                    subscription_type TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    payment_id TEXT,
                    amount REAL,
                    currency TEXT DEFAULT 'RUB',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Создание таблицы отслеживания зданий
            await db.execute("""
                CREATE TABLE IF NOT EXISTS building_trackers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    player_tag TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    last_check TEXT,
                    UNIQUE(telegram_id, player_tag)
                )
            """)
            
            # Создание таблицы снимков зданий
            await db.execute("""
                CREATE TABLE IF NOT EXISTS building_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_tag TEXT NOT NULL,
                    snapshot_time TEXT NOT NULL,
                    buildings_data TEXT NOT NULL,
                    UNIQUE(player_tag, snapshot_time)
                )
            """)
            
            # Создание таблицы привязанных кланов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS linked_clans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    clan_tag TEXT NOT NULL,
                    clan_name TEXT NOT NULL,
                    slot_number INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(telegram_id, slot_number)
                )
            """)
            
            # Создание индекса для привязанных кланов
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_linked_clans_telegram_id 
                ON linked_clans(telegram_id)
            """)
            
            # Создание таблицы запросов на сканирование войн
            await db.execute("""
                CREATE TABLE IF NOT EXISTS war_scan_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    clan_tag TEXT NOT NULL,
                    request_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    wars_added INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    UNIQUE(telegram_id, clan_tag, request_date)
                )
            """)
            
            # Создание индекса для запросов на сканирование
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_war_scan_requests_telegram_id_date 
                ON war_scan_requests(telegram_id, request_date)
            """)
            
            await db.commit()
            logger.info("База данных успешно инициализирована")
            
            # Add permanent PRO PLUS subscription for specified user
            await self._grant_permanent_proplus_subscription(5545099444)
    
    async def _grant_permanent_proplus_subscription(self, telegram_id: int):
        """Предоставление вечной PRO PLUS подписки для указанного пользователя"""
        try:
            # Create a subscription that expires in 100 years (essentially permanent)
            start_date = datetime.now()
            end_date = start_date + timedelta(days=36500)  # ~100 years
            
            permanent_subscription = Subscription(
                telegram_id=telegram_id,
                subscription_type="proplus_permanent",
                start_date=start_date,
                end_date=end_date,
                is_active=True,
                payment_id="PERMANENT_GRANT",
                amount=0.0
            )
            
            await self.save_subscription(permanent_subscription)
            logger.info(f"Предоставлена вечная PRO PLUS подписка для пользователя {telegram_id}")
        
        except Exception as e:
            logger.error(f"Ошибка при предоставлении вечной подписки: {e}")
    
    async def find_user(self, telegram_id: int) -> Optional[User]:
        """Поиск пользователя по Telegram ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT telegram_id, player_tag FROM users WHERE telegram_id = ?",
                (telegram_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return User(telegram_id=row[0], player_tag=row[1])
                return None
    
    async def save_user(self, user: User) -> bool:
        """Сохранение пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO users (telegram_id, player_tag) VALUES (?, ?)",
                    (user.telegram_id, user.player_tag)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении пользователя: {e}")
            return False
    
    async def delete_user(self, telegram_id: int) -> bool:
        """Удаление пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя: {e}")
            return False
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Получение всех пользователей для уведомлений"""
        users = []
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT telegram_id, player_tag FROM users"
                ) as cursor:
                    async for row in cursor:
                        users.append({
                            'telegram_id': row[0],
                            'player_tag': row[1]
                        })
        except Exception as e:
            logger.error(f"Ошибка при получении всех пользователей: {e}")
        return users

    # Методы управления профилями для премиум пользователей
    async def save_user_profile(self, profile: UserProfile) -> bool:
        """Сохранение профиля пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO user_profiles 
                    (telegram_id, player_tag, profile_name, is_primary, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (profile.telegram_id, profile.player_tag, profile.profile_name, 
                      profile.is_primary, profile.created_at))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении профиля: {e}")
            return False

    async def get_user_profiles(self, telegram_id: int) -> List[UserProfile]:
        """Получение всех профилей пользователя"""
        profiles = []
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, telegram_id, player_tag, profile_name, is_primary, created_at
                    FROM user_profiles WHERE telegram_id = ? ORDER BY is_primary DESC, created_at ASC
                """, (telegram_id,)) as cursor:
                    async for row in cursor:
                        profile = UserProfile(
                            telegram_id=row[1],
                            player_tag=row[2],
                            profile_name=row[3],
                            is_primary=bool(row[4]),
                            created_at=row[5]
                        )
                        profile.profile_id = row[0]
                        profiles.append(profile)
        except Exception as e:
            logger.error(f"Ошибка при получении профилей: {e}")
        return profiles

    async def delete_user_profile(self, telegram_id: int, player_tag: str) -> bool:
        """Удаление профиля пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    DELETE FROM user_profiles WHERE telegram_id = ? AND player_tag = ?
                """, (telegram_id, player_tag))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при удалении профиля: {e}")
            return False

    async def get_user_profile_count(self, telegram_id: int) -> int:
        """Получение количества профилей пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT COUNT(*) FROM user_profiles WHERE telegram_id = ?
                """, (telegram_id,)) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
        except Exception as e:
            logger.error(f"Ошибка при подсчете профилей: {e}")
            return 0

    async def set_primary_profile(self, telegram_id: int, player_tag: str) -> bool:
        """Установка основного профиля пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Сначала убираем флаг primary у всех профилей пользователя
                await db.execute("""
                    UPDATE user_profiles SET is_primary = 0 WHERE telegram_id = ?
                """, (telegram_id,))
                
                # Затем устанавливаем флаг для выбранного профиля
                await db.execute("""
                    UPDATE user_profiles SET is_primary = 1 
                    WHERE telegram_id = ? AND player_tag = ?
                """, (telegram_id, player_tag))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при установке основного профиля: {e}")
            return False

    async def get_primary_profile(self, telegram_id: int) -> Optional[UserProfile]:
        """Получение основного профиля пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, telegram_id, player_tag, profile_name, is_primary, created_at
                    FROM user_profiles WHERE telegram_id = ? AND is_primary = 1
                """, (telegram_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        profile = UserProfile(
                            telegram_id=row[1],
                            player_tag=row[2],
                            profile_name=row[3],
                            is_primary=bool(row[4]),
                            created_at=row[5]
                        )
                        profile.profile_id = row[0]
                        return profile
        except Exception as e:
            logger.error(f"Ошибка при получении основного профиля: {e}")
        return None
    
    async def save_war(self, war: WarToSave) -> bool:
        """Сохранение войны"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Сохранение основной информации о войне
                await db.execute("""
                    INSERT OR REPLACE INTO wars 
                    (end_time, opponent_name, team_size, clan_stars, opponent_stars,
                     clan_destruction, opponent_destruction, clan_attacks_used, result,
                     is_cwl_war, total_violations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    war.end_time, war.opponent_name, war.team_size,
                    war.clan_stars, war.opponent_stars, war.clan_destruction,
                    war.opponent_destruction, war.clan_attacks_used, war.result,
                    1 if war.is_cwl_war else 0, war.total_violations
                ))
                
                # Сохранение атак
                if war.attacks_by_member:
                    for member_tag, attacks in war.attacks_by_member.items():
                        for attack in attacks:
                            await db.execute("""
                                INSERT INTO attacks 
                                (war_id, attacker_tag, attacker_name, defender_tag,
                                 stars, destruction, attack_order, attack_timestamp, is_rule_violation)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                war.end_time, member_tag, attack.get('attacker_name', ''),
                                attack.get('defender_tag', ''), attack.get('stars', 0),
                                attack.get('destruction', 0.0), attack.get('order', 0),
                                attack.get('timestamp', 0), attack.get('is_violation', 0)
                            ))
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении войны: {e}")
            return False
    
    async def war_exists(self, end_time: str) -> bool:
        """Проверка существования войны"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM wars WHERE end_time = ?", (end_time,)
            ) as cursor:
                row = await cursor.fetchone()
                return row is not None
    
    async def get_subscribed_users(self) -> List[int]:
        """Получение списка пользователей с подпиской на уведомления"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT telegram_id FROM notifications") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    async def toggle_notifications(self, telegram_id: int) -> bool:
        """Переключение уведомлений для пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Проверяем, есть ли уже подписка
                async with db.execute(
                    "SELECT 1 FROM notifications WHERE telegram_id = ?", (telegram_id,)
                ) as cursor:
                    exists = await cursor.fetchone()
                
                if exists:
                    # Удаляем подписку
                    await db.execute("DELETE FROM notifications WHERE telegram_id = ?", (telegram_id,))
                    await db.commit()
                    return False  # Уведомления отключены
                else:
                    # Добавляем подписку
                    await db.execute("INSERT INTO notifications (telegram_id) VALUES (?)", (telegram_id,))
                    await db.commit()
                    return True  # Уведомления включены
        except Exception as e:
            logger.error(f"Ошибка при переключении уведомлений: {e}")
            return False
    
    async def save_donation_snapshot(self, members: List[Dict], snapshot_time: str = None):
        """Сохранение снимка донатов"""
        if not snapshot_time:
            snapshot_time = datetime.now().isoformat()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for member in members:
                    await db.execute("""
                        INSERT OR REPLACE INTO player_stats_snapshots
                        (snapshot_time, player_tag, donations)
                        VALUES (?, ?, ?)
                    """, (
                        snapshot_time,
                        member.get('tag', ''),
                        member.get('donations', 0)
                    ))
                await db.commit()
        except Exception as e:
            logger.error(f"Ошибка при сохранении снимка донатов: {e}")
    
    async def get_war_list(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Получение списка войн"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT end_time, opponent_name, team_size, clan_stars, opponent_stars,
                       result, is_cwl_war
                FROM wars 
                ORDER BY end_time DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset)) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'end_time': row[0],
                        'opponent_name': row[1],
                        'team_size': row[2],
                        'clan_stars': row[3],
                        'opponent_stars': row[4],
                        'result': row[5],
                        'is_cwl_war': bool(row[6])
                    }
                    for row in rows
                ]
    
    async def get_cwl_bonus_data(self, year_month: str) -> List[Dict]:
        """Получение данных о бонусах ЛВК за указанный месяц"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT bonus_results_json FROM cwl_seasons 
                WHERE season_date LIKE ?
            """, (f"{year_month}%",)) as cursor:
                row = await cursor.fetchone()
                
                if row and row[0]:
                    try:
                        bonus_data = json.loads(row[0])
                        return bonus_data if isinstance(bonus_data, list) else []
                    except json.JSONDecodeError:
                        logger.error(f"Ошибка декодирования JSON бонусов ЛВК для {year_month}")
                        return []
                
                return []
    
    async def get_cwl_season_donation_stats(self, season_start: str, season_end: str) -> Dict[str, int]:
        """Получение статистики донатов игроков за сезон ЛВК"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get snapshots at the start and end of the season
            async with db.execute("""
                SELECT player_tag, donations, snapshot_time
                FROM player_stats_snapshots
                WHERE snapshot_time >= ? AND snapshot_time <= ?
                ORDER BY player_tag, snapshot_time
            """, (season_start, season_end)) as cursor:
                rows = await cursor.fetchall()
            
            # Calculate donation difference for each player
            player_donations = {}
            player_snapshots = {}
            
            for row in rows:
                player_tag = row[0]
                donations = row[1]
                snapshot_time = row[2]
                
                if player_tag not in player_snapshots:
                    player_snapshots[player_tag] = []
                player_snapshots[player_tag].append((snapshot_time, donations))
            
            # Calculate difference between first and last snapshot
            for player_tag, snapshots in player_snapshots.items():
                if len(snapshots) >= 2:
                    first_donations = snapshots[0][1]
                    last_donations = snapshots[-1][1]
                    player_donations[player_tag] = max(0, last_donations - first_donations)
                elif len(snapshots) == 1:
                    player_donations[player_tag] = snapshots[0][1]
            
            return player_donations
    
    async def get_cwl_season_attack_stats(self, season_start: str, season_end: str) -> Dict[str, Dict]:
        """Получение статистики атак игроков за сезон ЛВК"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get all wars in the season
            async with db.execute("""
                SELECT end_time, is_cwl_war
                FROM wars
                WHERE end_time >= ? AND end_time <= ?
                ORDER BY end_time
            """, (season_start, season_end)) as cursor:
                war_rows = await cursor.fetchall()
            
            # Get all attacks for these wars
            player_stats = {}
            
            for war_row in war_rows:
                war_end_time = war_row[0]
                is_cwl = bool(war_row[1])
                
                async with db.execute("""
                    SELECT attacker_tag, COUNT(*) as attack_count
                    FROM attacks
                    WHERE war_id = ?
                    GROUP BY attacker_tag
                """, (war_end_time,)) as cursor:
                    attack_rows = await cursor.fetchall()
                
                for attack_row in attack_rows:
                    player_tag = attack_row[0]
                    attack_count = attack_row[1]
                    
                    if player_tag not in player_stats:
                        player_stats[player_tag] = {
                            'cwl_attacks': 0,
                            'regular_attacks': 0,
                            'cwl_wars': 0,
                            'regular_wars': 0
                        }
                    
                    if is_cwl:
                        player_stats[player_tag]['cwl_attacks'] += attack_count
                        player_stats[player_tag]['cwl_wars'] += 1
                    else:
                        player_stats[player_tag]['regular_attacks'] += attack_count
                        player_stats[player_tag]['regular_wars'] += 1
            
            return player_stats
    
    async def get_war_details(self, end_time: str) -> Optional[Dict]:
        """Получение детальной информации о войне"""
        async with aiosqlite.connect(self.db_path) as db:
            # Получаем основную информацию о войне
            async with db.execute("""
                SELECT * FROM wars WHERE end_time = ?
            """, (end_time,)) as cursor:
                war_row = await cursor.fetchone()
                if not war_row:
                    return None
            
            # Получаем атаки
            async with db.execute("""
                SELECT attacker_tag, attacker_name, defender_tag, stars, destruction,
                       attack_order, attack_timestamp, is_rule_violation
                FROM attacks WHERE war_id = ?
                ORDER BY attack_order
            """, (end_time,)) as cursor:
                attack_rows = await cursor.fetchall()
            
            war_data = {
                'end_time': war_row[0],
                'opponent_name': war_row[1],
                'team_size': war_row[2],
                'clan_stars': war_row[3],
                'opponent_stars': war_row[4],
                'clan_destruction': war_row[5],
                'opponent_destruction': war_row[6],
                'clan_attacks_used': war_row[7],
                'result': war_row[8],
                'is_cwl_war': bool(war_row[9]),
                'total_violations': war_row[10],
                'attacks': [
                    {
                        'attacker_tag': attack[0],
                        'attacker_name': attack[1],
                        'defender_tag': attack[2],
                        'stars': attack[3],
                        'destruction': attack[4],
                        'order': attack[5],
                        'timestamp': attack[6],
                        'is_violation': bool(attack[7])
                    }
                    for attack in attack_rows
                ]
            }
            
            return war_data
    
    async def save_subscription(self, subscription: Subscription) -> bool:
        """Сохранение подписки"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                now = datetime.now().isoformat()
                await db.execute("""
                    INSERT OR REPLACE INTO subscriptions 
                    (telegram_id, subscription_type, start_date, end_date, is_active, 
                     payment_id, amount, currency, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    subscription.telegram_id,
                    subscription.subscription_type,
                    subscription.start_date.isoformat(),
                    subscription.end_date.isoformat(),
                    1 if subscription.is_active else 0,
                    subscription.payment_id,
                    subscription.amount,
                    subscription.currency,
                    now,
                    now
                ))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении подписки: {e}")
            return False
    
    async def get_subscription(self, telegram_id: int) -> Optional[Subscription]:
        """Получение подписки пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT telegram_id, subscription_type, start_date, end_date, is_active,
                       payment_id, amount, currency
                FROM subscriptions 
                WHERE telegram_id = ?
            """, (telegram_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return Subscription(
                        telegram_id=row[0],
                        subscription_type=row[1],
                        start_date=datetime.fromisoformat(row[2]),
                        end_date=datetime.fromisoformat(row[3]),
                        is_active=bool(row[4]),
                        payment_id=row[5],
                        amount=row[6],
                        currency=row[7] or "RUB"
                    )
                return None
    
    async def extend_subscription(self, telegram_id: int, additional_days: int) -> bool:
        """Продление подписки"""
        try:
            subscription = await self.get_subscription(telegram_id)
            if subscription:
                # Продляем существующую подписку
                new_end_date = subscription.end_date + timedelta(days=additional_days)
                subscription.end_date = new_end_date
                subscription.is_active = True
                return await self.save_subscription(subscription)
            return False
        except Exception as e:
            logger.error(f"Ошибка при продлении подписки: {e}")
            return False
    
    async def deactivate_subscription(self, telegram_id: int) -> bool:
        """Деактивация подписки"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE subscriptions 
                    SET is_active = 0, updated_at = ?
                    WHERE telegram_id = ?
                """, (datetime.now().isoformat(), telegram_id))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при деактивации подписки: {e}")
            return False
    
    async def get_expired_subscriptions(self) -> List[Subscription]:
        """Получение истекших подписок"""
        async with aiosqlite.connect(self.db_path) as db:
            current_time = datetime.now().isoformat()
            async with db.execute("""
                SELECT telegram_id, subscription_type, start_date, end_date, is_active,
                       payment_id, amount, currency
                FROM subscriptions 
                WHERE is_active = 1 AND end_date < ?
            """, (current_time,)) as cursor:
                rows = await cursor.fetchall()
                return [
                    Subscription(
                        telegram_id=row[0],
                        subscription_type=row[1],
                        start_date=datetime.fromisoformat(row[2]),
                        end_date=datetime.fromisoformat(row[3]),
                        is_active=bool(row[4]),
                        payment_id=row[5],
                        amount=row[6],
                        currency=row[7] or "RUB"
                    )
                    for row in rows
                ]
    
    async def is_notifications_enabled(self, telegram_id: int) -> bool:
        """Проверка включены ли уведомления для пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT telegram_id FROM notifications WHERE telegram_id = ?",
                (telegram_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row is not None
    
    async def enable_notifications(self, telegram_id: int) -> bool:
        """Включение уведомлений для пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR IGNORE INTO notifications (telegram_id) VALUES (?)",
                    (telegram_id,)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при включении уведомлений: {e}")
            return False
    
    async def disable_notifications(self, telegram_id: int) -> bool:
        """Отключение уведомлений для пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM notifications WHERE telegram_id = ?",
                    (telegram_id,)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при отключении уведомлений: {e}")
            return False
    
    async def get_notification_users(self) -> List[int]:
        """Получение списка пользователей с включенными уведомлениями"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT telegram_id FROM notifications") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    # Building tracking methods
    async def save_building_tracker(self, tracker: BuildingTracker) -> bool:
        """Сохранение настроек отслеживания зданий"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO building_trackers 
                    (telegram_id, player_tag, is_active, created_at, last_check)
                    VALUES (?, ?, ?, ?, ?)
                """, (tracker.telegram_id, tracker.player_tag, int(tracker.is_active), 
                      tracker.created_at, tracker.last_check))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении настроек отслеживания: {e}")
            return False
    
    async def get_building_tracker(self, telegram_id: int) -> Optional[BuildingTracker]:
        """Получение настроек отслеживания зданий пользователя (первый найденный)"""
        trackers = await self.get_user_building_trackers(telegram_id)
        return trackers[0] if trackers else None

    async def get_user_building_trackers(self, telegram_id: int) -> List[BuildingTracker]:
        """Получение всех настроек отслеживания зданий пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT telegram_id, player_tag, is_active, created_at, last_check FROM building_trackers WHERE telegram_id = ?",
                (telegram_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [BuildingTracker(
                    telegram_id=row[0],
                    player_tag=row[1],
                    is_active=bool(row[2]),
                    created_at=row[3],
                    last_check=row[4]
                ) for row in rows]

    async def get_building_tracker_for_profile(self, telegram_id: int, player_tag: str) -> Optional[BuildingTracker]:
        """Получение настроек отслеживания для конкретного профиля"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT telegram_id, player_tag, is_active, created_at, last_check FROM building_trackers WHERE telegram_id = ? AND player_tag = ?",
                (telegram_id, player_tag)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return BuildingTracker(
                        telegram_id=row[0],
                        player_tag=row[1],
                        is_active=bool(row[2]),
                        created_at=row[3],
                        last_check=row[4]
                    )
                return None

    async def toggle_building_tracker_for_profile(self, telegram_id: int, player_tag: str) -> bool:
        """Переключение отслеживания для конкретного профиля"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Проверяем, существует ли трекер
                async with db.execute(
                    "SELECT is_active FROM building_trackers WHERE telegram_id = ? AND player_tag = ?",
                    (telegram_id, player_tag)
                ) as cursor:
                    row = await cursor.fetchone()
                    
                    if row:
                        # Переключаем состояние
                        new_state = not bool(row[0])
                        await db.execute(
                            "UPDATE building_trackers SET is_active = ? WHERE telegram_id = ? AND player_tag = ?",
                            (int(new_state), telegram_id, player_tag)
                        )
                    else:
                        # Создаем новый трекер
                        tracker = BuildingTracker(
                            telegram_id=telegram_id,
                            player_tag=player_tag,
                            is_active=True,
                            created_at=datetime.now().isoformat()
                        )
                        await db.execute("""
                            INSERT INTO building_trackers 
                            (telegram_id, player_tag, is_active, created_at, last_check)
                            VALUES (?, ?, ?, ?, ?)
                        """, (tracker.telegram_id, tracker.player_tag, int(tracker.is_active), 
                              tracker.created_at, tracker.last_check))
                    
                    await db.commit()
                    return True
        except Exception as e:
            logger.error(f"Ошибка при переключении отслеживания: {e}")
            return False
    
    async def get_active_building_trackers(self) -> List[BuildingTracker]:
        """Получение всех активных отслеживателей зданий"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT telegram_id, player_tag, is_active, created_at, last_check FROM building_trackers WHERE is_active = 1"
            ) as cursor:
                rows = await cursor.fetchall()
                return [BuildingTracker(
                    telegram_id=row[0],
                    player_tag=row[1], 
                    is_active=bool(row[2]),
                    created_at=row[3],
                    last_check=row[4]
                ) for row in rows]
    
    async def save_building_snapshot(self, snapshot: BuildingSnapshot) -> bool:
        """Сохранение снимка состояния зданий"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO building_snapshots 
                    (player_tag, snapshot_time, buildings_data)
                    VALUES (?, ?, ?)
                """, (snapshot.player_tag, snapshot.snapshot_time, snapshot.buildings_data))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении снимка зданий: {e}")
            return False
    
    async def get_latest_building_snapshot(self, player_tag: str) -> Optional[BuildingSnapshot]:
        """Получение последнего снимка зданий игрока"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT player_tag, snapshot_time, buildings_data FROM building_snapshots WHERE player_tag = ? ORDER BY snapshot_time DESC LIMIT 1",
                (player_tag,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return BuildingSnapshot(
                        player_tag=row[0],
                        snapshot_time=row[1],
                        buildings_data=row[2]
                    )
                return None
    
    async def update_tracker_last_check(self, telegram_id: int, last_check: str, player_tag: str = None) -> bool:
        """Обновление времени последней проверки отслеживателя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if player_tag:
                    # Обновляем для конкретного профиля
                    await db.execute(
                        "UPDATE building_trackers SET last_check = ? WHERE telegram_id = ? AND player_tag = ?",
                        (last_check, telegram_id, player_tag)
                    )
                else:
                    # Обновляем для всех профилей пользователя (для обратной совместимости)
                    await db.execute(
                        "UPDATE building_trackers SET last_check = ? WHERE telegram_id = ?",
                        (last_check, telegram_id)
                    )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении времени проверки: {e}")
            return False
    
    # Методы для работы с привязанными кланами
    async def get_linked_clans(self, telegram_id: int) -> List[LinkedClan]:
        """Получение всех привязанных кланов пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT id, telegram_id, clan_tag, clan_name, slot_number, created_at "
                    "FROM linked_clans WHERE telegram_id = ? ORDER BY slot_number",
                    (telegram_id,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [LinkedClan(
                        id=row[0],
                        telegram_id=row[1],
                        clan_tag=row[2],
                        clan_name=row[3],
                        slot_number=row[4],
                        created_at=row[5]
                    ) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении привязанных кланов: {e}")
            return []
    
    async def save_linked_clan(self, linked_clan: LinkedClan) -> bool:
        """Сохранение привязанного клана"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO linked_clans "
                    "(telegram_id, clan_tag, clan_name, slot_number, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (linked_clan.telegram_id, linked_clan.clan_tag, linked_clan.clan_name,
                     linked_clan.slot_number, linked_clan.created_at)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении привязанного клана: {e}")
            return False
    
    async def delete_linked_clan(self, telegram_id: int, slot_number: int) -> bool:
        """Удаление привязанного клана по номеру слота"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM linked_clans WHERE telegram_id = ? AND slot_number = ?",
                    (telegram_id, slot_number)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при удалении привязанного клана: {e}")
            return False
    
    async def get_max_linked_clans_for_user(self, telegram_id: int) -> int:
        """Получение максимального количества привязанных кланов для пользователя"""
        try:
            subscription = await self.get_subscription(telegram_id)
            if subscription and subscription.is_active and not subscription.is_expired():
                if subscription.subscription_type in ["proplus", "proplus_permanent"]:
                    return 5  # Pro Plus
                elif subscription.subscription_type in ["premium"]:
                    return 3  # Premium
            return 1  # Regular user
        except Exception as e:
            logger.error(f"Ошибка при получении лимита привязанных кланов: {e}")
            return 1
    
    # Методы для работы с запросами на сканирование войн
    async def can_request_war_scan(self, telegram_id: int) -> bool:
        """Проверка, может ли пользователь запросить сканирование войн (1 успешный запрос в день)"""
        try:
            today = datetime.now().date().isoformat()
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT COUNT(*) FROM war_scan_requests "
                    "WHERE telegram_id = ? AND request_date = ? AND status = 'success'",
                    (telegram_id, today)
                ) as cursor:
                    row = await cursor.fetchone()
                    count = row[0] if row else 0
                    return count == 0
        except Exception as e:
            logger.error(f"Ошибка при проверке лимита запросов сканирования: {e}")
            return False
    
    async def save_war_scan_request(self, telegram_id: int, clan_tag: str, status: str, wars_added: int = 0) -> bool:
        """Сохранение запроса на сканирование войн"""
        try:
            today = datetime.now().date().isoformat()
            created_at = datetime.now().isoformat()
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO war_scan_requests "
                    "(telegram_id, clan_tag, request_date, status, wars_added, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (telegram_id, clan_tag, today, status, wars_added, created_at)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении запроса сканирования: {e}")
            return False
    
    async def get_war_scan_requests_today(self, telegram_id: int) -> int:
        """Получение количества успешных запросов на сканирование за сегодня"""
        try:
            today = datetime.now().date().isoformat()
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT COUNT(*) FROM war_scan_requests "
                    "WHERE telegram_id = ? AND request_date = ? AND status = 'success'",
                    (telegram_id, today)
                ) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
        except Exception as e:
            logger.error(f"Ошибка при получении количества запросов: {e}")
            return 0