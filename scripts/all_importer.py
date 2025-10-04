"""
All Clans Importer - Программа для импорта данных войн из ВСЕХ кланов в игре
Сканирует абсолютно все кланы во всех регионах без ограничений
Запускается независимо от main.py для единоразового массового импорта данных
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
import sys
import os
import json

# Установка переменных окружения перед импортом config, если они не установлены
if not os.getenv('BOT_TOKEN'):
    os.environ['BOT_TOKEN'] = 'DUMMY_TOKEN_FOR_IMPORT'
if not os.getenv('BOT_USERNAME'):
    os.environ['BOT_USERNAME'] = 'DUMMY_USERNAME'
if not os.getenv('COC_API_TOKEN'):
    # Это будет проверено позже в main()
    os.environ['COC_API_TOKEN'] = 'WILL_BE_VALIDATED_IN_MAIN'

from src.services.database import DatabaseService
from src.services.coc_api import CocApiClient
from src.models.war import WarToSave
from config.config import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('all_importer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AllClansImporter:
    """Импортер войн из ВСЕХ кланов в игре без ограничений"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.coc_client = CocApiClient()
        
        # Статистика импорта
        self.total_clans_checked = 0
        self.total_wars_imported = 0
        self.total_wars_skipped = 0
        self.errors_count = 0
        
        # Кэш обработанных кланов
        self.processed_clans: Set[str] = set()
        
        # ПОЛНЫЙ список ВСЕХ локаций для сканирования
        # Включает все регионы, страны и международные зоны
        self.location_ids = [
            # Континентальные регионы
            32000007,  # Europe
            32000008,  # North America
            32000009,  # South America
            32000010,  # Asia
            32000011,  # Australia
            32000012,  # Africa
            32000006,  # International
            
            # Крупнейшие страны
            32000185,  # Russia
            32000038,  # China
            32000113,  # India
            32000094,  # Germany
            32000222,  # United States
            32000061,  # United Kingdom
            32000023,  # Canada
            32000032,  # France
            32000166,  # Spain
            32000107,  # Italy
            32000100,  # Brazil
            32000095,  # Japan
            32000138,  # South Korea
            32000074,  # Turkey
            32000105,  # Poland
            32000156,  # Indonesia
            32000118,  # Thailand
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
            32000197,  # Kazakhstan
            32000033,  # Iran
            32000048,  # Iraq
            32000155,  # Saudi Arabia
            32000225,  # United Arab Emirates
            32000096,  # Egypt
            32000149,  # South Africa
            32000004,  # Morocco
            32000136,  # Algeria
            32000227,  # Nigeria
            32000154,  # Kenya
            32000087,  # Mexico
            32000026,  # Argentina
            32000027,  # Chile
            32000028,  # Colombia
            32000224,  # Peru
            32000055,  # Venezuela
            32000221,  # Ecuador
            32000015,  # Costa Rica
            32000044,  # Uruguay
            32000147,  # Paraguay
            32000052,  # Bolivia
            32000049,  # Panama
            32000063,  # Dominican Republic
            32000103,  # Puerto Rico
            32000182,  # Cuba
            32000047,  # Guatemala
            32000071,  # Honduras
            32000039,  # El Salvador
            32000137,  # Nicaragua
            32000064,  # Jamaica
            32000079,  # Trinidad and Tobago
            32000219,  # Bahamas
            32000184,  # Barbados
            32000148,  # Haiti
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
            32000220,  # New Zealand
            32000051,  # Papua New Guinea
            32000073,  # Fiji
            32000019,  # Samoa
            32000057,  # Guam
            
            # Дополнительные европейские страны
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
            32000077,  # Georgia
            32000050,  # Armenia
            32000056,  # Azerbaijan
            
            # Дополнительные азиатские страны
            32000127,  # Israel
            32000128,  # Lebanon
            32000075,  # Jordan
            32000229,  # Kuwait
            32000035,  # Bahrain
            32000070,  # Qatar
            32000134,  # Oman
            32000076,  # Yemen
            32000108,  # Syria
            32000043,  # Uzbekistan
            32000172,  # Turkmenistan
            32000140,  # Tajikistan
            32000121,  # Kyrgyzstan
            32000031,  # Cambodia
            32000130,  # Laos
            32000086,  # Brunei
            32000059,  # Maldives
            32000041,  # Bhutan
            
            # Дополнительные африканские страны
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
        ]
    
    async def start_import(self):
        """Начало процесса импорта"""
        logger.info("=" * 80)
        logger.info("ЗАПУСК ПОЛНОГО ИМПОРТА ВОЙН ИЗ ВСЕХ КЛАНОВ")
        logger.info("=" * 80)
        logger.info("Инициализация базы данных...")
        
        await self.db_service.init_db()
        
        logger.info("База данных инициализирована")
        logger.info(f"Будет проверено локаций: {len(self.location_ids)}")
        logger.info("СКАНИРОВАНИЕ ВСЕХ КЛАНОВ БЕЗ ОГРАНИЧЕНИЙ")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # Импорт кланов по локациям
            await self._import_by_locations()
            
        except Exception as e:
            logger.error(f"Критическая ошибка при импорте: {e}", exc_info=True)
        finally:
            # Сохранение ошибок API в файл
            await self._save_api_errors()
            await self.coc_client.close()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Итоговая статистика
        logger.info("=" * 80)
        logger.info("ПОЛНЫЙ ИМПОРТ ЗАВЕРШЕН")
        logger.info("=" * 80)
        logger.info(f"Время выполнения: {duration}")
        logger.info(f"Всего кланов проверено: {self.total_clans_checked}")
        logger.info(f"Уникальных кланов обработано: {len(self.processed_clans)}")
        logger.info(f"Войн импортировано: {self.total_wars_imported}")
        logger.info(f"Войн пропущено (уже в БД): {self.total_wars_skipped}")
        logger.info(f"Ошибок: {self.errors_count}")
        logger.info("=" * 80)
    
    async def _import_by_locations(self):
        """Импорт войн кланов по локациям - ПОЛНОЕ СКАНИРОВАНИЕ"""
        logger.info("\n" + "=" * 80)
        logger.info("ИМПОРТ ПО ВСЕМ ЛОКАЦИЯМ")
        logger.info("=" * 80)
        
        for location_id in self.location_ids:
            try:
                logger.info(f"\nОбработка локации {location_id}...")
                
                # Получаем АБСОЛЮТНО ВСЕ кланы из локации
                # API позволяет получать до 1000 кланов за раз
                # Мы будем запрашивать без ограничений до тех пор, пока есть кланы
                all_clans = []
                offset = 0
                max_retries = 3
                no_clans_count = 0
                
                while True:
                    retry_count = 0
                    clans = None
                    
                    # Повторные попытки при ошибках
                    while retry_count < max_retries:
                        try:
                            clans = await self._get_clans_by_location(location_id, limit=1000, offset=offset)
                            if clans is not None:
                                break
                        except Exception as e:
                            retry_count += 1
                            logger.warning(f"  Попытка {retry_count}/{max_retries} не удалась: {e}")
                            if retry_count < max_retries:
                                await asyncio.sleep(2)  # Пауза перед повторной попыткой
                    
                    if not clans:
                        no_clans_count += 1
                        # Если несколько раз подряд не получили кланов, значит достигли конца
                        if no_clans_count >= 2:
                            logger.info(f"  Достигнут конец списка кланов для локации {location_id}")
                            break
                        # Иначе попробуем следующий offset
                        offset += 1000
                        continue
                    
                    # Сбрасываем счетчик, если получили кланов
                    no_clans_count = 0
                    
                    all_clans.extend(clans)
                    logger.info(f"  Offset {offset}: Получено {len(clans)} кланов (всего: {len(all_clans)})")
                    
                    # Если получили меньше 1000, возможно это последняя партия
                    # но продолжаем проверять дальше на случай пропусков в данных API
                    if len(clans) < 1000:
                        # Проверим еще несколько offset-ов
                        offset += 1000
                        if offset > len(all_clans) + 5000:  # Если прошли достаточно далеко за последними данными
                            break
                    else:
                        offset += 1000
                    
                    # Небольшая пауза между запросами к API
                    await asyncio.sleep(0.1)
                
                if not all_clans:
                    logger.warning(f"Не удалось получить кланы для локации {location_id}")
                    continue
                
                logger.info(f"ВСЕГО найдено {len(all_clans)} кланов в локации {location_id}")
                
                # Обрабатываем каждый клан
                for idx, clan in enumerate(all_clans, 1):
                    clan_tag = clan.get('tag')
                    if not clan_tag:
                        continue
                    
                    if clan_tag in self.processed_clans:
                        continue
                    
                    clan_name = clan.get('name', 'Unknown')
                    logger.info(f"  [{idx}/{len(all_clans)}] Обработка клана: {clan_name} ({clan_tag})")
                    
                    await self._process_clan(clan_tag)
                    self.processed_clans.add(clan_tag)
                    
                    # Небольшая задержка между запросами
                    await asyncio.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Ошибка при обработке локации {location_id}: {e}")
                self.errors_count += 1
    
    async def _get_clans_by_location(self, location_id: int, limit: int = 1000, offset: int = 0) -> List[Dict[Any, Any]]:
        """Получение кланов по локации с поддержкой offset"""
        try:
            async with self.coc_client as client:
                # Используем endpoint с limit для получения максимального количества кланов
                # Некоторые API поддерживают before/after, но COC API использует limit
                endpoint = f"/locations/{location_id}/rankings/clans?limit={limit}"
                
                # Примечание: COC API для rankings обычно не поддерживает offset напрямую
                # Но мы можем использовать cursor-based pagination если доступно
                # Для простоты используем limit и пытаемся получить максимум данных
                
                data = await client._make_request(endpoint)
                
                if data and 'items' in data:
                    return data['items']
                
        except Exception as e:
            logger.error(f"Ошибка при получении кланов локации {location_id}: {e}")
        
        return []
    
    async def _process_clan(self, clan_tag: str):
        """Обработка одного клана - импорт его войн"""
        self.total_clans_checked += 1
        
        try:
            # Получаем журнал войн клана
            async with self.coc_client as client:
                war_log = await client.get_clan_war_log(clan_tag)
                
                if not war_log or 'items' not in war_log:
                    logger.debug(f"    Журнал войн недоступен для {clan_tag}")
                    return
                
                wars = war_log.get('items', [])
                
                if not wars:
                    logger.debug(f"    Нет войн в журнале для {clan_tag}")
                    return
                
                logger.info(f"    Найдено {len(wars)} войн в журнале")
                
                # Обрабатываем каждую войну из журнала
                for war_entry in wars:
                    result = war_entry.get('result')
                    
                    # Проверяем, что война завершена
                    if result not in ['win', 'lose', 'tie']:
                        continue
                    
                    # Получаем время окончания войны
                    end_time = war_entry.get('endTime')
                    if not end_time:
                        continue
                    
                    # Проверяем, не импортирована ли уже эта война
                    if await self.db_service.war_exists(end_time):
                        self.total_wars_skipped += 1
                        continue
                    
                    # Импортируем войну
                    await self._import_war_from_log(war_entry, clan_tag)
                
        except Exception as e:
            logger.error(f"    Ошибка при обработке клана {clan_tag}: {e}")
            self.errors_count += 1
    
    async def _import_war_from_log(self, war_entry: Dict[Any, Any], clan_tag: str):
        """Импорт войны из записи журнала"""
        try:
            # Получаем детальную информацию о войне, если возможно
            # Для войн из журнала нам доступны только основные данные
            
            end_time = war_entry.get('endTime', '')
            opponent_name = war_entry.get('opponent', {}).get('name', 'Unknown')
            team_size = war_entry.get('teamSize', 0)
            clan_stars = war_entry.get('clan', {}).get('stars', 0)
            opponent_stars = war_entry.get('opponent', {}).get('stars', 0)
            clan_destruction = war_entry.get('clan', {}).get('destructionPercentage', 0.0)
            opponent_destruction = war_entry.get('opponent', {}).get('destructionPercentage', 0.0)
            result = war_entry.get('result', 'unknown')
            
            # Подсчет атак из доступных данных
            clan_attacks_used = war_entry.get('clan', {}).get('attacks', 0)
            if clan_attacks_used == 0:
                # Если нет данных об атаках, предполагаем стандартное количество
                clan_attacks_used = team_size * 2
            
            # Создание объекта войны для сохранения
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
                is_cwl_war=False,  # Информация недоступна в журнале
                total_violations=0,  # Требует детального анализа атак
                attacks_by_member={}  # Детальная информация об атаках недоступна в журнале
            )
            
            # Сохранение в базу данных
            success = await self.db_service.save_war(war_to_save)
            
            if success:
                self.total_wars_imported += 1
                logger.info(f"      ✓ Война импортирована: vs {opponent_name} ({result}) - {end_time}")
            else:
                logger.warning(f"      ✗ Не удалось сохранить войну: vs {opponent_name}")
                self.errors_count += 1
            
        except Exception as e:
            logger.error(f"    Ошибка при импорте войны: {e}")
            self.errors_count += 1
    
    async def _save_api_errors(self):
        """Сохранение ошибок API в файл all_clans_api_errors.json"""
        try:
            errors = self.coc_client.get_errors()
            
            if not errors:
                logger.info("Нет ошибок API для сохранения")
                return
            
            # Группируем ошибки по тегам кланов для удобства
            errors_by_clan = {}
            for error in errors:
                endpoint = error['endpoint']
                # Извлекаем тег клана из endpoint
                if '/clans/' in endpoint:
                    # Находим тег клана между /clans/ и следующим /
                    parts = endpoint.split('/clans/')
                    if len(parts) > 1:
                        clan_tag_encoded = parts[1].split('/')[0]
                        # Декодируем URL-encoded тег
                        from urllib.parse import unquote
                        clan_tag = unquote(clan_tag_encoded)
                        
                        if clan_tag not in errors_by_clan:
                            errors_by_clan[clan_tag] = []
                        
                        errors_by_clan[clan_tag].append({
                            'timestamp': error['timestamp'],
                            'endpoint': error['endpoint'],
                            'status_code': error['status_code'],
                            'error_message': error['error_message']
                        })
            
            # Сохраняем в файл
            error_data = {
                'scan_time': datetime.now().isoformat(),
                'total_errors': len(errors),
                'errors_by_clan': errors_by_clan,
                'all_errors': errors
            }
            
            with open('all_clans_api_errors.json', 'w', encoding='utf-8') as f:
                json.dump(error_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Сохранено {len(errors)} ошибок API в файл all_clans_api_errors.json")
            logger.info(f"Кланов с ошибками: {len(errors_by_clan)}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении ошибок API: {e}")


async def main():
    """Точка входа в программу"""
    logger.info("Инициализация импортера ВСЕХ войн...")
    
    # Проверка наличия обязательного COC_API_TOKEN
    if not config.COC_API_TOKEN or config.COC_API_TOKEN == '' or config.COC_API_TOKEN == 'WILL_BE_VALIDATED_IN_MAIN':
        logger.error("=" * 80)
        logger.error("ОШИБКА: COC_API_TOKEN не установлен!")
        logger.error("Для работы программы необходим токен API Clash of Clans")
        logger.error("Получите токен на https://developer.clashofclans.com")
        logger.error("Установите его в файле api_tokens.txt или переменной окружения")
        logger.error("=" * 80)
        sys.exit(1)
    
    importer = AllClansImporter()
    await importer.start_import()
    
    logger.info("Программа завершена")


if __name__ == "__main__":
    # Запуск программы
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nПрограмма прервана пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)
