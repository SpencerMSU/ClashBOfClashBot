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
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        if not self.session:
            # Создаем коннектор с улучшенными настройками для стабильности
            connector = aiohttp.TCPConnector(
                limit=50,  # Уменьшаем общий лимит для стабильности
                limit_per_host=10,  # Уменьшаем лимит на хост
                enable_cleanup_closed=True,
                keepalive_timeout=60,  # Уменьшаем время жизни соединений
                ttl_dns_cache=300,  # Кэшируем DNS на 5 минут
                use_dns_cache=True,
                family=0,  # Использовать и IPv4 и IPv6
                ssl=False,  # COC API использует HTTPS, но отключаем дополнительную проверку SSL
                force_close=False  # Переиспользуем соединения
            )
            
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'ClashBot/1.0 (aiohttp)'
                },
                timeout=aiohttp.ClientTimeout(
                    total=30,      # Общий таймаут
                    connect=10,    # Таймаут подключения
                    sock_read=20,  # Таймаут чтения
                    sock_connect=10  # Таймаут сокета
                ),
                connector=connector
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        # НЕ закрываем сессию здесь, так как она может использоваться повторно
        pass

    async def _make_request(self, endpoint: str, max_retries: int = 3) -> Optional[Dict[Any, Any]]:
        """Базовый метод для выполнения HTTP запросов с retry логикой"""
        # Используем сессию из контекстного менеджера или создаем новую
        session_to_use = self.session
        if not session_to_use:
            # Создаем временную сессию для одного запроса
            connector = aiohttp.TCPConnector(
                limit=50,
                limit_per_host=10,
                enable_cleanup_closed=True,
                keepalive_timeout=60,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            session_to_use = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'ClashBot/1.0 (aiohttp)'
                },
                timeout=aiohttp.ClientTimeout(
                    total=30,
                    connect=10,
                    sock_read=20,
                    sock_connect=10
                ),
                connector=connector
            )
        
        url = f"{self.base_url}{endpoint}"
        last_exception = None
        
        # Retry логика с экспоненциальной задержкой
        for attempt in range(max_retries):
            try:
                async with session_to_use.get(url) as response:
                    if response.status == 403:
                        logger.error("ОШИБКА 403: API ключ недействителен или ваш IP изменился. "
                                   "Проверьте настройки на developer.clashofclans.com")
                        return None
                    elif response.status == 404:
                        logger.warning(f"Ресурс не найден: {url}")
                        return None
                    elif response.status == 429:
                        # Rate limiting - ждем и повторяем
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limit достигнут для {url}. Ожидание {retry_after} секунд...")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        return None
                    elif response.status >= 500:
                        # Серверные ошибки - можно повторить
                        logger.warning(f"Серверная ошибка {response.status} для {url}. Попытка {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
                            continue
                        return None
                    elif response.status != 200:
                        logger.error(f"HTTP {response.status} при запросе к {url}")
                        return None
                    
                    return await response.json()
                    
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(f"Таймаут при запросе к {url} (попытка {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                    
            except aiohttp.ClientConnectorError as e:
                last_exception = e
                logger.warning(f"Ошибка соединения с {url} (попытка {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                    
            except aiohttp.ClientError as e:
                last_exception = e
                logger.warning(f"Сетевая ошибка при запросе к {url} (попытка {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                    
            except Exception as e:
                last_exception = e
                logger.error(f"Неожиданная ошибка при запросе к {url}: {e}")
                break  # Не повторяем при неожиданных ошибках
        
        # Если мы дошли сюда, все попытки неудачны
        logger.error(f"Не удалось выполнить запрос к {url} после {max_retries} попыток. Последняя ошибка: {last_exception}")
        
        try:
            # Закрываем сессию только если она была создана временно
            if not self.session and session_to_use:
                await session_to_use.close()
        except Exception as cleanup_error:
            logger.warning(f"Ошибка при закрытии временной сессии: {cleanup_error}")
            
        return None

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