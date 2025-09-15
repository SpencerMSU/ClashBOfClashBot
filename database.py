"""
Сервис для работы с базой данных - аналог Java DatabaseService
"""
import aiosqlite
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from models.user import User
from models.war import WarToSave, AttackData
from models.subscription import Subscription
from models.building import BuildingSnapshot, BuildingUpgrade, BuildingTracker
from config import config

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
                    telegram_id INTEGER PRIMARY KEY,
                    player_tag TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    last_check TEXT
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
        """Получение настроек отслеживания зданий пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT telegram_id, player_tag, is_active, created_at, last_check FROM building_trackers WHERE telegram_id = ?",
                (telegram_id,)
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
    
    async def update_tracker_last_check(self, telegram_id: int, last_check: str) -> bool:
        """Обновление времени последней проверки отслеживателя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE building_trackers SET last_check = ? WHERE telegram_id = ?",
                    (last_check, telegram_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении времени проверки: {e}")
            return False