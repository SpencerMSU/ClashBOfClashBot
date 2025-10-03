"""
Error Handler - Скрипт для повторного сканирования кланов из 404_api_errors.json
Проходится по файлу с ошибками и пытается повторно получить данные о войнах кланов
"""
import asyncio
import logging
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Set

# Установка переменных окружения перед импортом config
if not os.getenv('BOT_TOKEN'):
    os.environ['BOT_TOKEN'] = 'DUMMY_TOKEN_FOR_ERRORS'
if not os.getenv('BOT_USERNAME'):
    os.environ['BOT_USERNAME'] = 'DUMMY_USERNAME'
if not os.getenv('COC_API_TOKEN'):
    os.environ['COC_API_TOKEN'] = 'WILL_BE_VALIDATED_IN_MAIN'

from database import DatabaseService
from coc_api import CocApiClient
from models.war import WarToSave
from config import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('errors_rescan.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ErrorHandler:
    """Обработчик ошибок API для повторного сканирования"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.coc_client = CocApiClient()
        
        # Статистика
        self.total_clans_rescanned = 0
        self.total_wars_imported = 0
        self.total_wars_skipped = 0
        self.still_failing = 0
        self.successful_rescans = 0
    
    async def start_rescan(self):
        """Начало процесса повторного сканирования"""
        logger.info("=" * 80)
        logger.info("ЗАПУСК ПОВТОРНОГО СКАНИРОВАНИЯ КЛАНОВ С ОШИБКАМИ")
        logger.info("=" * 80)
        
        # Проверка наличия файла с ошибками
        if not os.path.exists('404_api_errors.json'):
            logger.error("Файл 404_api_errors.json не найден!")
            logger.error("Сначала запустите war_importer.py для создания файла с ошибками")
            return
        
        logger.info("Инициализация базы данных...")
        await self.db_service.init_db()
        logger.info("База данных инициализирована")
        
        # Загрузка ошибок из файла
        errors_data = self._load_errors()
        
        if not errors_data:
            logger.error("Не удалось загрузить данные об ошибках")
            return
        
        errors_by_clan = errors_data.get('errors_by_clan', {})
        
        if not errors_by_clan:
            logger.info("Нет кланов с ошибками для повторного сканирования")
            return
        
        logger.info(f"Найдено {len(errors_by_clan)} кланов с ошибками")
        logger.info(f"Начинается повторное сканирование...")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # Повторное сканирование кланов
            await self._rescan_clans(errors_by_clan)
            
        except Exception as e:
            logger.error(f"Критическая ошибка при повторном сканировании: {e}", exc_info=True)
        finally:
            # Сохранение новых ошибок
            await self._save_remaining_errors()
            await self.coc_client.close()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Итоговая статистика
        logger.info("=" * 80)
        logger.info("ПОВТОРНОЕ СКАНИРОВАНИЕ ЗАВЕРШЕНО")
        logger.info("=" * 80)
        logger.info(f"Время выполнения: {duration}")
        logger.info(f"Кланов просканировано повторно: {self.total_clans_rescanned}")
        logger.info(f"Успешных повторных попыток: {self.successful_rescans}")
        logger.info(f"Всё ещё недоступны: {self.still_failing}")
        logger.info(f"Войн импортировано: {self.total_wars_imported}")
        logger.info(f"Войн пропущено (уже в БД): {self.total_wars_skipped}")
        logger.info("=" * 80)
    
    def _load_errors(self) -> Dict[str, Any]:
        """Загрузка ошибок из JSON файла"""
        try:
            with open('404_api_errors.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Загружено данных об ошибках:")
            logger.info(f"  Время сканирования: {data.get('scan_time', 'Неизвестно')}")
            logger.info(f"  Всего ошибок: {data.get('total_errors', 0)}")
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке файла 404_api_errors.json: {e}")
            return {}
    
    async def _rescan_clans(self, errors_by_clan: Dict[str, List[Dict[str, Any]]]):
        """Повторное сканирование кланов с ошибками"""
        for idx, (clan_tag, clan_errors) in enumerate(errors_by_clan.items(), 1):
            logger.info(f"\n[{idx}/{len(errors_by_clan)}] Повторное сканирование клана: {clan_tag}")
            logger.info(f"  Предыдущих ошибок: {len(clan_errors)}")
            
            # Показываем последнюю ошибку
            if clan_errors:
                last_error = clan_errors[-1]
                logger.info(f"  Последняя ошибка: {last_error.get('error_message', 'Unknown')}")
                logger.info(f"  Статус код: {last_error.get('status_code', 'Unknown')}")
            
            self.total_clans_rescanned += 1
            
            # Пытаемся получить данные о войнах клана
            success = await self._process_clan(clan_tag)
            
            if success:
                self.successful_rescans += 1
                logger.info(f"  ✓ Клан успешно просканирован повторно")
            else:
                self.still_failing += 1
                logger.warning(f"  ✗ Клан всё ещё недоступен")
            
            # Небольшая задержка между запросами
            await asyncio.sleep(0.5)
    
    async def _process_clan(self, clan_tag: str) -> bool:
        """Обработка одного клана - импорт его войн"""
        try:
            # Получаем журнал войн клана
            async with self.coc_client as client:
                war_log = await client.get_clan_war_log(clan_tag)
                
                if not war_log or 'items' not in war_log:
                    logger.debug(f"    Журнал войн недоступен для {clan_tag}")
                    return False
                
                wars = war_log.get('items', [])
                
                if not wars:
                    logger.debug(f"    Нет войн в журнале для {clan_tag}")
                    return True  # Успех, просто нет данных
                
                logger.info(f"    Найдено {len(wars)} войн в журнале")
                
                # Обрабатываем каждую войну из журнала
                imported = 0
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
                    if await self._import_war_from_log(war_entry, clan_tag):
                        imported += 1
                
                if imported > 0:
                    logger.info(f"    Импортировано новых войн: {imported}")
                
                return True
                
        except Exception as e:
            logger.error(f"    Ошибка при обработке клана {clan_tag}: {e}")
            return False
    
    async def _import_war_from_log(self, war_entry: Dict[Any, Any], clan_tag: str) -> bool:
        """Импорт войны из записи журнала"""
        try:
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
                is_cwl_war=False,
                total_violations=0,
                attacks_by_member={}
            )
            
            # Сохранение в базу данных
            success = await self.db_service.save_war(war_to_save)
            
            if success:
                self.total_wars_imported += 1
                logger.debug(f"      ✓ Война импортирована: vs {opponent_name} ({result})")
                return True
            else:
                logger.warning(f"      ✗ Не удалось сохранить войну: vs {opponent_name}")
                return False
            
        except Exception as e:
            logger.error(f"    Ошибка при импорте войны: {e}")
            return False
    
    async def _save_remaining_errors(self):
        """Сохранение оставшихся ошибок в файл"""
        try:
            errors = self.coc_client.get_errors()
            
            if not errors:
                logger.info("Нет новых ошибок после повторного сканирования")
                # Если ошибок нет, удаляем старый файл или создаем пустой
                error_data = {
                    'scan_time': datetime.now().isoformat(),
                    'total_errors': 0,
                    'errors_by_clan': {},
                    'all_errors': [],
                    'note': 'Все кланы успешно просканированы'
                }
            else:
                # Группируем новые ошибки
                errors_by_clan = {}
                for error in errors:
                    endpoint = error['endpoint']
                    if '/clans/' in endpoint:
                        parts = endpoint.split('/clans/')
                        if len(parts) > 1:
                            clan_tag_encoded = parts[1].split('/')[0]
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
                
                error_data = {
                    'scan_time': datetime.now().isoformat(),
                    'total_errors': len(errors),
                    'errors_by_clan': errors_by_clan,
                    'all_errors': errors,
                    'note': 'Ошибки после повторного сканирования'
                }
                
                logger.info(f"Найдено {len(errors)} новых ошибок")
                logger.info(f"Кланов всё ещё с ошибками: {len(errors_by_clan)}")
            
            # Сохраняем в файл
            with open('404_api_errors.json', 'w', encoding='utf-8') as f:
                json.dump(error_data, f, ensure_ascii=False, indent=2)
            
            logger.info("Файл 404_api_errors.json обновлён")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении ошибок: {e}")


async def main():
    """Точка входа в программу"""
    logger.info("Инициализация обработчика ошибок...")
    
    # Проверка наличия обязательного COC_API_TOKEN
    if not config.COC_API_TOKEN or config.COC_API_TOKEN == '' or config.COC_API_TOKEN == 'WILL_BE_VALIDATED_IN_MAIN':
        logger.error("=" * 80)
        logger.error("ОШИБКА: COC_API_TOKEN не установлен!")
        logger.error("Для работы программы необходим токен API Clash of Clans")
        logger.error("Получите токен на https://developer.clashofclans.com")
        logger.error("Установите его в файле api_tokens.txt или переменной окружения")
        logger.error("=" * 80)
        sys.exit(1)
    
    handler = ErrorHandler()
    await handler.start_rescan()
    
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
