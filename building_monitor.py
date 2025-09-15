"""
Трекер зданий для отслеживания улучшений - премиум функция
"""
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from database import DatabaseService
from coc_api import CocApiClient
from models.building import BuildingSnapshot, BuildingUpgrade, BuildingTracker
from config import config

logger = logging.getLogger(__name__)


class BuildingMonitor:
    """Сервис мониторинга улучшений зданий для премиум пользователей"""
    
    def __init__(self, db_service: DatabaseService, coc_client: CocApiClient, bot_instance=None):
        self.db_service = db_service
        self.coc_client = coc_client
        self.bot = bot_instance
        
        self.is_running = False
        self.task = None
        
        # Интервал проверки - каждые 5 минут
        self.check_interval = 300  # 5 минут в секундах
        
        # Словарь для перевода названий зданий на русский
        self.building_names_ru = {
            "Town Hall": "Ратуша",
            "Army Camp": "Казарма",
            "Barracks": "Учебные казармы",
            "Laboratory": "Лаборатория",
            "Spell Factory": "Фабрика заклинаний",
            "Clan Castle": "Замок клана",
            "Gold Mine": "Золотая шахта",
            "Elixir Collector": "Накопитель эликсира",
            "Dark Elixir Drill": "Бур темного эликсира",
            "Gold Storage": "Хранилище золота",
            "Elixir Storage": "Хранилище эликсира",
            "Dark Elixir Storage": "Хранилище темного эликсира",
            "Cannon": "Пушка",
            "Archer Tower": "Башня лучниц",
            "Mortar": "Мортира",
            "Air Defense": "Воздушная защита",
            "Wizard Tower": "Башня магов",
            "Air Sweeper": "Воздушная метла",
            "Hidden Tesla": "Скрытая тесла",
            "Bomb Tower": "Башня-бомба",
            "X-Bow": "Адский лук",
            "Inferno Tower": "Башня ада",
            "Eagle Artillery": "Орлиная артиллерия",
            "Scattershot": "Разброс",
            "Builder's Hut": "Хижина строителя",
            "Barbarian King": "Король варваров",
            "Archer Queen": "Королева лучниц",
            "Grand Warden": "Великий хранитель",
            "Royal Champion": "Королевский чемпион"
        }
    
    async def start(self):
        """Запуск мониторинга зданий"""
        if self.is_running:
            logger.warning("Монитор зданий уже запущен")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._monitoring_loop())
        logger.info("Сервис мониторинга зданий запущен")
    
    async def stop(self):
        """Остановка мониторинга зданий"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Сервис мониторинга зданий остановлен")
    
    async def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        while self.is_running:
            try:
                await self._check_all_trackers()
                
                # Ждем до следующей проверки (5 минут)
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Монитор зданий] Ошибка в фоновой задаче: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повтором при ошибке
    
    async def _check_all_trackers(self):
        """Проверка всех активных отслеживателей"""
        try:
            trackers = await self.db_service.get_active_building_trackers()
            logger.info(f"[Монитор зданий] Проверка {len(trackers)} активных отслеживателей")
            
            for tracker in trackers:
                # Проверяем, что у пользователя есть активная премиум подписка
                subscription = await self.db_service.get_subscription(tracker.telegram_id)
                if not subscription or not subscription.is_active or subscription.is_expired():
                    logger.info(f"Отключение отслеживания для пользователя {tracker.telegram_id} - нет активной подписки")
                    await self._deactivate_tracker(tracker.telegram_id)
                    continue
                
                await self._check_player_buildings(tracker)
                
        except Exception as e:
            logger.error(f"[Монитор зданий] Ошибка при проверке отслеживателей: {e}")
    
    async def _check_player_buildings(self, tracker: BuildingTracker):
        """Проверка зданий конкретного игрока"""
        try:
            # Получаем текущую информацию о игроке
            async with self.coc_client as client:
                player_data = await client.get_player_info(tracker.player_tag)
                
                if not player_data:
                    logger.warning(f"Не удалось получить данные игрока {tracker.player_tag}")
                    return
            
            # Получаем последний снимок зданий
            last_snapshot = await self.db_service.get_latest_building_snapshot(tracker.player_tag)
            
            if not last_snapshot:
                # Создаем первый снимок
                await self._create_initial_snapshot(tracker.player_tag, player_data)
                logger.info(f"Создан первый снимок зданий для игрока {tracker.player_tag}")
                return
            
            # Сравниваем здания
            upgrades = await self._compare_buildings(last_snapshot, player_data)
            
            if upgrades:
                # Отправляем уведомления об улучшениях
                await self._send_upgrade_notifications(tracker.telegram_id, upgrades)
                
                # Сохраняем новый снимок
                await self._create_snapshot(tracker.player_tag, player_data)
            
            # Обновляем время последней проверки
            now = datetime.now().isoformat()
            await self.db_service.update_tracker_last_check(tracker.telegram_id, now)
            
        except Exception as e:
            logger.error(f"[Монитор зданий] Ошибка при проверке игрока {tracker.player_tag}: {e}")
    
    async def _create_initial_snapshot(self, player_tag: str, player_data: Dict[Any, Any]):
        """Создание первого снимка зданий"""
        await self._create_snapshot(player_tag, player_data)
    
    async def _create_snapshot(self, player_tag: str, player_data: Dict[Any, Any]):
        """Создание снимка состояния зданий"""
        try:
            buildings_data = {}
            
            # Извлекаем данные о зданиях (включая ратушу)
            if 'townHallLevel' in player_data:
                buildings_data['Town Hall'] = player_data['townHallLevel']
            
            # Извлекаем данные о героях
            if 'heroes' in player_data:
                for hero in player_data['heroes']:
                    if 'name' in hero and 'level' in hero:
                        buildings_data[hero['name']] = hero['level']
            
            # Извлекаем данные о войсках (войска могут улучшаться в лаборатории)
            if 'troops' in player_data:
                for troop in player_data['troops']:
                    if 'name' in troop and 'level' in troop:
                        buildings_data[f"{troop['name']} (войска)"] = troop['level']
            
            # Извлекаем данные о заклинаниях
            if 'spells' in player_data:
                for spell in player_data['spells']:
                    if 'name' in spell and 'level' in spell:
                        buildings_data[f"{spell['name']} (заклинание)"] = spell['level']
            
            snapshot = BuildingSnapshot(
                player_tag=player_tag,
                snapshot_time=datetime.now().isoformat(),
                buildings_data=json.dumps(buildings_data)
            )
            
            await self.db_service.save_building_snapshot(snapshot)
            
        except Exception as e:
            logger.error(f"Ошибка при создании снимка зданий: {e}")
    
    async def _compare_buildings(self, last_snapshot: BuildingSnapshot, current_data: Dict[Any, Any]) -> List[BuildingUpgrade]:
        """Сравнение зданий и поиск улучшений"""
        upgrades = []
        
        try:
            # Загружаем данные из последнего снимка
            old_buildings = json.loads(last_snapshot.buildings_data)
            
            # Создаем текущий снимок для сравнения
            current_buildings = {}
            
            # Ратуша
            if 'townHallLevel' in current_data:
                current_buildings['Town Hall'] = current_data['townHallLevel']
            
            # Герои
            if 'heroes' in current_data:
                for hero in current_data['heroes']:
                    if 'name' in hero and 'level' in hero:
                        current_buildings[hero['name']] = hero['level']
            
            # Войска
            if 'troops' in current_data:
                for troop in current_data['troops']:
                    if 'name' in troop and 'level' in troop:
                        current_buildings[f"{troop['name']} (войска)"] = troop['level']
            
            # Заклинания
            if 'spells' in current_data:
                for spell in current_data['spells']:
                    if 'name' in spell and 'level' in spell:
                        current_buildings[f"{spell['name']} (заклинание)"] = spell['level']
            
            # Сравниваем уровни
            for building_name, current_level in current_buildings.items():
                old_level = old_buildings.get(building_name, 0)
                
                if current_level > old_level:
                    upgrades.append(BuildingUpgrade(
                        building_name=building_name,
                        old_level=old_level,
                        new_level=current_level
                    ))
            
        except Exception as e:
            logger.error(f"Ошибка при сравнении зданий: {e}")
        
        return upgrades
    
    async def _send_upgrade_notifications(self, telegram_id: int, upgrades: List[BuildingUpgrade]):
        """Отправка уведомлений об улучшениях"""
        if not self.bot:
            return
        
        try:
            for upgrade in upgrades:
                # Переводим название на русский
                building_name_ru = self.building_names_ru.get(upgrade.building_name, upgrade.building_name)
                
                message = (
                    f"🏗️ <b>Улучшение завершено!</b>\n\n"
                    f"🔨 {building_name_ru} улучшен с {upgrade.old_level} на {upgrade.new_level} уровень!\n\n"
                    f"🎉 Поздравляем с успешным улучшением!"
                )
                
                await self.bot.send_message(
                    chat_id=telegram_id,
                    text=message,
                    parse_mode='HTML'
                )
                
                logger.info(f"Отправлено уведомление об улучшении {building_name_ru} пользователю {telegram_id}")
                
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомлений: {e}")
    
    async def activate_tracking(self, telegram_id: int, player_tag: str) -> bool:
        """Активация отслеживания зданий для пользователя"""
        try:
            # Проверяем, что у пользователя есть премиум подписка
            subscription = await self.db_service.get_subscription(telegram_id)
            if not subscription or not subscription.is_active or subscription.is_expired():
                return False
            
            tracker = BuildingTracker(
                telegram_id=telegram_id,
                player_tag=player_tag,
                is_active=True,
                created_at=datetime.now().isoformat()
            )
            
            success = await self.db_service.save_building_tracker(tracker)
            if success:
                logger.info(f"Активировано отслеживание зданий для пользователя {telegram_id}, игрок {player_tag}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка при активации отслеживания: {e}")
            return False
    
    async def _deactivate_tracker(self, telegram_id: int):
        """Деактивация отслеживания"""
        try:
            tracker = await self.db_service.get_building_tracker(telegram_id)
            if tracker:
                tracker.is_active = False
                await self.db_service.save_building_tracker(tracker)
                logger.info(f"Отслеживание зданий деактивировано для пользователя {telegram_id}")
                
        except Exception as e:
            logger.error(f"Ошибка при деактивации отслеживания: {e}")
    
    async def deactivate_tracking(self, telegram_id: int) -> bool:
        """Деактивация отслеживания зданий пользователем"""
        try:
            await self._deactivate_tracker(telegram_id)
            return True
        except Exception as e:
            logger.error(f"Ошибка при деактивации отслеживания пользователем: {e}")
            return False
    
    async def is_tracking_active(self, telegram_id: int) -> bool:
        """Проверка активности отслеживания для пользователя"""
        try:
            tracker = await self.db_service.get_building_tracker(telegram_id)
            return tracker is not None and tracker.is_active
        except Exception as e:
            logger.error(f"Ошибка при проверке статуса отслеживания: {e}")
            return False