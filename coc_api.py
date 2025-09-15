"""
Клиент для работы с API Clash of Clans - аналог Java CocApiClient
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
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str) -> Optional[Dict[Any, Any]]:
        """Базовый метод для выполнения HTTP запросов"""
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
        
        url = f"{self.base_url}{endpoint}"
        try:
            async with self.session.get(url) as response:
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
        
        except aiohttp.ClientTimeout:
            logger.error(f"Таймаут при запросе к {url}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка клиента при запросе к {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON от {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к {url}: {e}")
            return None
    
    async def get_player_info(self, player_tag: str) -> Optional[Dict[Any, Any]]:
        """Получение информации об игроке"""
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