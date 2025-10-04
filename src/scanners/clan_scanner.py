"""
Сканер кланов для поиска и отслеживания войн в различных кланах
Сканирует топ-кланы из различных локаций и лиг для получения информации о войнах
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set
import json

from src.services.database import DatabaseService
from src.services.coc_api import CocApiClient
from src.models.war import WarToSave
from config.config import config

logger = logging.getLogger(__name__)


class ClanScanner:
    """Сервис сканирования кланов для сбора информации о войнах"""
    
    def __init__(self, db_service: DatabaseService, coc_client: CocApiClient):
        self.db_service = db_service
        self.coc_client = coc_client
        
        self.is_running = False
        self.task = None
        
        # Интервал сканирования - 15 минут
        self.scan_interval = 900  # 15 минут в секундах
        
        # Список локаций для сканирования (коды стран/регионов)
        self.location_ids = [
            32000007,  # Europe
            32000008,  # North America
            32000009,  # South America
            32000010,  # Asia
            32000185,  # Russia
            32000038,  # China
            32000113,  # India
            32000094,  # Germany
            32000222,  # United States
            32000006,  # International
        ]
        
        # Кэш отсканированных кланов (тег клана -> время последнего сканирования)
        self.scanned_clans: Dict[str, datetime] = {}
        
        # Минимальный интервал повторного сканирования одного клана (1 час)
        self.rescan_interval = 3600
    
    async def start(self):
        """Запуск сервиса сканирования"""
        if self.is_running:
            logger.warning("[Сканер кланов] Уже запущен")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._scan_loop())
        logger.info("[Сканер кланов] Запущен")
    
    async def stop(self):
        """Остановка сервиса сканирования"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("[Сканер кланов] Остановлен")
    
    async def _scan_loop(self):
        """Основной цикл сканирования"""
        # Первое сканирование сразу после запуска
        try:
            await self._scan_clans()
        except Exception as e:
            logger.error(f"[Сканер кланов] Ошибка при первом сканировании: {e}")
        
        while self.is_running:
            try:
                # Ждем интервал перед следующим сканированием
                await asyncio.sleep(self.scan_interval)
                
                await self._scan_clans()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Сканер кланов] Ошибка в цикле сканирования: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повтором при ошибке
    
    async def _scan_clans(self):
        """Сканирование кланов"""
        logger.info("[Сканер кланов] Начало сканирования")
        
        scanned_count = 0
        wars_found = 0
        
        try:
            # Сканируем кланы по локациям
            for location_id in self.location_ids:
                try:
                    clans = await self._get_top_clans_by_location(location_id)
                    if not clans:
                        continue
                    
                    logger.info(f"[Сканер кланов] Найдено {len(clans)} кланов в локации {location_id}")
                    
                    for clan in clans:
                        clan_tag = clan.get('tag')
                        if not clan_tag:
                            continue
                        
                        # Проверяем, не сканировали ли мы этот клан недавно
                        if not self._should_scan_clan(clan_tag):
                            continue
                        
                        # Сканируем клан на наличие войн
                        war_saved = await self._scan_clan_war(clan_tag)
                        if war_saved:
                            wars_found += 1
                        
                        scanned_count += 1
                        
                        # Обновляем кэш
                        self.scanned_clans[clan_tag] = datetime.now()
                        
                        # Небольшая задержка между запросами
                        await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"[Сканер кланов] Ошибка при сканировании локации {location_id}: {e}")
                    continue
            
            logger.info(f"[Сканер кланов] Завершено. Отсканировано {scanned_count} кланов, найдено {wars_found} новых войн")
            
        except Exception as e:
            logger.error(f"[Сканер кланов] Ошибка при сканировании: {e}")
    
    def _should_scan_clan(self, clan_tag: str) -> bool:
        """Проверка, нужно ли сканировать клан"""
        if clan_tag not in self.scanned_clans:
            return True
        
        last_scan = self.scanned_clans[clan_tag]
        time_since_scan = (datetime.now() - last_scan).total_seconds()
        
        return time_since_scan >= self.rescan_interval
    
    async def _get_top_clans_by_location(self, location_id: int, limit: int = 10) -> List[Dict[Any, Any]]:
        """Получение топ кланов по локации"""
        try:
            async with self.coc_client as client:
                # Используем внутренний метод для получения рейтинга кланов
                endpoint = f"/locations/{location_id}/rankings/clans?limit={limit}"
                data = await client._make_request(endpoint)
                
                if data and 'items' in data:
                    return data['items']
                
        except Exception as e:
            logger.error(f"[Сканер кланов] Ошибка при получении топ кланов локации {location_id}: {e}")
        
        return []
    
    async def _scan_clan_war(self, clan_tag: str) -> bool:
        """Сканирование войны клана"""
        try:
            async with self.coc_client as client:
                war_data = await client.get_clan_current_war(clan_tag)
                
                if not war_data:
                    return False
                
                war_state = war_data.get('state', '')
                
                # Обрабатываем только завершенные войны
                if war_state != 'warEnded':
                    return False
                
                end_time = war_data.get('endTime')
                if not end_time:
                    return False
                
                # Проверяем, не сохранена ли уже эта война
                if await self.db_service.war_exists(end_time):
                    return False
                
                # Анализируем и сохраняем войну
                await self._analyze_and_save_war(war_data, clan_tag)
                
                return True
                
        except Exception as e:
            logger.error(f"[Сканер кланов] Ошибка при сканировании войны клана {clan_tag}: {e}")
            return False
    
    async def _analyze_and_save_war(self, war_data: Dict[Any, Any], clan_tag: str):
        """Анализ и сохранение войны"""
        try:
            clan_data = war_data.get('clan', {})
            opponent_data = war_data.get('opponent', {})
            
            # Основная информация о войне
            end_time = war_data.get('endTime', '')
            opponent_name = opponent_data.get('name', 'Неизвестный противник')
            team_size = len(clan_data.get('members', []))
            clan_stars = clan_data.get('stars', 0)
            opponent_stars = opponent_data.get('stars', 0)
            clan_destruction = clan_data.get('destructionPercentage', 0.0)
            opponent_destruction = opponent_data.get('destructionPercentage', 0.0)
            
            # Подсчет использованных атак
            clan_attacks_used, total_violations, attacks_by_member = self._analyze_attacks(clan_data)
            
            # Определение результата
            result = self._determine_result(clan_stars, opponent_stars)
            
            # Проверка на ЛВК (упрощенная)
            is_cwl_war = False  # Можно улучшить проверку
            
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
                is_cwl_war=is_cwl_war,
                total_violations=total_violations,
                attacks_by_member=attacks_by_member
            )
            
            # Сохранение в базу данных
            success = await self.db_service.save_war(war_to_save)
            
            if success:
                clan_name = clan_data.get('name', clan_tag)
                logger.info(f"[Сканер кланов] Война сохранена: {clan_name} vs {opponent_name} (завершена {end_time})")
            
        except Exception as e:
            logger.error(f"[Сканер кланов] Ошибка при анализе и сохранении войны: {e}")
    
    def _analyze_attacks(self, clan_data: Dict[Any, Any]) -> tuple:
        """Анализ атак клана"""
        members = clan_data.get('members', [])
        total_attacks_used = 0
        total_violations = 0
        attacks_by_member = {}
        
        for member in members:
            member_tag = member.get('tag', '')
            member_attacks = member.get('attacks', [])
            total_attacks_used += len(member_attacks)
            
            # Анализ нарушений (упрощенный алгоритм)
            member_violations = self._analyze_member_violations(member, member_attacks)
            total_violations += member_violations
            
            # Сохранение атак участника
            if member_attacks:
                attacks_by_member[member_tag] = [
                    {
                        'attacker_name': member.get('name', ''),
                        'defender_tag': attack.get('defenderTag', ''),
                        'stars': attack.get('stars', 0),
                        'destruction': attack.get('destructionPercentage', 0.0),
                        'order': attack.get('order', 0),
                        'timestamp': 0,  # API не предоставляет timestamp
                        'is_violation': 0  # Требует дополнительного анализа
                    }
                    for attack in member_attacks
                ]
        
        return total_attacks_used, total_violations, attacks_by_member
    
    def _analyze_member_violations(self, member: Dict[Any, Any], attacks: List[Dict[Any, Any]]) -> int:
        """Анализ нарушений участника (упрощенный)"""
        violations = 0
        
        # Простая проверка: если участник не использовал все атаки
        expected_attacks = 2  # Обычно в КВ каждый участник может атаковать 2 раза
        if len(attacks) < expected_attacks:
            violations += expected_attacks - len(attacks)
        
        return violations
    
    def _determine_result(self, clan_stars: int, opponent_stars: int) -> str:
        """Определение результата войны"""
        if clan_stars > opponent_stars:
            return "win"
        elif clan_stars < opponent_stars:
            return "lose"
        else:
            return "tie"
    
    async def scan_clan_wars_history(self, clan_tag: str) -> int:
        """Сканирование всех войн клана из warlog и добавление их в базу данных
        
        Args:
            clan_tag: Тег клана для сканирования
            
        Returns:
            Количество добавленных войн
        """
        wars_added = 0
        
        try:
            logger.info(f"[Сканер кланов] Начало сканирования истории войн для клана {clan_tag}")
            
            async with self.coc_client as client:
                # Получаем журнал войн клана
                war_log = await client.get_clan_war_log(clan_tag)
                
                if not war_log or 'items' not in war_log:
                    logger.warning(f"[Сканер кланов] Не удалось получить журнал войн для клана {clan_tag}")
                    return 0
                
                wars = war_log.get('items', [])
                logger.info(f"[Сканер кланов] Найдено {len(wars)} войн в журнале клана {clan_tag}")
                
                for war in wars:
                    # Пропускаем войны, которые еще не завершены
                    result = war.get('result')
                    if not result or result == 'none':
                        continue
                    
                    end_time = war.get('endTime')
                    if not end_time:
                        continue
                    
                    # Проверяем, не сохранена ли уже эта война
                    if await self.db_service.war_exists(end_time):
                        continue
                    
                    # Создаем структуру данных, похожую на currentwar
                    # В warlog меньше информации, но достаточно для базовой статистики
                    war_data = {
                        'endTime': end_time,
                        'state': 'warEnded',
                        'clan': {
                            'name': war.get('clan', {}).get('name', ''),
                            'stars': war.get('clan', {}).get('stars', 0),
                            'destructionPercentage': war.get('clan', {}).get('destructionPercentage', 0.0),
                            'members': war.get('clan', {}).get('members', [])
                        },
                        'opponent': {
                            'name': war.get('opponent', {}).get('name', 'Неизвестный противник'),
                            'stars': war.get('opponent', {}).get('stars', 0),
                            'destructionPercentage': war.get('opponent', {}).get('destructionPercentage', 0.0)
                        }
                    }
                    
                    # Анализируем и сохраняем войну
                    await self._analyze_and_save_war(war_data, clan_tag)
                    wars_added += 1
                    
                    # Небольшая задержка между обработкой войн
                    await asyncio.sleep(0.1)
                
                logger.info(f"[Сканер кланов] Добавлено {wars_added} новых войн для клана {clan_tag}")
                return wars_added
                
        except Exception as e:
            logger.error(f"[Сканер кланов] Ошибка при сканировании истории войн клана {clan_tag}: {e}")
            return wars_added

