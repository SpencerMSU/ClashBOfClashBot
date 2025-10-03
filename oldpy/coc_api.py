"""
Клиент для работы с API Clash of Clans - аналог Java CocApiClient

Этот модуль предоставляет асинхронный клиент для работы с официальным API Clash of Clans.
Включает валидацию тегов для предотвращения ошибок типа "использование тега клана как тега игрока".

Основные функции:
- CocApiClient: Асинхронный клиент для API запросов
- Валидация тегов: validate_player_tag(), validate_clan_tag()
- Определение типа тега: is_player_tag(), is_clan_tag()
- Форматирование тегов: format_player_tag(), format_clan_tag()

Важно: Теги кланов обычно состоят из 9 символов, теги игроков - из 8-10 символов.
Система автоматически определяет тип тега и предотвращает неправильное использование.
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import quote
import json

from config import config

logger = logging.getLogger(__name__)


class CocApiClient:
    """Клиент для работы с API Clash of Clans"""
    
    def __init__(self):
        self.base_url = config.COC_API_BASE_URL
        self.api_token = config.COC_API_TOKEN
        self.session = None
        # Трекер ошибок API
        self.api_errors = []
    
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

    async def _make_request(self, endpoint: str, track_errors: bool = True) -> Optional[Dict[Any, Any]]:
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
                    if track_errors:
                        self._track_error(endpoint, 403, "API key invalid or IP changed")
                    return None
                elif response.status == 404:
                    logger.warning(f"Ресурс не найден: {url}")
                    if track_errors:
                        self._track_error(endpoint, 404, "Resource not found")
                    return None
                elif response.status != 200:
                    logger.error(f"HTTP {response.status} при запросе к {url}")
                    if track_errors:
                        self._track_error(endpoint, response.status, f"HTTP error {response.status}")
                    return None
                
                return await response.json()
        
        except asyncio.TimeoutError:
            logger.error(f"Таймаут при запросе к {url}")
            if track_errors:
                self._track_error(endpoint, 0, "Timeout error")
            return None
        except Exception as e:
            logger.error(f"Ошибка при запросе к {url}: {e}")
            if track_errors:
                self._track_error(endpoint, 0, str(e))
            return None
        finally:
            # Закрываем сессию только если она была создана временно
            if not self.session and session_to_use:
                await session_to_use.close()
    
    def _track_error(self, endpoint: str, status_code: int, error_message: str):
        """Отслеживание ошибок API"""
        from datetime import datetime
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'status_code': status_code,
            'error_message': error_message
        }
        self.api_errors.append(error_entry)
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """Получение списка всех ошибок"""
        return self.api_errors
    
    def clear_errors(self):
        """Очистка списка ошибок"""
        self.api_errors = []

    async def get_player_info(self, player_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение информации об игроке"""
        # Валидация тега игрока
        is_valid, validation_message = validate_player_tag(player_tag)
        if not is_valid:
            logger.error(f"Невалидный тег игрока '{player_tag}': {validation_message}")
            return None
        
        # Предупреждение, если тег похож на клановый
        if validation_message:
            logger.warning(f"Тег игрока '{player_tag}': {validation_message}")
        
        formatted_tag = quote(player_tag, safe='')
        endpoint = f"/players/{formatted_tag}"
        
        player_data = await self._make_request(endpoint)
        if player_data:
            logger.info(f"Получена информация об игроке {player_tag}")
        else:
            logger.warning(f"Не удалось получить информацию об игроке {player_tag}")
        
        return player_data
    
    async def get_clan_info(self, clan_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение информации о клане"""
        # Валидация тега клана
        is_valid, validation_message = validate_clan_tag(clan_tag)
        if not is_valid:
            logger.error(f"Невалидный тег клана '{clan_tag}': {validation_message}")
            return None
        
        formatted_tag = quote(clan_tag, safe='')
        endpoint = f"/clans/{formatted_tag}"
        
        clan_data = await self._make_request(endpoint)
        if clan_data:
            logger.info(f"Получена информация о клане {clan_tag}")
        else:
            logger.warning(f"Не удалось получить информацию о клане {clan_tag}")
        
        return clan_data
    
    async def get_clan_members(self, clan_tag: str) -> Optional[List[Dict[Any, Any]]]:
        """Получение списка участников клана"""
        # Валидация тега клана
        is_valid, validation_message = validate_clan_tag(clan_tag)
        if not is_valid:
            logger.error(f"Невалидный тег клана '{clan_tag}': {validation_message}")
            return None
        
        formatted_tag = quote(clan_tag, safe='')
        endpoint = f"/clans/{formatted_tag}/members"
        
        members_data = await self._make_request(endpoint)
        if members_data and 'items' in members_data:
            logger.info(f"Получен список участников клана {clan_tag}")
            return members_data['items']
        else:
            logger.warning(f"Не удалось получить список участников клана {clan_tag}")
            return None
    
    async def get_clan_current_war(self, clan_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение информации о текущей войне клана"""
        # Валидация тега клана
        is_valid, validation_message = validate_clan_tag(clan_tag)
        if not is_valid:
            logger.error(f"Невалидный тег клана '{clan_tag}': {validation_message}")
            return None
        
        formatted_tag = quote(clan_tag, safe='')
        endpoint = f"/clans/{formatted_tag}/currentwar"
        
        war_data = await self._make_request(endpoint)
        if war_data:
            logger.info(f"Получена информация о текущей войне клана {clan_tag}")
        else:
            logger.warning(f"Не удалось получить информацию о текущей войне клана {clan_tag}")
        
        return war_data
    
    async def get_clan_war_log(self, clan_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение журнала войн клана"""
        # Валидация тега клана
        is_valid, validation_message = validate_clan_tag(clan_tag)
        if not is_valid:
            logger.error(f"Невалидный тег клана '{clan_tag}': {validation_message}")
            return None
        
        formatted_tag = quote(clan_tag, safe='')
        endpoint = f"/clans/{formatted_tag}/warlog"
        
        war_log = await self._make_request(endpoint)
        if war_log:
            logger.info(f"Получен журнал войн клана {clan_tag}")
        else:
            logger.warning(f"Не удалось получить журнал войн клана {clan_tag}")
        
        return war_log
    
    async def get_clan_war_league_group(self, clan_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение информации о группе Лиги войн кланов"""
        # Валидация тега клана
        is_valid, validation_message = validate_clan_tag(clan_tag)
        if not is_valid:
            logger.error(f"Невалидный тег клана '{clan_tag}': {validation_message}")
            return None
        
        formatted_tag = quote(clan_tag, safe='')
        endpoint = f"/clans/{formatted_tag}/currentwar/leaguegroup"
        
        league_group = await self._make_request(endpoint)
        if league_group:
            logger.info(f"Получена информация о группе ЛВК клана {clan_tag}")
        else:
            logger.debug(f"Группа ЛВК для клана {clan_tag} не найдена или сезон не активен")
        
        return league_group
    
    async def get_cwl_war_info(self, war_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение информации о конкретной войне ЛВК"""
        formatted_tag = quote(war_tag, safe='')
        endpoint = f"/clanwarleagues/wars/{formatted_tag}"
        
        war_data = await self._make_request(endpoint)
        if war_data:
            logger.info(f"Получена информация о войне ЛВК {war_tag}")
        else:
            logger.warning(f"Не удалось получить информацию о войне ЛВК {war_tag}")
        
        return war_data
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            self.session = None


# Вспомогательные функции для работы с данными API
def format_clan_tag(tag: str) -> str:
    """Форматирование тега клана"""
    tag = tag.replace(' ', '').upper().replace('O', '0')
    if not tag.startswith('#'):
        tag = '#' + tag
    return tag


def format_player_tag(tag: str) -> str:
    """Форматирование тега игрока"""
    tag = tag.replace(' ', '').upper().replace('O', '0')
    if not tag.startswith('#'):
        tag = '#' + tag
    return tag


def is_clan_tag(tag: str) -> bool:
    """Проверка, является ли тег тегом клана"""
    # Убираем #, пробелы и приводим к верхнему регистру
    clean_tag = tag.replace('#', '').replace(' ', '').upper()
    
    # Простая проверка длины - теги кланов обычно 8-9 символов
    # Но нельзя точно определить тип тега только по длине
    # Эта функция должна использоваться осторожно
    return 8 <= len(clean_tag) <= 9


def is_player_tag(tag: str) -> bool:
    """Проверка, является ли тег тегом игрока"""
    # Убираем #, пробелы и приводим к верхнему регистру
    clean_tag = tag.replace('#', '').replace(' ', '').upper()
    
    # Теги игроков обычно 8-10 символов
    # Но если это 9 символов, лучше дополнительно проверить
    return 8 <= len(clean_tag) <= 10


def validate_player_tag(tag: str) -> tuple[bool, str]:
    """
    Проверка валидности тега игрока
    Возвращает: (валидность, сообщение об ошибке)
    """
    if not tag:
        return False, "Тег не может быть пустым"
    
    clean_tag = tag.replace('#', '').replace(' ', '').upper()
    
    # Проверяем длину
    if len(clean_tag) < 8:
        return False, "Тег слишком короткий (должен быть минимум 8 символов)"
    elif len(clean_tag) > 10:
        return False, "Тег слишком длинный (должен быть максимум 10 символов)"
    
    # Проверяем на недопустимые символы
    valid_chars = set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    if not all(c in valid_chars for c in clean_tag):
        return False, "Тег содержит недопустимые символы"
    
    # Предупреждение, если похоже на тег клана
    if len(clean_tag) == 9:
        return True, "Внимание: тег из 9 символов может быть тегом клана. Если поиск не дает результатов, попробуйте поиск по клану."
    
    return True, ""


def validate_clan_tag(tag: str) -> tuple[bool, str]:
    """
    Проверка валидности тега клана
    Возвращает: (валидность, сообщение об ошибке)
    """
    if not tag:
        return False, "Тег не может быть пустым"
    
    clean_tag = tag.replace('#', '').replace(' ', '').upper()
    
    # Проверяем длину
    if len(clean_tag) < 8:
        return False, "Тег слишком короткий (должен быть минимум 8 символов)"
    elif len(clean_tag) > 10:
        return False, "Тег слишком длинный (должен быть максимум 10 символов)"
    
    # Проверяем на недопустимые символы
    valid_chars = set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    if not all(c in valid_chars for c in clean_tag):
        return False, "Тег содержит недопустимые символы"
    
    return True, ""


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
    if not league_group:
        return False
    
    state = league_group.get('state', '')
    return state in ['inWar', 'warEnded']