"""
Архиватор войн - аналог Java WarArchiver
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import json

from database import DatabaseService
from coc_api import CocApiClient, is_war_ended, is_war_in_preparation, is_cwl_active
from models.war import WarToSave
from config import config

logger = logging.getLogger(__name__)


class WarArchiver:
    """Сервис архивации войн и уведомлений"""
    
    def __init__(self, clan_tag: str, db_service: DatabaseService, 
                 coc_client: CocApiClient, bot_instance=None):
        self.clan_tag = clan_tag
        self.db_service = db_service
        self.coc_client = coc_client
        self.bot = bot_instance
        
        self.is_running = False
        self.task = None
        self.notified_war_start_time = None
        self.last_known_war_end_time = None
        
        # Интервалы проверки
        self.check_interval = config.ARCHIVE_CHECK_INTERVAL  # 15 минут
        self.donation_snapshot_interval = config.DONATION_SNAPSHOT_INTERVAL  # 6 часов
        self.last_donation_snapshot = None
    
    async def start(self):
        """Запуск сервиса архивации"""
        if self.is_running:
            logger.warning("Архиватор уже запущен")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._archive_loop())
        logger.info(f"Сервис архивации войн запущен для клана {self.clan_tag}")
    
    async def stop(self):
        """Остановка сервиса архивации"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Сервис архивации войн остановлен")
    
    async def _archive_loop(self):
        """Основной цикл архивации"""
        # При первом запуске проверяем журнал войн на наличие непроцессированных войн
        try:
            await self._check_war_log_for_past_wars()
        except Exception as e:
            logger.error(f"[Архиватор] Ошибка при проверке журнала войн: {e}")
        
        while self.is_running:
            try:
                await self._check_current_war()
                await self._check_donation_snapshots()
                
                # Ждем до следующей проверки
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Архиватор] Ошибка в фоновой задаче: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повтором при ошибке
    
    async def _check_war_log_for_past_wars(self):
        """Проверка журнала войн на наличие непроцессированных войн"""
        logger.info(f"[Архиватор] Проверка журнала войн для клана {self.clan_tag}")
        
        try:
            async with self.coc_client as client:
                war_log = await client.get_clan_war_log(self.clan_tag)
                
                if not war_log or 'items' not in war_log:
                    logger.warning(f"[Архиватор] Журнал войн недоступен для клана {self.clan_tag}")
                    return
                
                wars = war_log.get('items', [])
                logger.info(f"[Архиватор] Найдено {len(wars)} войн в журнале")
                
                # Обрабатываем войны из журнала (от новых к старым)
                processed_count = 0
                for war_entry in wars:
                    # Проверяем, что война завершена
                    if war_entry.get('result') not in ['win', 'lose', 'tie']:
                        continue
                    
                    end_time = war_entry.get('endTime')
                    if not end_time:
                        continue
                    
                    # Проверяем, не сохранена ли уже эта война
                    if await self.db_service.war_exists(end_time):
                        continue
                    
                    # Получаем информацию о войне из журнала
                    clan_data = war_entry.get('clan', {})
                    opponent_data = war_entry.get('opponent', {})
                    
                    if not clan_data or not opponent_data:
                        continue
                    
                    # Собираем информацию о войне
                    opponent_name = opponent_data.get('name', 'Неизвестный противник')
                    team_size = war_entry.get('teamSize', len(clan_data.get('members', [])))
                    clan_stars = clan_data.get('stars', 0)
                    opponent_stars = opponent_data.get('stars', 0)
                    clan_destruction = clan_data.get('destructionPercentage', 0.0)
                    opponent_destruction = opponent_data.get('destructionPercentage', 0.0)
                    
                    # Подсчет использованных атак и анализ атак
                    clan_attacks_used, total_violations, attacks_by_member = self._analyze_attacks(clan_data)
                    
                    # Определение результата
                    result = war_entry.get('result', self._determine_result(clan_stars, opponent_stars))
                    
                    # Проверяем, является ли война ЛВК (упрощенная проверка по журналу)
                    # В журнале войн нет прямой информации о ЛВК, используем эвристику
                    is_cwl_war = False  # В журнале обычно ЛВК войны не отображаются, но можем проверить
                    
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
                        processed_count += 1
                        logger.info(f"[Архиватор] Война против {opponent_name} (завершена {end_time}) добавлена из журнала")
                
                if processed_count > 0:
                    logger.info(f"[Архиватор] Обработано {processed_count} войн из журнала")
                else:
                    logger.info(f"[Архиватор] Все войны из журнала уже обработаны")
                    
        except Exception as e:
            logger.error(f"[Архиватор] Ошибка при обработке журнала войн: {e}")
    
    async def _check_current_war(self):
        """Проверка текущей войны"""
        logger.info(f"[Архиватор] Проверка текущей войны для клана {self.clan_tag}")
        
        async with self.coc_client as client:
            current_war = await client.get_clan_current_war(self.clan_tag)
            
            if not current_war:
                logger.warning(f"[Архиватор] Не удалось получить информацию о текущей войне для {self.clan_tag}")
                return
            
            war_state = current_war.get('state', '')
            
            # Проверяем на уведомления о начале войны
            if war_state == 'preparation':
                await self._check_war_start_notification(current_war)
            
            # Проверяем завершенные войны
            elif war_state == 'warEnded':
                await self._check_completed_war(current_war)
    
    async def _check_war_start_notification(self, war_data: Dict[Any, Any]):
        """Проверка и отправка уведомлений о начале войны"""
        start_time_str = war_data.get('startTime')
        if not start_time_str:
            return
        
        # Если уже отправляли уведомление для этой войны
        if start_time_str == self.notified_war_start_time:
            return
        
        try:
            # Парсим время начала войны
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            
            # Проверяем, что война начнется менее чем через час
            time_until_start = start_time - now
            if time_until_start <= timedelta(hours=1) and time_until_start > timedelta(0):
                await self._send_war_start_notification(war_data)
                self.notified_war_start_time = start_time_str
                
        except Exception as e:
            logger.error(f"[Архиватор] Ошибка при проверке уведомления о начале войны: {e}")
    
    async def _send_war_start_notification(self, war_data: Dict[Any, Any]):
        """Отправка уведомления о начале войны"""
        if not self.bot:
            return
        
        try:
            opponent_name = war_data.get('opponent', {}).get('name', 'Неизвестный противник')
            clan_size = len(war_data.get('clan', {}).get('members', []))
            opponent_size = len(war_data.get('opponent', {}).get('members', []))
            
            message_text = (
                "⚔️ *Внимание!* Скоро начнется клановая война!\n\n"
                f"*Противник:* {opponent_name}\n"
                f"*Размер:* {clan_size} на {opponent_size}\n"
                f"*Начало примерно через:* меньше часа."
            )
            
            # Получаем список подписанных пользователей
            subscribed_users = await self.db_service.get_subscribed_users()
            
            logger.info(f"[Архиватор] Скоро начнется война! Отправка уведомлений {len(subscribed_users)} пользователям...")
            
            # Отправляем уведомления
            for user_id in subscribed_users:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message_text,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"[Архиватор] Ошибка при отправке уведомления пользователю {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"[Архиватор] Ошибка при отправке уведомлений о начале войны: {e}")
    
    async def _check_completed_war(self, war_data: Dict[Any, Any]):
        """Проверка и сохранение завершенной войны"""
        end_time = war_data.get('endTime')
        if not end_time:
            return
        
        # Проверяем, не сохраняли ли мы уже эту войну
        if await self.db_service.war_exists(end_time):
            return
        
        # Если это та же война, что мы уже обработали
        if end_time == self.last_known_war_end_time:
            return
        
        logger.info(f"[Архиватор] Обнаружена новая завершенная война: {end_time}")
        
        try:
            # Проверяем, является ли это войной ЛВК
            is_cwl_war = await self._is_cwl_war()
            
            # Анализируем и сохраняем войну
            await self._analyze_and_save_war(war_data, is_cwl_war)
            self.last_known_war_end_time = end_time
            
        except Exception as e:
            logger.error(f"[Архиватор] Ошибка при обработке завершенной войны: {e}")
    
    async def _is_cwl_war(self) -> bool:
        """Проверка, является ли текущая война частью ЛВК"""
        try:
            async with self.coc_client as client:
                league_group = await client.get_clan_war_league_group(self.clan_tag)
                return is_cwl_active(league_group)
        except Exception as e:
            logger.error(f"[Архиватор] Ошибка при проверке ЛВК: {e}")
            return False
    
    async def _analyze_and_save_war(self, war_data: Dict[Any, Any], is_cwl_war: bool):
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
            
            # Подсчет использованных атак и нарушений
            clan_attacks_used, total_violations, attacks_by_member = self._analyze_attacks(clan_data)
            
            # Определение результата
            result = self._determine_result(clan_stars, opponent_stars)
            
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
                war_type = "ЛВК" if is_cwl_war else "КВ"
                logger.info(f"[Архиватор] Война против {opponent_name} сохранена. Является {war_type}: {is_cwl_war}")
            else:
                logger.error(f"[Архиватор] Ошибка при сохранении войны против {opponent_name}")
                
        except Exception as e:
            logger.error(f"[Архиватор] Ошибка при анализе и сохранении войны: {e}")
    
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
        # Здесь можно реализовать более сложную логику анализа нарушений
        # Например, проверка атак не по порядку, пропущенные атаки и т.д.
        
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
    
    async def _check_donation_snapshots(self):
        """Проверка и создание снимков донатов"""
        now = datetime.now()
        
        # Проверяем каждые 6 часов
        if (self.last_donation_snapshot is None or 
            (now - self.last_donation_snapshot).total_seconds() >= self.donation_snapshot_interval):
            
            try:
                async with self.coc_client as client:
                    clan_data = await client.get_clan_info(self.clan_tag)
                    
                    if clan_data and 'memberList' in clan_data:
                        await self.db_service.save_donation_snapshot(
                            clan_data['memberList'], 
                            now.isoformat()
                        )
                        self.last_donation_snapshot = now
                        logger.info("[Архиватор] Снимок донатов сохранен.")
                        
            except Exception as e:
                logger.error(f"[Архиватор] Ошибка при сохранении снимка донатов: {e}")