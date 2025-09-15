"""
Сервис для работы с базой данных - аналог Java DatabaseService
"""
import aiosqlite
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from models.user import User
from models.war import WarToSave, AttackData
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
            
            await db.commit()
            logger.info("База данных успешно инициализирована")
    
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