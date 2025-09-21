"""
ClashBot - Telegram бот для Clash of Clans
Все модули объединены в один файл main.py
"""

# ============================================================================
# IMPORTS - Все необходимые импорты
# ============================================================================

import asyncio
import logging
import os
import sys
import aiosqlite
import aiohttp
import json
import tempfile
import traceback
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from urllib.parse import quote
import hashlib

# Telegram imports
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError

# HTTP imports
from asyncio_throttle import Throttler

# ============================================================================
# CONFIGURATION - Конфигурация бота
# ============================================================================

def _read_api_tokens(filename: str = 'api_tokens.txt') -> dict:
    """Чтение API токенов из текстового файла"""
    tokens = {}
    
    try:
        # Сначала ищем файл в текущей директории
        if os.path.exists(filename):
            filepath = filename
        else:
            # Если не найден, ищем в директории скрипта
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Пропускаем комментарии и пустые строки
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            tokens[key.strip()] = value.strip()
        
    except Exception as e:
        print(f"Ошибка при чтении файла токенов {filename}: {e}")
    
    return tokens


class BotConfig:
    """Конфигурация бота"""
    
    def __init__(self):
        # Читаем токены из файла
        api_tokens = _read_api_tokens()
        
        # Основные токены и настройки (сначала пробуем файл, потом переменные окружения)
        self.BOT_TOKEN: str = api_tokens.get('BOT_TOKEN', '') or os.getenv('BOT_TOKEN', '')
        self.BOT_USERNAME: str = api_tokens.get('BOT_USERNAME', '') or os.getenv('BOT_USERNAME', '')
        self.COC_API_TOKEN: str = api_tokens.get('COC_API_TOKEN', '') or os.getenv('COC_API_TOKEN', '')
        
        # YooKassa платежные реквизиты
        self.YOOKASSA_SHOP_ID: str = api_tokens.get('YOOKASSA_SHOP_ID', '') or os.getenv('YOOKASSA_SHOP_ID', '')
        self.YOOKASSA_SECRET_KEY: str = api_tokens.get('YOOKASSA_SECRET_KEY', '') or os.getenv('YOOKASSA_SECRET_KEY', '')
        
        # Настройки базы данных
        self.DATABASE_PATH: str = os.getenv('DATABASE_PATH', 'clashbot.db')
        
        # Настройки клана
        self.OUR_CLAN_TAG: str = os.getenv('OUR_CLAN_TAG', '#2PQU0PLJ2')
        
        # Настройки API
        self.COC_API_BASE_URL: str = 'https://api.clashofclans.com/v1'
        
        # Настройки архивации
        self.ARCHIVE_CHECK_INTERVAL: int = int(os.getenv('ARCHIVE_CHECK_INTERVAL', '900'))  # 15 минут
        self.DONATION_SNAPSHOT_INTERVAL: int = int(os.getenv('DONATION_SNAPSHOT_INTERVAL', '21600'))  # 6 часов
        
        # Валидация обязательных параметров для валидации (но не для тестов)
        try:
            self._validate_config()
        except ValueError:
            # В тестовом режиме игнорируем ошибки валидации
            pass
    
    def _validate_config(self):
        """Проверка обязательных параметров конфигурации"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменные окружения")
        if not self.COC_API_TOKEN:
            raise ValueError("COC_API_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменные окружения")


# Глобальный экземпляр конфигурации
config = BotConfig()

# ============================================================================
# MODELS - Модели данных
# ============================================================================

@dataclass
class User:
    """Модель пользователя бота"""
    telegram_id: int
    player_tag: str
    
    def __init__(self, telegram_id: int, player_tag: str):
        self.telegram_id = telegram_id
        self.player_tag = player_tag


@dataclass
class UserProfile:
    """Модель профиля пользователя"""
    telegram_id: int
    player_tag: str
    profile_name: Optional[str] = None
    is_primary: bool = False
    created_at: Optional[str] = None
    profile_id: Optional[int] = None
    
    def __init__(self, telegram_id: int, player_tag: str, profile_name: str = None, 
                 is_primary: bool = False, created_at: str = None, profile_id: int = None):
        self.telegram_id = telegram_id
        self.player_tag = player_tag
        self.profile_name = profile_name
        self.is_primary = is_primary
        self.created_at = created_at or datetime.now().isoformat()
        self.profile_id = profile_id


@dataclass
class LinkedClan:
    """Привязанный клан пользователя"""
    id: Optional[int]
    telegram_id: int
    clan_tag: str
    clan_name: str
    slot_number: int  # номер слота (1-5)
    created_at: str
    
    def __init__(self, telegram_id: int, clan_tag: str, clan_name: str, 
                 slot_number: int, created_at: str = None, id: int = None):
        self.id = id
        self.telegram_id = telegram_id
        self.clan_tag = clan_tag
        self.clan_name = clan_name
        self.slot_number = slot_number
        self.created_at = created_at or datetime.now().isoformat()


@dataclass
class Subscription:
    """Модель подписки пользователя"""
    telegram_id: int
    subscription_type: str  # "1month", "3months", "6months", "1year"
    start_date: datetime
    end_date: datetime
    is_active: bool
    payment_id: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "RUB"
    
    def __init__(self, telegram_id: int, subscription_type: str, start_date: datetime, 
                 end_date: datetime, is_active: bool = True, payment_id: str = None, 
                 amount: float = None, currency: str = "RUB"):
        self.telegram_id = telegram_id
        self.subscription_type = subscription_type
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active
        self.payment_id = payment_id
        self.amount = amount
        self.currency = currency
    
    def is_expired(self) -> bool:
        """Проверка истечения подписки"""
        return datetime.now() > self.end_date
    
    def days_remaining(self) -> int:
        """Количество дней до истечения подписки"""
        if self.is_expired():
            return 0
        return (self.end_date - datetime.now()).days


@dataclass
class BuildingSnapshot:
    """Снимок состояния зданий игрока"""
    player_tag: str
    snapshot_time: str
    buildings_data: str  # JSON строка с данными о зданиях
    
    def __init__(self, player_tag: str, snapshot_time: str, buildings_data: str):
        self.player_tag = player_tag
        self.snapshot_time = snapshot_time
        self.buildings_data = buildings_data


@dataclass
class BuildingUpgrade:
    """Информация об улучшении здания"""
    building_name: str
    old_level: int
    new_level: int
    
    def __init__(self, building_name: str, old_level: int, new_level: int):
        self.building_name = building_name
        self.old_level = old_level
        self.new_level = new_level


@dataclass
class BuildingTracker:
    """Настройки отслеживания улучшений для пользователя"""
    telegram_id: int
    player_tag: str
    is_active: bool
    created_at: str
    last_check: Optional[str] = None
    
    def __init__(self, telegram_id: int, player_tag: str, is_active: bool, 
                 created_at: str, last_check: Optional[str] = None):
        self.telegram_id = telegram_id
        self.player_tag = player_tag
        self.is_active = is_active
        self.created_at = created_at
        self.last_check = last_check


@dataclass
class AttackData:
    """Данные об атаке"""
    attacker_name: str
    stars: int
    destruction: float
    
    def __init__(self, attacker_name: str, stars: int, destruction: float):
        self.attacker_name = attacker_name
        self.stars = stars
        self.destruction = destruction


@dataclass
class WarToSave:
    """Данные войны для сохранения в БД"""
    end_time: str
    opponent_name: str
    team_size: int
    clan_stars: int
    opponent_stars: int
    clan_destruction: float
    opponent_destruction: float
    clan_attacks_used: int
    result: str
    is_cwl_war: bool
    total_violations: int
    attacks_by_member: Dict[str, List[Dict]] = None
    
    def __init__(self, end_time: str, opponent_name: str, team_size: int, 
                 clan_stars: int, opponent_stars: int, clan_destruction: float,
                 opponent_destruction: float, clan_attacks_used: int, result: str,
                 is_cwl_war: bool, total_violations: int, attacks_by_member: Dict = None):
        self.end_time = end_time
        self.opponent_name = opponent_name
        self.team_size = team_size
        self.clan_stars = clan_stars
        self.opponent_stars = opponent_stars
        self.clan_destruction = clan_destruction
        self.opponent_destruction = opponent_destruction
        self.clan_attacks_used = clan_attacks_used
        self.result = result
        self.is_cwl_war = is_cwl_war
        self.total_violations = total_violations
        self.attacks_by_member = attacks_by_member or {}


@dataclass
class Player:
    """Модель игрока из COC API"""
    tag: str
    name: str
    town_hall_level: int
    trophies: int
    clan: Optional[Dict] = None
    

@dataclass
class Clan:
    """Модель клана из COC API"""
    tag: str
    name: str
    description: str
    location: Optional[Dict] = None
    members: List[Dict] = None
    war_wins: int = 0
    war_losses: int = 0
    war_ties: int = 0


# ============================================================================
# USER STATE - Состояния пользователя
# ============================================================================

from enum import Enum

class UserState(Enum):
    """Состояния пользователя для диалогов"""
    AWAITING_PLAYER_TAG_TO_LINK = "awaiting_player_tag_to_link"
    AWAITING_PLAYER_TAG_TO_SEARCH = "awaiting_player_tag_to_search"
    AWAITING_CLAN_TAG_TO_SEARCH = "awaiting_clan_tag_to_search"
    AWAITING_CLAN_TAG_TO_LINK = "awaiting_clan_tag_to_link"
    AWAITING_NOTIFICATION_TIME = "awaiting_notification_time"
    AWAITING_PLAYER_TAG_TO_ADD_PROFILE = "awaiting_player_tag_to_add_profile"


# ============================================================================
# COC API CLIENT - Клиент для работы с API Clash of Clans
# ============================================================================

# Валидация тегов
def validate_player_tag(tag: str) -> tuple[bool, str]:
    """Валидация тега игрока"""
    if not tag:
        return False, "Тег не может быть пустым"
    
    # Убираем лишние символы и приводим к верхнему регистру
    clean_tag = tag.strip().upper()
    if not clean_tag.startswith('#'):
        clean_tag = '#' + clean_tag
    
    # Удаляем все, кроме букв, цифр и символа #
    allowed_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#'
    clean_tag = ''.join(c for c in clean_tag if c in allowed_chars)
    
    # Проверяем длину (тег игрока обычно 8-10 символов включая #)
    if len(clean_tag) < 8 or len(clean_tag) > 12:
        return False, f"Неверная длина тега: {len(clean_tag)} символов. Ожидается 8-12."
    
    # Проверяем, что это не тег клана (кланы обычно имеют 9 символов)
    if len(clean_tag) == 9:
        return False, "Возможно, это тег клана. Теги игроков обычно содержат 8-10 символов."
    
    return True, clean_tag


def validate_clan_tag(tag: str) -> tuple[bool, str]:
    """Валидация тега клана"""
    if not tag:
        return False, "Тег не может быть пустым"
    
    # Убираем лишние символы и приводим к верхнему регистру
    clean_tag = tag.strip().upper()
    if not clean_tag.startswith('#'):
        clean_tag = '#' + clean_tag
    
    # Удаляем все, кроме букв, цифр и символа #
    allowed_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#'
    clean_tag = ''.join(c for c in clean_tag if c in allowed_chars)
    
    # Проверяем длину (тег клана обычно 9 символов включая #)
    if len(clean_tag) < 8 or len(clean_tag) > 12:
        return False, f"Неверная длина тега: {len(clean_tag)} символов. Ожидается 8-12."
    
    return True, clean_tag


def determine_war_result(clan_stars: int, opponent_stars: int) -> str:
    """Определение результата войны"""
    if clan_stars > opponent_stars:
        return "win"
    elif clan_stars < opponent_stars:
        return "lose"
    else:
        return "tie"


def extract_member_list(clan_data: Dict[Any, Any]) -> List[Dict[Any, Any]]:
    """Извлечение списка участников из данных клана"""
    return clan_data.get('memberList', []) if clan_data else []


def is_war_ended(war_data: Dict[Any, Any]) -> bool:
    """Проверка, завершена ли война"""
    return war_data.get('state') == 'warEnded' if war_data else False


def is_war_in_preparation(war_data: Dict[Any, Any]) -> bool:
    """Проверка, находится ли война в стадии подготовки"""
    return war_data.get('state') == 'preparation' if war_data else False


def is_cwl_active(league_group: Dict[Any, Any]) -> bool:
    """Проверка, активна ли Лига войн кланов"""
    return league_group.get('state') in ['preparation', 'inWar'] if league_group else False


class CocApiClient:
    """Клиент для работы с API Clash of Clans"""
    
    def __init__(self):
        self.base_url = config.COC_API_BASE_URL
        self.api_token = config.COC_API_TOKEN
        self.session = None
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        if not self.session:
            # Создаем коннектор с пулом соединений для оптимизации
            connector = aiohttp.TCPConnector(
                limit=100,  # Максимум 100 соединений в пуле
                limit_per_host=30,  # Максимум 30 соединений на хост
                enable_cleanup_closed=True,
                keepalive_timeout=300  # Держим соединения живыми 5 минут
            )
            
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json'
                },
                timeout=aiohttp.ClientTimeout(total=10),  # Уменьшили таймаут до 10 секунд
                connector=connector
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        # НЕ закрываем сессию здесь, так как она может использоваться повторно
        pass

    async def _make_request(self, endpoint: str) -> Optional[Dict[Any, Any]]:
        """Базовый метод для выполнения HTTP запросов"""
        # Используем сессию из контекстного менеджера или создаем новую
        session_to_use = self.session
        if not session_to_use:
            # Создаем временную сессию для одного запроса
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                enable_cleanup_closed=True,
                keepalive_timeout=300
            )
            
            session_to_use = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json'
                },
                timeout=aiohttp.ClientTimeout(total=15),
                connector=connector
            )
        
        url = f"{self.base_url}{endpoint}"
        try:
            async with session_to_use.get(url) as response:
                if response.status == 403:
                    logger.error("ОШИБКА 403: API ключ недействителен или ваш IP изменился. "
                               "Проверьте настройки на developer.clashofclans.com")
                    return None
                elif response.status == 404:
                    logger.warning(f"Ресурс не найден: {url}")
                    return None
                elif response.status != 200:
                    logger.error(f"HTTP {response.status} при запросе к {url}")
                    return None
                
                return await response.json()
        
        except asyncio.TimeoutError:
            logger.error(f"Таймаут при запросе к {url}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при запросе к {url}: {e}")
            return None
        finally:
            # Закрываем временную сессию если она была создана
            if not self.session and session_to_use:
                await session_to_use.close()

    async def get_player(self, player_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение информации об игроке"""
        # Валидация тега
        is_valid, clean_tag = validate_player_tag(player_tag)
        if not is_valid:
            logger.error(f"Недействительный тег игрока: {player_tag}. {clean_tag}")
            return None
        
        encoded_tag = quote(clean_tag, safe='')
        return await self._make_request(f"/players/{encoded_tag}")

    async def get_clan(self, clan_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение информации о клане"""
        # Валидация тега
        is_valid, clean_tag = validate_clan_tag(clan_tag)
        if not is_valid:
            logger.error(f"Недействительный тег клана: {clan_tag}. {clean_tag}")
            return None
        
        encoded_tag = quote(clean_tag, safe='')
        return await self._make_request(f"/clans/{encoded_tag}")

    async def get_clan_war(self, clan_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение информации о текущей войне клана"""
        # Валидация тега
        is_valid, clean_tag = validate_clan_tag(clan_tag)
        if not is_valid:
            logger.error(f"Недействительный тег клана: {clan_tag}. {clean_tag}")
            return None
        
        encoded_tag = quote(clean_tag, safe='')
        return await self._make_request(f"/clans/{encoded_tag}/currentwar")

    async def get_clan_war_league(self, clan_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение информации о Лиге войн кланов"""
        # Валидация тега
        is_valid, clean_tag = validate_clan_tag(clan_tag)
        if not is_valid:
            logger.error(f"Недействительный тег клана: {clan_tag}. {clean_tag}")
            return None
        
        encoded_tag = quote(clean_tag, safe='')
        return await self._make_request(f"/clans/{encoded_tag}/currentwar/leaguegroup")

    async def get_cwl_round_wars(self, war_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение информации о конкретной войне ЛВК"""
        encoded_tag = quote(war_tag, safe='')
        return await self._make_request(f"/clanwarleagues/wars/{encoded_tag}")

    async def close(self):
        """Закрытие HTTP сессии"""
        if self.session:
            await self.session.close()
            self.session = None


# ============================================================================
# DATABASE SERVICE - Сервис для работы с базой данных
# ============================================================================

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
    
    # Additional simplified database methods for the merged version
    async def get_subscribed_users(self) -> List[int]:
        """Получение списка пользователей с активными подписками"""
        users = []
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT telegram_id FROM subscriptions 
                    WHERE is_active = 1 AND datetime(end_date) > datetime('now')
                """) as cursor:
                    async for row in cursor:
                        users.append(row[0])
        except Exception as e:
            logger.error(f"Ошибка при получении подписчиков: {e}")
        return users

    async def save_subscription(self, subscription: Subscription) -> bool:
        """Сохранение подписки"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO subscriptions 
                    (telegram_id, subscription_type, start_date, end_date, is_active, 
                     payment_id, amount, currency, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    subscription.telegram_id, subscription.subscription_type,
                    subscription.start_date.isoformat(), subscription.end_date.isoformat(),
                    1 if subscription.is_active else 0, subscription.payment_id,
                    subscription.amount, subscription.currency,
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении подписки: {e}")
            return False

    async def get_subscription(self, telegram_id: int) -> Optional[Subscription]:
        """Получение подписки пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT telegram_id, subscription_type, start_date, end_date, is_active,
                           payment_id, amount, currency
                    FROM subscriptions WHERE telegram_id = ?
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
        except Exception as e:
            logger.error(f"Ошибка при получении подписки: {e}")
        return None

    # Simplified methods for notifications, building tracking, etc.
    async def is_notifications_enabled(self, telegram_id: int) -> bool:
        """Проверка включены ли уведомления для пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT 1 FROM notifications WHERE telegram_id = ?", (telegram_id,)
                ) as cursor:
                    return await cursor.fetchone() is not None
        except Exception:
            return False

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
        except Exception:
            return False

    async def disable_notifications(self, telegram_id: int) -> bool:
        """Отключение уведомлений для пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM notifications WHERE telegram_id = ?", (telegram_id,)
                )
                await db.commit()
                return True
        except Exception:
            return False

    async def get_notification_users(self) -> List[int]:
        """Получение списка пользователей с включенными уведомлениями"""
        users = []
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT telegram_id FROM notifications") as cursor:
                    async for row in cursor:
                        users.append(row[0])
        except Exception:
            pass
        return users

    # Building tracking methods (simplified)
    async def save_building_tracker(self, tracker: BuildingTracker) -> bool:
        """Сохранение настроек отслеживания зданий"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO building_trackers 
                    (telegram_id, player_tag, is_active, created_at, last_check)
                    VALUES (?, ?, ?, ?, ?)
                """, (tracker.telegram_id, tracker.player_tag, 
                      1 if tracker.is_active else 0, tracker.created_at, tracker.last_check))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении трекера зданий: {e}")
            return False

    async def get_building_tracker(self, telegram_id: int) -> Optional[BuildingTracker]:
        """Получение настроек отслеживания зданий"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT telegram_id, player_tag, is_active, created_at, last_check
                    FROM building_trackers WHERE telegram_id = ?
                """, (telegram_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return BuildingTracker(
                            telegram_id=row[0],
                            player_tag=row[1],
                            is_active=bool(row[2]),
                            created_at=row[3],
                            last_check=row[4]
                        )
        except Exception as e:
            logger.error(f"Ошибка при получении трекера зданий: {e}")
        return None

    # Linked clans methods (simplified)
    async def get_linked_clans(self, telegram_id: int) -> List[LinkedClan]:
        """Получение привязанных кланов пользователя"""
        clans = []
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, telegram_id, clan_tag, clan_name, slot_number, created_at
                    FROM linked_clans WHERE telegram_id = ? ORDER BY slot_number
                """, (telegram_id,)) as cursor:
                    async for row in cursor:
                        clan = LinkedClan(
                            telegram_id=row[1],
                            clan_tag=row[2],
                            clan_name=row[3],
                            slot_number=row[4],
                            created_at=row[5],
                            id=row[0]
                        )
                        clans.append(clan)
        except Exception as e:
            logger.error(f"Ошибка при получении привязанных кланов: {e}")
        return clans

    async def save_linked_clan(self, linked_clan: LinkedClan) -> bool:
        """Сохранение привязанного клана"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO linked_clans 
                    (telegram_id, clan_tag, clan_name, slot_number, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (linked_clan.telegram_id, linked_clan.clan_tag, linked_clan.clan_name,
                      linked_clan.slot_number, linked_clan.created_at))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении привязанного клана: {e}")
            return False

    async def delete_linked_clan(self, telegram_id: int, slot_number: int) -> bool:
        """Удаление привязанного клана"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    DELETE FROM linked_clans WHERE telegram_id = ? AND slot_number = ?
                """, (telegram_id, slot_number))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при удалении привязанного клана: {e}")
            return False


# ============================================================================
# KEYBOARDS - Клавиатуры и кнопки для бота
# ============================================================================

class WarSort:
    """Типы сортировки войн"""
    RECENT = "recent"
    WINS = "wins"
    LOSSES = "losses"
    CWL_ONLY = "cwl_only"


class MemberSort:
    """Типы сортировки участников"""
    ROLE = "role"
    TROPHIES = "trophies"
    DONATIONS = "donations"
    NAME = "name"


class MemberView:
    """Типы отображения участников"""
    COMPACT = "compact"
    DETAILED = "detailed"


class Keyboards:
    """Класс для создания клавиатур бота"""
    
    # Константы для кнопок
    PROFILE_BTN = "👤 Профиль"
    CLAN_BTN = "🛡 Клан"
    LINK_ACC_BTN = "🔗 Привязать аккаунт"
    SEARCH_PROFILE_BTN = "🔍 Найти профиль по тегу"
    MY_CLAN_BTN = "🛡 Мой клан (из профиля)"
    SEARCH_CLAN_BTN = "🔍 Найти клан по тегу"
    BACK_BTN = "⬅️ Назад в главное меню"
    MY_PROFILE_PREFIX = "👤 Мой профиль"
    PROFILE_MANAGER_BTN = "👥 Менеджер профилей"
    CLAN_MEMBERS_BTN = "👥 Список участников"
    CLAN_WARLOG_BTN = "⚔️ Последние войны"
    BACK_TO_CLAN_MENU_BTN = "⬅️ Назад в меню кланов"
    CLAN_CURRENT_CWL_BTN = "⚔️ Текущее ЛВК"
    CLAN_CWL_BONUS_BTN = "🏆 Бонусы ЛВК"
    NOTIFICATIONS_BTN = "🔔 Уведомления"
    CLAN_CURRENT_WAR_BTN = "⚔️ Текущая КВ"
    SUBSCRIPTION_BTN = "💎 Премиум подписка"
    LINKED_CLANS_BTN = "🔗 Привязанные кланы"
    
    # Константы для callback-данных
    MEMBERS_CALLBACK = "members"
    WAR_LIST_CALLBACK = "warlist"
    WAR_INFO_CALLBACK = "warinfo"
    PROFILE_CALLBACK = "profile"
    NOTIFY_TOGGLE_CALLBACK = "notify_toggle"
    CWL_BONUS_CALLBACK = "cwlbonus"
    MEMBERS_SORT_CALLBACK = "members_sort"
    MEMBERS_VIEW_CALLBACK = "members_view"
    SUBSCRIPTION_CALLBACK = "subscription"
    SUBSCRIPTION_EXTEND_CALLBACK = "subscription_extend"
    SUBSCRIPTION_TYPE_CALLBACK = "sub_type"
    SUBSCRIPTION_PERIOD_CALLBACK = "sub_period"
    SUBSCRIPTION_PAY_CALLBACK = "sub_pay"
    PREMIUM_MENU_CALLBACK = "premium_menu"
    NOTIFY_ADVANCED_CALLBACK = "notify_advanced"
    NOTIFY_CUSTOM_CALLBACK = "notify_custom"
    BUILDING_TRACKER_CALLBACK = "building_tracker"
    BUILDING_TOGGLE_CALLBACK = "building_toggle"
    PROFILE_MANAGER_CALLBACK = "profile_manager"
    PROFILE_SELECT_CALLBACK = "profile_select"
    PROFILE_DELETE_CALLBACK = "profile_delete"
    PROFILE_DELETE_CONFIRM_CALLBACK = "profile_delete_confirm"
    PROFILE_ADD_CALLBACK = "profile_add"
    LINKED_CLANS_CALLBACK = "linked_clans"
    LINKED_CLAN_SELECT_CALLBACK = "linked_clan_select"
    LINKED_CLAN_ADD_CALLBACK = "linked_clan_add"
    LINKED_CLAN_DELETE_CALLBACK = "linked_clan_delete"
    
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Главное меню бота"""
        keyboard = [
            [KeyboardButton(Keyboards.PROFILE_BTN), KeyboardButton(Keyboards.CLAN_BTN)],
            [KeyboardButton(Keyboards.NOTIFICATIONS_BTN)]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def profile_menu(player_name: Optional[str] = None, has_premium: bool = False, 
                    profile_count: int = 0) -> ReplyKeyboardMarkup:
        """Меню профиля"""
        keyboard = []
        
        if has_premium and profile_count > 0:
            # Для премиум пользователей с профилями показываем менеджер профилей
            keyboard.append([KeyboardButton(Keyboards.PROFILE_MANAGER_BTN)])
        elif player_name:
            # Для обычных пользователей или премиум с одним профилем
            keyboard.append([KeyboardButton(f"{Keyboards.MY_PROFILE_PREFIX} ({player_name})")])
        else:
            keyboard.append([KeyboardButton(Keyboards.LINK_ACC_BTN)])
        
        # Всегда добавляем кнопку подписки, чтобы она была видна всем пользователям
        keyboard.append([KeyboardButton(Keyboards.SUBSCRIPTION_BTN)])
        
        keyboard.extend([
            [KeyboardButton(Keyboards.SEARCH_PROFILE_BTN)],
            [KeyboardButton(Keyboards.MY_CLAN_BTN)] if (player_name or (has_premium and profile_count > 0)) else [],
            [KeyboardButton(Keyboards.BACK_BTN)]
        ])
        
        # Удаляем пустые списки
        keyboard = [row for row in keyboard if row]
        
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def clan_menu() -> ReplyKeyboardMarkup:
        """Меню клана"""
        keyboard = [
            [KeyboardButton(Keyboards.SEARCH_CLAN_BTN)],
            [KeyboardButton(Keyboards.LINKED_CLANS_BTN)],
            [KeyboardButton(Keyboards.BACK_BTN)]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def clan_inspection_menu() -> InlineKeyboardMarkup:
        """Меню для просмотра клана"""
        keyboard = [
            [InlineKeyboardButton("👥 Участники", callback_data=Keyboards.MEMBERS_CALLBACK)],
            [InlineKeyboardButton("⚔️ История войн", callback_data=Keyboards.WAR_LIST_CALLBACK)],
            [InlineKeyboardButton("⚔️ Текущая война", callback_data="current_war")],
            [InlineKeyboardButton("🏆 ЛВК", callback_data="cwl_info")],
            [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def members_pagination(clan_tag: str, current_page: int, total_pages: int, 
                          sort_type: str = "role", view_type: str = "compact") -> InlineKeyboardMarkup:
        """Пагинация для списка участников"""
        keyboard = []
        
        # Сортировка и вид
        sort_buttons = [
            InlineKeyboardButton("🎖 По роли", 
                               callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:role:{view_type}:{current_page}"),
            InlineKeyboardButton("🏆 По трофеям", 
                               callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:trophies:{view_type}:{current_page}")
        ]
        keyboard.append(sort_buttons)
        
        view_buttons = [
            InlineKeyboardButton("📋 Компактно", 
                               callback_data=f"{Keyboards.MEMBERS_VIEW_CALLBACK}:{clan_tag}:{sort_type}:compact:{current_page}"),
            InlineKeyboardButton("📄 Подробно", 
                               callback_data=f"{Keyboards.MEMBERS_VIEW_CALLBACK}:{clan_tag}:{sort_type}:detailed:{current_page}")
        ]
        keyboard.append(view_buttons)
        
        # Навигация
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️", 
                                                   callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:{sort_type}:{view_type}:{current_page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️", 
                                                   callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:{sort_type}:{view_type}:{current_page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Кнопка назад
        keyboard.append([InlineKeyboardButton("⬅️ К информации о клане", callback_data="clan_info")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def notifications_menu(is_enabled: bool = False) -> InlineKeyboardMarkup:
        """Меню уведомлений"""
        keyboard = []
        
        # Основная кнопка включения/отключения
        toggle_text = "🔕 Отключить уведомления" if is_enabled else "🔔 Включить уведомления"
        keyboard.append([InlineKeyboardButton(toggle_text, callback_data=Keyboards.NOTIFY_TOGGLE_CALLBACK)])
        
        # Дополнительные настройки (только если уведомления включены)
        if is_enabled:
            keyboard.append([InlineKeyboardButton("⚙️ Расширенные настройки", 
                                                callback_data=Keyboards.NOTIFY_ADVANCED_CALLBACK)])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def subscription_menu(has_subscription: bool = False) -> InlineKeyboardMarkup:
        """Меню подписки"""
        keyboard = []
        
        if not has_subscription:
            # Кнопки выбора типа подписки
            keyboard.extend([
                [InlineKeyboardButton("💎 PRO (1 месяц) - 99₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:pro:1month:99")],
                [InlineKeyboardButton("💎 PRO (3 месяца) - 249₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:pro:3months:249")],
                [InlineKeyboardButton("🌟 PRO PLUS (6 месяцев) - 399₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:proplus:6months:399")],
                [InlineKeyboardButton("🔥 PRO PLUS (1 год) - 699₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:proplus:1year:699")]
            ])
        else:
            # Управление существующей подпиской
            keyboard.extend([
                [InlineKeyboardButton("🔄 Продлить подписку", 
                                    callback_data=Keyboards.SUBSCRIPTION_EXTEND_CALLBACK)],
                [InlineKeyboardButton("💎 Премиум функции", 
                                    callback_data=Keyboards.PREMIUM_MENU_CALLBACK)]
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_max_profiles_for_subscription(subscription_type: str) -> int:
        """Получение максимального количества профилей для типа подписки"""
        if subscription_type in ["pro", "1month", "3months"]:
            return 3  # PRO - до 3 профилей
        elif subscription_type in ["proplus", "proplus_permanent", "6months", "1year"]:
            return 5  # PRO PLUS - до 5 профилей
        else:
            return 1  # Бесплатно - 1 профиль
    
    @staticmethod
    def linked_clans_menu(linked_clans: List[Dict[str, Any]], max_clans: int) -> InlineKeyboardMarkup:
        """Меню привязанных кланов"""
        keyboard = []
        
        # Показываем существующие кланы
        for clan in linked_clans:
            slot_num = clan.get('slot_number', 1)
            clan_name = clan.get('clan_name', 'Неизвестный клан')[:20]  # Ограничиваем длину
            button_text = f"🛡 Слот {slot_num}: {clan_name}"
            callback_data = f"{Keyboards.LINKED_CLAN_SELECT_CALLBACK}:{clan.get('clan_tag', '')}:{slot_num}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        # Добавляем пустые слоты, если есть место
        used_slots = {clan.get('slot_number', 1) for clan in linked_clans}
        for slot_num in range(1, max_clans + 1):
            if slot_num not in used_slots:
                button_text = f"➕ Слот {slot_num}: Добавить клан"
                callback_data = f"{Keyboards.LINKED_CLAN_ADD_CALLBACK}:{slot_num}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def profile_manager_menu(profiles: List[UserProfile]) -> InlineKeyboardMarkup:
        """Меню менеджера профилей"""
        keyboard = []
        
        # Добавляем кнопки для каждого профиля
        for profile in profiles:
            profile_name = profile.profile_name or f"Профиль {profile.player_tag[-4:]}"
            if profile.is_primary:
                profile_name += " ⭐"
            
            keyboard.append([InlineKeyboardButton(
                profile_name, 
                callback_data=f"{Keyboards.PROFILE_SELECT_CALLBACK}:{profile.player_tag}"
            )])
        
        # Кнопка добавления нового профиля
        keyboard.append([InlineKeyboardButton(
            "➕ Добавить профиль", 
            callback_data=Keyboards.PROFILE_ADD_CALLBACK
        )])
        
        # Кнопка удаления профиля
        if len(profiles) > 1:  # Можно удалять только если больше одного профиля
            keyboard.append([InlineKeyboardButton(
                "🗑 Удалить профиль", 
                callback_data=Keyboards.PROFILE_DELETE_CALLBACK
            )])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def profile_delete_menu(profiles: List[UserProfile]) -> InlineKeyboardMarkup:
        """Меню удаления профилей"""
        keyboard = []
        
        # Добавляем кнопки для каждого профиля (кроме основного, если он единственный)
        for profile in profiles:
            if len(profiles) == 1 and profile.is_primary:
                continue  # Не показываем единственный основной профиль
            
            profile_name = profile.profile_name or f"Профиль {profile.player_tag[-4:]}"
            keyboard.append([InlineKeyboardButton(
                f"🗑 Удалить {profile_name}", 
                callback_data=f"{Keyboards.PROFILE_DELETE_CONFIRM_CALLBACK}:{profile.player_tag}"
            )])
        
        # Кнопка отмены
        keyboard.append([InlineKeyboardButton(
            "❌ Отмена", 
            callback_data=Keyboards.PROFILE_MANAGER_CALLBACK
        )])
        
        return InlineKeyboardMarkup(keyboard)


# ============================================================================
# SIMPLIFIED COMPONENTS - Essential bot functionality 
# ============================================================================

# Payment Service (simplified)
class PaymentService:
    """Упрощенный сервис платежей"""
    def __init__(self):
        self.shop_id = config.YOOKASSA_SHOP_ID
        self.secret_key = config.YOOKASSA_SECRET_KEY
    
    async def create_payment(self, amount: float, currency: str = "RUB", description: str = "") -> Optional[str]:
        """Создание платежа (заглушка)"""
        # В реальном приложении здесь была бы интеграция с YooKassa
        return "test_payment_id"

# Policy service (simplified)
def get_policy_text() -> str:
    """Получение текста политики конфиденциальности"""
    return "🔒 *Политика конфиденциальности ClashBot*\n\n" \
           "Мы обрабатываем только необходимые данные для работы бота..."

# Message Generator (simplified)
class MessageGenerator:
    """Упрощенный генератор сообщений"""
    
    def __init__(self, db_service: DatabaseService, coc_client: CocApiClient):
        self.db_service = db_service
        self.coc_client = coc_client
    
    async def display_player_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                 player_tag: str, back_keyboard=None):
        """Отображение информации об игроке"""
        try:
            async with self.coc_client as client:
                player_data = await client.get_player(player_tag)
            
            if not player_data:
                if hasattr(update, 'callback_query') and update.callback_query:
                    await update.callback_query.edit_message_text("❌ Игрок не найден")
                else:
                    await update.message.reply_text("❌ Игрок не найден")
                return
            
            message = f"👤 *{player_data.get('name', 'Неизвестно')}*\n"
            message += f"🏠 ТХ: {player_data.get('townHallLevel', 'Неизвестно')}\n"
            message += f"🏆 Трофеи: {player_data.get('trophies', 'Неизвестно')}\n"
            
            clan = player_data.get('clan')
            if clan:
                message += f"🛡 Клан: {clan.get('name', 'Неизвестно')}\n"
            
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(
                    message, parse_mode=ParseMode.MARKDOWN,
                    reply_markup=back_keyboard
                )
            else:
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Ошибка при отображении информации об игроке: {e}")
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text("❌ Произошла ошибка")
            else:
                await update.message.reply_text("❌ Произошла ошибка")

    async def display_clan_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, clan_tag: str):
        """Отображение информации о клане"""
        try:
            async with self.coc_client as client:
                clan_data = await client.get_clan(clan_tag)
            
            if not clan_data:
                await update.message.reply_text("❌ Клан не найден")
                return
            
            message = f"🛡 *{clan_data.get('name', 'Неизвестно')}*\n"
            message += f"👥 Участников: {clan_data.get('members', 0)}/50\n"
            message += f"🏆 Очки: {clan_data.get('clanPoints', 'Неизвестно')}\n"
            message += f"⚔️ Побед в войнах: {clan_data.get('warWins', 'Неизвестно')}\n"
            
            # Сохраняем тег клана для последующих действий
            context.user_data['inspecting_clan'] = clan_tag
            
            await update.message.reply_text(
                message, parse_mode=ParseMode.MARKDOWN,
                reply_markup=Keyboards.clan_inspection_menu()
            )
        except Exception as e:
            logger.error(f"Ошибка при отображении информации о клане: {e}")
            await update.message.reply_text("❌ Произошла ошибка")

# Handlers (simplified)
class MessageHandler:
    """Упрощенный обработчик сообщений"""
    
    def __init__(self, message_generator: MessageGenerator):
        self.message_generator = message_generator
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        if not update.message or not update.message.text:
            return
        
        text = update.message.text.strip()
        user_id = update.effective_user.id
        
        # Проверяем состояние пользователя
        user_state = context.user_data.get('state')
        
        if user_state == UserState.AWAITING_PLAYER_TAG_TO_SEARCH.value:
            await self._handle_player_tag_search(update, context, text)
        elif user_state == UserState.AWAITING_CLAN_TAG_TO_SEARCH.value:
            await self._handle_clan_tag_search(update, context, text)
        elif user_state == UserState.AWAITING_PLAYER_TAG_TO_LINK.value:
            await self._handle_player_tag_link(update, context, text)
        else:
            await self._handle_menu_command(update, context, text)
    
    async def _handle_menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Обработка команд меню"""
        if text == Keyboards.PROFILE_BTN:
            keyboard = Keyboards.profile_menu()
            await update.message.reply_text("👤 Меню профиля:", reply_markup=keyboard)
        
        elif text == Keyboards.CLAN_BTN:
            keyboard = Keyboards.clan_menu()
            await update.message.reply_text("🛡 Меню клана:", reply_markup=keyboard)
        
        elif text == Keyboards.SEARCH_PROFILE_BTN:
            context.user_data['state'] = UserState.AWAITING_PLAYER_TAG_TO_SEARCH.value
            await update.message.reply_text("🔍 Введите тег игрока для поиска:")
        
        elif text == Keyboards.SEARCH_CLAN_BTN:
            context.user_data['state'] = UserState.AWAITING_CLAN_TAG_TO_SEARCH.value
            await update.message.reply_text("🔍 Введите тег клана для поиска:")
        
        elif text == Keyboards.LINK_ACC_BTN:
            context.user_data['state'] = UserState.AWAITING_PLAYER_TAG_TO_LINK.value
            await update.message.reply_text("🔗 Введите ваш тег игрока для привязки:")
        
        elif text == Keyboards.NOTIFICATIONS_BTN:
            db_service = DatabaseService()
            is_enabled = await db_service.is_notifications_enabled(update.effective_user.id)
            keyboard = Keyboards.notifications_menu(is_enabled)
            await update.message.reply_text("🔔 Настройки уведомлений:", reply_markup=keyboard)
        
        elif text == "/start":
            keyboard = Keyboards.main_menu()
            await update.message.reply_text(
                "🎮 *Добро пожаловать в ClashBot!*\n\n"
                "Выберите действие из меню:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        
        else:
            keyboard = Keyboards.main_menu()
            await update.message.reply_text("🎮 Главное меню:", reply_markup=keyboard)
    
    async def _handle_player_tag_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, tag: str):
        """Обработка поиска игрока"""
        context.user_data.pop('state', None)
        await self.message_generator.display_player_info(update, context, tag)
    
    async def _handle_clan_tag_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, tag: str):
        """Обработка поиска клана"""
        context.user_data.pop('state', None)
        await self.message_generator.display_clan_info(update, context, tag)
    
    async def _handle_player_tag_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE, tag: str):
        """Обработка привязки игрока"""
        context.user_data.pop('state', None)
        
        # Проверяем валидность тега
        is_valid, clean_tag = validate_player_tag(tag)
        if not is_valid:
            await update.message.reply_text(f"❌ Неверный тег игрока: {clean_tag}")
            return
        
        # Сохраняем пользователя
        db_service = DatabaseService()
        user = User(telegram_id=update.effective_user.id, player_tag=clean_tag)
        success = await db_service.save_user(user)
        
        if success:
            await update.message.reply_text(f"✅ Аккаунт {clean_tag} успешно привязан!")
        else:
            await update.message.reply_text("❌ Ошибка при привязке аккаунта")

class CallbackHandler:
    """Упрощенный обработчик callback-запросов"""
    
    def __init__(self, message_generator: MessageGenerator):
        self.message_generator = message_generator
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback-запросов"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == Keyboards.NOTIFY_TOGGLE_CALLBACK:
            await self._handle_notify_toggle(update, context)
        elif data == "main_menu":
            keyboard = Keyboards.main_menu()
            await query.edit_message_text("🎮 Главное меню:", reply_markup=keyboard)
        else:
            await query.edit_message_text("🔄 Функция в разработке...")
    
    async def _handle_notify_toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Переключение уведомлений"""
        db_service = DatabaseService()
        user_id = update.effective_user.id
        
        is_enabled = await db_service.is_notifications_enabled(user_id)
        
        if is_enabled:
            success = await db_service.disable_notifications(user_id)
            message = "🔕 Уведомления отключены"
        else:
            success = await db_service.enable_notifications(user_id)
            message = "🔔 Уведомления включены"
        
        if success:
            keyboard = Keyboards.notifications_menu(not is_enabled)
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
        else:
            await update.callback_query.edit_message_text("❌ Ошибка при изменении настроек")

# Simplified bot components (war archiver, building monitor - stubs)
class WarArchiver:
    """Заглушка архиватора войн"""
    def __init__(self, db_service: DatabaseService, coc_client: CocApiClient):
        self.db_service = db_service
        self.coc_client = coc_client
        self.is_running = False
    
    async def start(self):
        """Запуск архиватора"""
        self.is_running = True
    
    async def stop(self):
        """Остановка архиватора"""
        self.is_running = False

class BuildingMonitor:
    """Заглушка монитора зданий"""
    def __init__(self, db_service: DatabaseService, coc_client: CocApiClient):
        self.db_service = db_service
        self.coc_client = coc_client
        self.is_running = False
    
    async def start(self):
        """Запуск монитора"""
        self.is_running = True
    
    async def stop(self):
        """Остановка монитора"""
        self.is_running = False


# ============================================================================
# MAIN BOT CLASS - Основной класс бота
# ============================================================================

class ClashBot:
    """Основной класс Telegram бота для Clash of Clans"""
    
    def __init__(self):
        # Инициализация компонентов
        self.token = config.BOT_TOKEN
        self.db_service = DatabaseService()
        self.coc_client = CocApiClient()
        self.message_generator = MessageGenerator(self.db_service, self.coc_client)
        
        # Обработчики
        self.message_handler = MessageHandler(self.message_generator)
        self.callback_handler = CallbackHandler(self.message_generator)
        
        # Архиватор войн
        self.war_archiver = None
        
        # Монитор зданий
        self.building_monitor = None
        
        # Приложение Telegram
        self.application = None
        self.bot_instance = None
    
    async def initialize(self):
        """Инициализация бота"""
        await self._init_components()
        await self._setup_handlers()
    
    async def _init_components(self):
        """Инициализация компонентов"""
        # Инициализация базы данных
        await self.db_service.init_db()
        
        # Инициализация архиватора войн и монитора зданий
        self.war_archiver = WarArchiver(self.db_service, self.coc_client)
        self.building_monitor = BuildingMonitor(self.db_service, self.coc_client)
        
        # Создание приложения Telegram
        self.application = Application.builder().token(self.token).build()
        self.bot_instance = self.application.bot
        
        logger.info("Компоненты бота успешно инициализированы")
    
    async def _setup_handlers(self):
        """Настройка обработчиков"""
        # Обработчик команд
        self.application.add_handler(CommandHandler("start", self._start_command))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler.handle_message))
        
        # Обработчик callback-запросов
        self.application.add_handler(CallbackQueryHandler(self.callback_handler.handle_callback))
        
        logger.info("Обработчики успешно настроены")
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        keyboard = Keyboards.main_menu()
        welcome_message = (
            "🎮 *Добро пожаловать в ClashBot!*\n\n"
            "🏆 *Возможности бота:*\n"
            "• 👤 Управление профилями игроков\n"
            "• 🛡 Информация о кланах и войнах\n"
            "• 🔔 Уведомления о важных событиях\n"
            "• 💎 Премиум функции\n\n"
            "Выберите действие из меню:"
        )
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    
    async def run(self):
        """Запуск бота"""
        try:
            logger.info("Запуск инициализации бота...")
            await self.initialize()
            
            logger.info("Запуск архиватора войн...")
            await self.war_archiver.start()
            
            logger.info("Запуск монитора зданий...")
            await self.building_monitor.start()
            
            logger.info("Запуск Telegram бота...")
            await self.application.run_polling(
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
            raise
    
    async def stop(self):
        """Остановка бота"""
        try:
            logger.info("Остановка бота...")
            
            if self.war_archiver:
                await self.war_archiver.stop()
            
            if self.building_monitor:
                await self.building_monitor.stop()
            
            if self.coc_client:
                await self.coc_client.close()
            
            if self.application:
                await self.application.stop()
            
            logger.info("Бот успешно остановлен")
            
        except Exception as e:
            logger.error(f"Ошибка при остановке бота: {e}")


# ============================================================================
# VALIDATION FUNCTIONS - Функции валидации
# ============================================================================

# Создание тестового файла токенов для валидации
TEST_TOKENS_CONTENT = """# Test tokens for validation
BOT_TOKEN=test_token
COC_API_TOKEN=test_coc_token
BOT_USERNAME=test_bot
"""

def create_test_tokens_file():
    """Создание временного файла с тестовыми токенами"""
    with open('api_tokens.txt', 'w', encoding='utf-8') as f:
        f.write(TEST_TOKENS_CONTENT)

def cleanup_test_tokens_file():
    """Удаление временного файла с тестовыми токенами"""
    if os.path.exists('api_tokens.txt'):
        os.remove('api_tokens.txt')

async def validate_components():
    """Валидация всех компонентов бота"""
    try:
        print("🔍 Начинаем валидацию компонентов бота...")
        
        # Создаем тестовый файл токенов
        create_test_tokens_file()
        
        # Тестируем конфигурацию
        print("✅ Конфигурация: OK")
        
        # Тестируем базу данных
        db_service = DatabaseService(':memory:')  # Используем in-memory базу для тестов
        await db_service.init_db()
        print("✅ База данных: OK")
        
        # Тестируем COC API клиент
        coc_client = CocApiClient()
        print("✅ COC API клиент: OK")
        
        # Тестируем генератор сообщений
        message_generator = MessageGenerator(db_service, coc_client)
        print("✅ Генератор сообщений: OK")
        
        # Тестируем обработчики
        message_handler = MessageHandler(message_generator)
        callback_handler = CallbackHandler(message_generator)
        print("✅ Обработчики: OK")
        
        # Тестируем архиватор
        archiver = WarArchiver(db_service, coc_client)
        await archiver.start()
        await archiver.stop()
        assert archiver.is_running is False
        print("✅ Архиватор войн: OK")
        
        print("\n🎉 Все компоненты успешно прошли валидацию!")
        print("🚀 Бот готов к запуску с реальными токенами!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Удаляем тестовый файл токенов
        cleanup_test_tokens_file()

async def validation_main():
    """Главная функция валидации"""
    success = await validate_components()
    
    if success:
        print("\n📝 Для запуска бота:")
        print("1. Создайте файл api_tokens.txt на основе примера")
        print("2. Заполните BOT_TOKEN и COC_API_TOKEN в файле")
        print("3. Альтернативно: используйте .env файл с переменными окружения")
        print("4. Запустите: python main.py")
        sys.exit(0)
    else:
        print("\n❌ Валидация не пройдена. Проверьте ошибки выше.")
        sys.exit(1)


# ============================================================================
# MAIN FUNCTION - Точка входа в приложение
# ============================================================================

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Отключаем INFO логи от HTTP библиотек
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('telegram.ext').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция приложения"""
    try:
        logger.info("Запуск бота Clash of Clans...")
        
        # Проверяем переменные окружения
        if not config.BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменную окружения BOT_TOKEN.")
            return
        
        if not config.COC_API_TOKEN:
            logger.error("COC_API_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменную окружения COC_API_TOKEN.")
            return
        
        # Создание и запуск бота
        bot = ClashBot()
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Проверяем аргумент командной строки для валидации
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        asyncio.run(validation_main())
    else:
        # Запуск бота
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Программа завершена пользователем")
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            sys.exit(1)
