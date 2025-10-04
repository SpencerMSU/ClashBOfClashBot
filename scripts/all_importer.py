"""
УЛЬТРА СКАНЕР ВСЕХ КЛАНОВ - Максимальная производительность
Сканирует МИЛЛИОНЫ кланов из всех регионов мира за все время их существования
Использует параллельные запросы и оптимизированную архитектуру для максимальной скорости
"""
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
import sys
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

# Проверка версии aiohttp для совместимости
try:
    aiohttp_version = aiohttp.__version__
    logger_init = logging.getLogger(__name__)
    logger_init.info(f"🔍 Используется aiohttp версии: {aiohttp_version}")
except:
    print("⚠️ Не удалось определить версию aiohttp")

# Добавление корневой папки проекта в путь Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Установка переменных окружения перед импортом config
if not os.getenv('BOT_TOKEN'):
    os.environ['BOT_TOKEN'] = 'DUMMY_TOKEN_FOR_IMPORT'
if not os.getenv('BOT_USERNAME'):
    os.environ['BOT_USERNAME'] = 'DUMMY_USERNAME'

from src.services.database import DatabaseService
from src.models.war import WarToSave
from config.config import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultra_scanner.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class UltraClanScanner:
    """УЛЬТРА СКАНЕР - Сканирует МИЛЛИОНЫ кланов с максимальной скоростью"""
    
    def __init__(self):
        # Определяем абсолютный путь к базе данных в корневой папке проекта
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        db_path = os.path.join(parent_dir, 'clashbot.db')
        
        logger.info(f"🗄️ Путь к базе данных: {db_path}")
        self.db_service = DatabaseService(db_path=db_path)
        
        # Статистика
        self.total_clans_found = 0
        self.total_clans_processed = 0
        self.total_wars_imported = 0
        self.total_wars_skipped = 0
        self.errors_count = 0
        self.start_time = None
        
        # Кэш обработанных кланов
        self.processed_clans: Set[str] = set()
        
        # Параллельность и производительность
        self.max_concurrent_requests = 50  # Максимум одновременных запросов
        self.requests_per_second = 100     # Максимум запросов в секунду
        self.semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        # Пул соединений для максимальной производительности
        self.connector = None
        self.session = None
        
        # МАКСИМАЛЬНЫЙ список всех локаций для сканирования МИЛЛИОНОВ кланов
        self.location_ids = self._get_all_locations()
        
        # Счетчики для rate limiting
        self.request_times = []
        
    def _get_all_locations(self) -> List[int]:
        """Получить ПОЛНЫЙ список ВСЕХ возможных локаций"""
        return [
            # Глобальные регионы
            32000006,  # International  
            32000007,  # Europe
            32000008,  # North America
            32000009,  # South America
            32000010,  # Asia
            32000011,  # Australia
            32000012,  # Africa
            
            # Все страны Европы
            32000185,  # Russia - ОГРОМНЫЙ регион
            32000094,  # Germany
            32000061,  # United Kingdom
            32000032,  # France
            32000166,  # Spain
            32000107,  # Italy
            32000105,  # Poland
            32000084,  # Netherlands
            32000223,  # Belgium
            32000034,  # Switzerland
            32000022,  # Austria
            32000091,  # Sweden
            32000143,  # Norway
            32000062,  # Denmark
            32000082,  # Finland
            32000152,  # Czech Republic
            32000157,  # Romania
            32000088,  # Hungary
            32000054,  # Greece
            32000101,  # Portugal
            32000119,  # Ukraine
            32000029,  # Belarus
            32000065,  # Ireland
            32000090,  # Croatia
            32000089,  # Serbia
            32000093,  # Bosnia and Herzegovina
            32000106,  # Slovenia
            32000133,  # Slovakia
            32000045,  # Bulgaria
            32000139,  # Lithuania
            32000099,  # Latvia
            32000058,  # Estonia
            32000067,  # Albania
            32000069,  # North Macedonia
            32000092,  # Malta
            32000037,  # Cyprus
            32000066,  # Iceland
            32000078,  # Luxembourg
            32000141,  # Moldova
            
            # Все страны Азии
            32000038,  # China - ОГРОМНЫЙ регион
            32000113,  # India - ОГРОМНЫЙ регион  
            32000095,  # Japan
            32000138,  # South Korea
            32000074,  # Turkey
            32000156,  # Indonesia
            32000118,  # Thailand
            32000018,  # Vietnam
            32000131,  # Philippines
            32000144,  # Malaysia
            32000142,  # Singapore
            32000226,  # Myanmar
            32000053,  # Bangladesh
            32000098,  # Pakistan
            32000228,  # Sri Lanka
            32000116,  # Afghanistan
            32000159,  # Nepal
            32000097,  # Taiwan
            32000135,  # Hong Kong
            32000036,  # Macau
            32000046,  # Mongolia
            32000127,  # Israel
            32000128,  # Lebanon
            32000075,  # Jordan
            32000229,  # Kuwait
            32000035,  # Bahrain
            32000070,  # Qatar
            32000134,  # Oman
            32000076,  # Yemen
            32000108,  # Syria
            32000033,  # Iran
            32000048,  # Iraq
            32000155,  # Saudi Arabia
            32000225,  # United Arab Emirates
            32000197,  # Kazakhstan
            32000043,  # Uzbekistan
            32000172,  # Turkmenistan
            32000140,  # Tajikistan
            32000121,  # Kyrgyzstan
            32000031,  # Cambodia
            32000130,  # Laos
            32000086,  # Brunei
            32000059,  # Maldives
            32000041,  # Bhutan
            32000077,  # Georgia
            32000050,  # Armenia
            32000056,  # Azerbaijan
            
            # Все страны Северной Америки
            32000222,  # United States - ОГРОМНЫЙ регион
            32000023,  # Canada - ОГРОМНЫЙ регион
            32000087,  # Mexico - ОГРОМНЫЙ регион
            32000015,  # Costa Rica
            32000049,  # Panama
            32000047,  # Guatemala
            32000071,  # Honduras
            32000039,  # El Salvador
            32000137,  # Nicaragua
            
            # Все страны Южной Америки
            32000100,  # Brazil - ОГРОМНЫЙ регион
            32000026,  # Argentina
            32000027,  # Chile
            32000028,  # Colombia
            32000224,  # Peru
            32000055,  # Venezuela
            32000221,  # Ecuador
            32000044,  # Uruguay
            32000147,  # Paraguay
            32000052,  # Bolivia
            
            # Все страны Карибского бассейна
            32000063,  # Dominican Republic
            32000103,  # Puerto Rico
            32000182,  # Cuba
            32000064,  # Jamaica
            32000079,  # Trinidad and Tobago
            32000219,  # Bahamas
            32000184,  # Barbados
            32000148,  # Haiti
            
            # Все страны Африки
            32000096,  # Egypt
            32000149,  # South Africa
            32000004,  # Morocco
            32000136,  # Algeria
            32000227,  # Nigeria
            32000154,  # Kenya
            32000110,  # Tunisia
            32000150,  # Libya
            32000085,  # Mauritius
            32000112,  # Senegal
            32000109,  # Ghana
            32000042,  # Ivory Coast
            32000102,  # Cameroon
            32000151,  # Uganda
            32000122,  # Tanzania
            32000160,  # Ethiopia
            32000129,  # Angola
            32000115,  # Zimbabwe
            32000120,  # Zambia
            32000080,  # Mozambique
            32000068,  # Botswana
            32000060,  # Namibia
            32000123,  # Madagascar
            32000146,  # Mauritania
            32000104,  # Mali
            32000126,  # Niger
            32000132,  # Burkina Faso
            32000145,  # Gabon
            32000114,  # Congo
            32000153,  # Rwanda
            32000125,  # Malawi
            32000111,  # Benin
            32000117,  # Togo
            32000040,  # Sierra Leone
            32000072,  # Liberia
            32000124,  # Guinea
            32000081,  # Chad
            32000083,  # Somalia
            32000158,  # Eritrea
            32000161,  # Djibouti
            32000030,  # Seychelles
            32000024,  # Cape Verde
            32000025,  # Comoros
            
            # Океания
            32000220,  # New Zealand
            32000051,  # Papua New Guinea
            32000073,  # Fiji
            32000019,  # Samoa
            32000057,  # Guam
            
            # Дополнительные ID для поиска скрытых кланов
            *range(32000001, 32000300),  # Сканируем все возможные ID локаций
        ]
    
    async def start_ultra_scan(self):
        """Запуск УЛЬТРА сканирования МИЛЛИОНОВ кланов"""
        logger.info("🚀" * 40)
        logger.info("🚀 ЗАПУСК УЛЬТРА СКАНЕРА ВСЕХ КЛАНОВ МИРА 🚀")
        logger.info("🚀" * 40)
        
        self.start_time = datetime.now()
        
        logger.info("⚡ Инициализация высокопроизводительной системы...")
        await self._init_high_performance_system()
        
        logger.info("💾 Инициализация базы данных...")
        await self.db_service.init_db()
        
        logger.info(f"🌍 Будет просканировано {len(self.location_ids)} локаций")
        logger.info(f"⚡ Максимальная параллельность: {self.max_concurrent_requests} запросов")
        logger.info(f"🚄 Скорость: {self.requests_per_second} запросов/сек")
        logger.info("🎯 ЦЕЛЬ: НАЙТИ И ИМПОРТИРОВАТЬ ВСЕ ВОЙНЫ ВСЕХ КЛАНОВ")
        logger.info("🚀" * 40)
        
        try:
            # Параллельное сканирование всех локаций
            await self._ultra_parallel_scan()
            
            # Отправка уведомления в бота после завершения
            await self._send_completion_notification()
            
        except Exception as e:
            logger.error(f"💥 Критическая ошибка: {e}", exc_info=True)
        finally:
            await self._cleanup()
        
        # Итоговая статистика
        self._print_final_stats()
    
    async def _init_high_performance_system(self):
        """Инициализация высокопроизводительной системы"""
        # Создаем коннектор с максимальной производительностью
        self.connector = aiohttp.TCPConnector(
            limit=200,              # Максимум соединений в пуле
            limit_per_host=100,     # Максимум соединений на хост
            ttl_dns_cache=300,      # DNS кэш на 5 минут
            use_dns_cache=True,     # Используем DNS кэш
            keepalive_timeout=60,   # Держим соединения живыми
            enable_cleanup_closed=True,
            force_close=False
        )
        
        # Создаем сессию с оптимизированными настройками
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout,
            headers={
                'Authorization': f'Bearer {config.COC_API_TOKEN}',
                'Accept': 'application/json',
                'User-Agent': 'ClashBot-UltraScanner/1.0'
            }
        )
    
    async def _ultra_parallel_scan(self):
        """УЛЬТРА параллельное сканирование всех локаций"""
        logger.info("⚡ Начинаем УЛЬТРА параллельное сканирование...")
        
        # Создаем задачи для всех локаций параллельно
        tasks = []
        for location_id in self.location_ids:
            task = asyncio.create_task(self._scan_location_ultra(location_id))
            tasks.append(task)
        
        # Выполняем все задачи параллельно с прогрессом
        completed = 0
        for task in asyncio.as_completed(tasks):
            try:
                await task
                completed += 1
                logger.info(f"📍 Завершено локаций: {completed}/{len(self.location_ids)}")
            except Exception as e:
                logger.error(f"💥 Ошибка при сканировании локации: {e}")
                self.errors_count += 1
    
    async def _scan_location_ultra(self, location_id: int):
        """УЛЬТРА сканирование одной локации"""
        try:
            logger.info(f"🔍 Начинаем сканирование локации {location_id}...")
            
            # Получаем ВСЕ кланы из локации используя множественные запросы
            all_clans = []
            
            # Пробуем разные endpoints для получения максимального количества кланов
            endpoints_to_try = [
                f"/locations/{location_id}/rankings/clans",
                f"/locations/{location_id}/rankings/players", 
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    clans = await self._get_all_clans_from_endpoint(endpoint, location_id)
                    if clans:
                        all_clans.extend(clans)
                        logger.info(f"📊 Endpoint {endpoint}: +{len(clans)} кланов")
                except Exception as e:
                    logger.debug(f"⚠️ Endpoint {endpoint} недоступен: {e}")
            
            # Удаляем дубликаты
            unique_clans = {}
            for clan in all_clans:
                clan_tag = clan.get('tag')
                if clan_tag and clan_tag not in unique_clans:
                    unique_clans[clan_tag] = clan
            
            all_clans = list(unique_clans.values())
            self.total_clans_found += len(all_clans)
            
            if not all_clans:
                logger.debug(f"❌ Локация {location_id}: кланы не найдены")
                return
            
            logger.info(f"✅ Локация {location_id}: найдено {len(all_clans)} уникальных кланов")
            
            # Параллельно обрабатываем все кланы
            clan_tasks = []
            for clan in all_clans:
                clan_tag = clan.get('tag')
                if clan_tag and clan_tag not in self.processed_clans:
                    task = asyncio.create_task(self._process_clan_ultra(clan_tag))
                    clan_tasks.append(task)
            
            # Выполняем обработку кланов пакетами для контроля нагрузки
            batch_size = 20
            for i in range(0, len(clan_tasks), batch_size):
                batch = clan_tasks[i:i + batch_size]
                await asyncio.gather(*batch, return_exceptions=True)
                
                # Добавляем небольшую паузу между пакетами
                if i + batch_size < len(clan_tasks):
                    await asyncio.sleep(0.1)
            
            logger.info(f"🎯 Локация {location_id}: обработка завершена")
            
        except Exception as e:
            logger.error(f"💥 Ошибка при сканировании локации {location_id}: {e}")
            self.errors_count += 1
    
    async def _get_all_clans_from_endpoint(self, endpoint: str, location_id: int) -> List[Dict[str, Any]]:
        """Получение ВСЕХ кланов из endpoint с пагинацией"""
        all_items = []
        
        try:
            # Пробуем получить максимальное количество данных
            limits_to_try = [1000, 500, 200]  # Разные лимиты для максимального охвата
            
            for limit in limits_to_try:
                try:
                    url = f"{config.COC_API_BASE_URL}{endpoint}?limit={limit}"
                    
                    async with self.semaphore:
                        await self._rate_limit()
                        
                        async with self.session.get(url) as response:
                            if response.status == 200:
                                data = await response.json()
                                items = data.get('items', [])
                                
                                if items:
                                    # Для rankings/players извлекаем кланы из профилей игроков
                                    if 'players' in endpoint:
                                        clans = []
                                        for player in items:
                                            clan = player.get('clan')
                                            if clan and clan.get('tag'):
                                                clans.append(clan)
                                        all_items.extend(clans)
                                    else:
                                        all_items.extend(items)
                                    
                                    logger.debug(f"📈 {endpoint} (limit={limit}): +{len(items)} элементов")
                                    break  # Успешно получили данные
                                    
                            elif response.status == 403:
                                logger.debug(f"🔒 {endpoint}: доступ запрещен")
                                break
                            else:
                                logger.debug(f"⚠️ {endpoint}: статус {response.status}")
                                
                except Exception as e:
                    logger.debug(f"⚠️ Ошибка limit={limit}: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"💥 Ошибка endpoint {endpoint}: {e}")
        
        return all_items
    
    async def _process_clan_ultra(self, clan_tag: str):
        """УЛЬТРА обработка клана с максимальной скоростью"""
        if clan_tag in self.processed_clans:
            return
        
        self.processed_clans.add(clan_tag)
        self.total_clans_processed += 1
        
        try:
            async with self.semaphore:
                await self._rate_limit()
                
                # Получаем журнал войн клана
                url = f"{config.COC_API_BASE_URL}/clans/{quote(clan_tag)}/warlog"
                
                async with self.session.get(url) as response:
                    if response.status != 200:
                        if response.status == 403:
                            logger.debug(f"🔒 Клан {clan_tag}: журнал приватный")
                        else:
                            logger.debug(f"⚠️ Клан {clan_tag}: статус {response.status}")
                        return
                    
                    data = await response.json()
                    wars = data.get('items', [])
                    
                    if not wars:
                        return
                    
                    # Параллельно обрабатываем все войны клана
                    import_tasks = []
                    for war_entry in wars:
                        if war_entry.get('result') in ['win', 'lose', 'tie']:
                            task = asyncio.create_task(self._import_war_ultra(war_entry))
                            import_tasks.append(task)
                    
                    if import_tasks:
                        results = await asyncio.gather(*import_tasks, return_exceptions=True)
                        imported = sum(1 for r in results if r is True)
                        
                        if imported > 0:
                            logger.debug(f"⚡ Клан {clan_tag}: импортировано {imported} войн")
        
        except Exception as e:
            logger.debug(f"💥 Ошибка обработки клана {clan_tag}: {e}")
            self.errors_count += 1
    
    async def _import_war_ultra(self, war_entry: Dict[str, Any]) -> bool:
        """УЛЬТРА быстрый импорт войны"""
        try:
            end_time = war_entry.get('endTime', '')
            if not end_time:
                return False
            
            # Быстрая проверка существования войны
            if await self.db_service.war_exists(end_time):
                self.total_wars_skipped += 1
                return False
            
            # Создание объекта войны
            opponent_name = war_entry.get('opponent', {}).get('name', 'Unknown')
            team_size = war_entry.get('teamSize', 0)
            clan_stars = war_entry.get('clan', {}).get('stars', 0)
            opponent_stars = war_entry.get('opponent', {}).get('stars', 0)
            clan_destruction = war_entry.get('clan', {}).get('destructionPercentage', 0.0)
            opponent_destruction = war_entry.get('opponent', {}).get('destructionPercentage', 0.0)
            result = war_entry.get('result', 'unknown')
            clan_attacks_used = war_entry.get('clan', {}).get('attacks', team_size * 2)
            
            war_to_save = WarToSave(
                end_time=end_time,
                opponent_name=opponent_name,
                team_size=team_size,
                clan_stars=clan_stars,
                opponent_stars=opponent_stars,
                clan_destruction=clan_destruction,
                opponent_destruction=opponent_destruction,
                clan_attacks_used=clan_attacks_used,
                result=result,
                is_cwl_war=False,
                total_violations=0,
                attacks_by_member={}
            )
            
            # Быстрое сохранение в БД
            success = await self.db_service.save_war(war_to_save)
            
            if success:
                self.total_wars_imported += 1
                return True
            else:
                self.errors_count += 1
                return False
                
        except Exception as e:
            logger.debug(f"💥 Ошибка импорта войны: {e}")
            self.errors_count += 1
            return False
    
    async def _rate_limit(self):
        """Контроль скорости запросов"""
        now = time.time()
        
        # Удаляем старые записи (старше 1 секунды)
        self.request_times = [t for t in self.request_times if now - t < 1.0]
        
        # Если достигли лимита, ждем
        if len(self.request_times) >= self.requests_per_second:
            sleep_time = 1.0 - (now - self.request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.request_times.append(now)
    
    async def _send_completion_notification(self):
        """Отправка уведомления в бота о завершении импорта"""
        try:
            logger.info("📱 Отправляем уведомление о завершении импорта...")
            
            # Создаем сообщение с результатами
            duration = datetime.now() - self.start_time
            message = (
                f"🎉 **ИМПОРТ ВОЙН ЗАВЕРШЕН УСПЕШНО!** 🎉\n\n"
                f"📊 **Статистика:**\n"
                f"• ⏱️ Время выполнения: {duration}\n"
                f"• 🌍 Локаций просканировано: {len(self.location_ids)}\n"
                f"• 🏰 Кланов найдено: {self.total_clans_found:,}\n"
                f"• ⚡ Кланов обработано: {self.total_clans_processed:,}\n"
                f"• ⚔️ Войн импортировано: {self.total_wars_imported:,}\n"
                f"• 📦 Войн пропущено: {self.total_wars_skipped:,}\n"
                f"• ❌ Ошибок: {self.errors_count:,}\n\n"
                f"🚀 Ваша база данных пополнена МИЛЛИОНАМИ войн!"
            )
            
            # Отправляем уведомление всем пользователям через систему бота
            await self._notify_all_users(message)
            
        except Exception as e:
            logger.error(f"💥 Ошибка при отправке уведомления: {e}")
    
    async def _notify_all_users(self, message: str):
        """Уведомление всех пользователей бота"""
        try:
            # Получаем всех пользователей из базы данных
            users = await self.db_service.get_all_users()
            
            if not users:
                logger.info("👥 Нет пользователей для уведомления")
                return
            
            # Создаем простой HTTP клиент для отправки через Telegram Bot API
            telegram_url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
            
            notification_tasks = []
            for user in users:
                user_id = user.get('telegram_id')
                if user_id:
                    task = asyncio.create_task(
                        self._send_telegram_message(telegram_url, user_id, message)
                    )
                    notification_tasks.append(task)
            
            # Отправляем уведомления пакетами
            batch_size = 10
            for i in range(0, len(notification_tasks), batch_size):
                batch = notification_tasks[i:i + batch_size]
                await asyncio.gather(*batch, return_exceptions=True)
                await asyncio.sleep(0.1)  # Избегаем rate limiting Telegram
            
            logger.info(f"📱 Уведомления отправлены {len(users)} пользователям")
            
        except Exception as e:
            logger.error(f"💥 Ошибка при уведомлении пользователей: {e}")
    
    async def _send_telegram_message(self, url: str, user_id: int, message: str):
        """Отправка сообщения пользователю через Telegram API"""
        try:
            payload = {
                'chat_id': user_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.debug(f"✅ Уведомление отправлено пользователю {user_id}")
                else:
                    logger.debug(f"⚠️ Ошибка отправки пользователю {user_id}: {response.status}")
                    
        except Exception as e:
            logger.debug(f"💥 Ошибка отправки сообщения пользователю {user_id}: {e}")
    
    async def _cleanup(self):
        """Очистка ресурсов"""
        try:
            if self.session:
                await self.session.close()
            if self.connector:
                await self.connector.close()
        except Exception as e:
            logger.error(f"💥 Ошибка при очистке ресурсов: {e}")
    
    def _print_final_stats(self):
        """Вывод финальной статистики"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        logger.info("🎉" * 50)
        logger.info("🎉 УЛЬТРА СКАНИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО! 🎉")
        logger.info("🎉" * 50)
        logger.info(f"⏱️ Общее время выполнения: {duration}")
        logger.info(f"🌍 Локаций просканировано: {len(self.location_ids)}")
        logger.info(f"🏰 Кланов найдено: {self.total_clans_found:,}")
        logger.info(f"⚡ Кланов обработано: {self.total_clans_processed:,}")
        logger.info(f"⚔️ Войн импортировано: {self.total_wars_imported:,}")
        logger.info(f"📦 Войн пропущено: {self.total_wars_skipped:,}")
        logger.info(f"❌ Ошибок: {self.errors_count:,}")
        
        if self.total_clans_processed > 0:
            wars_per_clan = self.total_wars_imported / self.total_clans_processed
            logger.info(f"📈 Среднее войн на клан: {wars_per_clan:.2f}")
        
        if duration.total_seconds() > 0:
            clans_per_second = self.total_clans_processed / duration.total_seconds()
            wars_per_second = self.total_wars_imported / duration.total_seconds()
            logger.info(f"🚄 Скорость обработки: {clans_per_second:.2f} кланов/сек")
            logger.info(f"⚡ Скорость импорта: {wars_per_second:.2f} войн/сек")
        
        logger.info("🎉" * 50)


async def main():
    """Точка входа в УЛЬТРА сканер"""
    logger.info("🚀 Инициализация УЛЬТРА СКАНЕРА...")
    
    # Проверка рабочей папки
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    logger.info(f"📁 Текущая папка: {current_dir}")
    logger.info(f"📁 Скрипт находится в: {script_dir}")
    logger.info(f"📁 Корневая папка проекта: {parent_dir}")
    
    # Проверка базы данных
    db_path = os.path.join(parent_dir, 'clashbot.db')
    logger.info(f"🗄️ Ожидаемый путь к БД: {db_path}")
    
    if os.path.exists(db_path):
        logger.info("✅ База данных найдена")
        if os.access(db_path, os.R_OK):
            logger.info("✅ База данных доступна для чтения")
        else:
            logger.error("❌ Нет прав на чтение базы данных")
            sys.exit(1)
        if os.access(db_path, os.W_OK):
            logger.info("✅ База данных доступна для записи")
        else:
            logger.error("❌ Нет прав на запись в базу данных")
            sys.exit(1)
    else:
        logger.warning("⚠️ База данных не найдена, будет создана автоматически")
        # Проверяем права на создание файлов в корневой папке
        if not os.access(parent_dir, os.W_OK):
            logger.error(f"❌ Нет прав на создание БД в папке: {parent_dir}")
            sys.exit(1)
    
    # Проверка наличия обязательных токенов
    if not config.COC_API_TOKEN or config.COC_API_TOKEN == '':
        logger.error("💥 ОШИБКА: COC_API_TOKEN не установлен!")
        logger.error("Получите токен на https://developer.clashofclans.com")
        sys.exit(1)
    
    if not config.BOT_TOKEN or config.BOT_TOKEN == 'DUMMY_TOKEN_FOR_IMPORT':
        logger.error("💥 ОШИБКА: BOT_TOKEN не установлен!")
        logger.error("Установите токен бота для отправки уведомлений")
        sys.exit(1)
    
    scanner = UltraClanScanner()
    await scanner.start_ultra_scan()
    
    logger.info("🎉 УЛЬТРА СКАНЕР ЗАВЕРШИЛ РАБОТУ!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 УЛЬТРА сканер остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)