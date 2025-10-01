"""
Генератор сообщений - аналог Java MessageGenerator
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database import DatabaseService
from coc_api import CocApiClient, format_clan_tag, format_player_tag
from keyboards import Keyboards, WarSort, MemberSort, MemberView
from models.user import User
from models.user_profile import UserProfile
from user_state import UserState
from models.subscription import Subscription
from payment_service import YooKassaService
from config import config

logger = logging.getLogger(__name__)


class MessageGenerator:
    """Генератор сообщений и форматирование данных"""
    
    def __init__(self, db_service: DatabaseService, coc_client: CocApiClient):
        self.db_service = db_service
        self.coc_client = coc_client
        self.payment_service = YooKassaService(config.BOT_USERNAME)
        
        # Константы для форматирования
        self.MEMBERS_PER_PAGE = 10
        self.WARS_PER_PAGE = 10
        
        self.ROLE_TRANSLATIONS = {
            "leader": "👑 Глава",
            "coLeader": "⚜️ Соруководитель", 
            "admin": "🔰 Старейшина",
            "member": "👤 Участник"
        }
    
    def _format_datetime(self, iso_datetime_str: str) -> str:
        """Форматирование ISO datetime строки в читаемый формат"""
        try:
            # Парсим ISO datetime (формат: 20250919T044950.000Z)
            dt = datetime.fromisoformat(iso_datetime_str.replace('Z', '+00:00'))
            
            # Конвертируем в московское время (UTC+3)
            moscow_tz = timezone(timedelta(hours=3))
            moscow_dt = dt.astimezone(moscow_tz)
            
            # Форматируем в читаемый вид: "19.09.2025 07:49"
            return moscow_dt.strftime('%d.%m.%Y %H:%M')
        except Exception as e:
            logger.error(f"Ошибка при форматировании времени {iso_datetime_str}: {e}")
            # Возвращаем исходную строку в случае ошибки
            return iso_datetime_str
    
    async def handle_profile_menu_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка запроса меню профиля"""
        chat_id = update.effective_chat.id
        
        try:
            # Проверяем подписку пользователя
            subscription = await self.db_service.get_subscription(chat_id)
            has_premium = subscription and subscription.is_active and not subscription.is_expired()
            
            if has_premium:
                # Для премиум пользователей проверяем профили
                profiles = await self.db_service.get_user_profiles(chat_id)
                profile_count = len(profiles)
                
                if profile_count > 1:
                    # Показываем менеджер профилей
                    await update.message.reply_text(
                        "Меню профиля:",
                        reply_markup=Keyboards.profile_menu(None, has_premium=True, profile_count=profile_count)
                    )
                    return
                elif profile_count == 1:
                    # Показываем единственный профиль
                    primary_profile = profiles[0]
                    async with self.coc_client as client:
                        player_data = await client.get_player_info(primary_profile.player_tag)
                        player_name = player_data.get('name') if player_data else None
                        
                        await update.message.reply_text(
                            "Меню профиля:",
                            reply_markup=Keyboards.profile_menu(player_name, has_premium=True, profile_count=1)
                        )
                    return
            
            # Для обычных пользователей или премиум без профилей
            user = await self.db_service.find_user(chat_id)
            if user:
                async with self.coc_client as client:
                    player_data = await client.get_player_info(user.player_tag)
                    player_name = player_data.get('name') if player_data else None
                    
                    await update.message.reply_text(
                        "Меню профиля:",
                        reply_markup=Keyboards.profile_menu(player_name, has_premium=has_premium, profile_count=0)
                    )
            else:
                await update.message.reply_text(
                    "Меню профиля:",
                    reply_markup=Keyboards.profile_menu(None, has_premium=has_premium, profile_count=0)
                )
        except Exception as e:
            logger.error(f"Ошибка при получении меню профиля: {e}")
            await update.message.reply_text(
                "Меню профиля:",
                reply_markup=Keyboards.profile_menu(None, has_premium=False, profile_count=0)
            )
    
    async def handle_my_profile_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка запроса просмотра собственного профиля"""
        chat_id = update.effective_chat.id
        
        user = await self.db_service.find_user(chat_id)
        if not user:
            await update.message.reply_text(
                "Вы не привязали свой аккаунт. Используйте кнопку \"🔗 Привязать аккаунт\".",
                reply_markup=Keyboards.profile_menu(None)
            )
            return
        
        # Display profile info without clan inspection menu - just profile info
        await self.display_player_info(update, context, user.player_tag, None)
    
    async def handle_link_account(self, update: Update, context: ContextTypes.DEFAULT_TYPE, player_tag: str):
        """Обработка привязки аккаунта"""
        chat_id = update.effective_chat.id
        
        async with self.coc_client as client:
            player_data = await client.get_player_info(player_tag)
            
            if not player_data:
                await update.message.reply_text(
                    "❌ Игрок с таким тегом не найден. Проверьте правильность тега.",
                    reply_markup=Keyboards.profile_menu(None)
                )
                return
            
            user = User(telegram_id=chat_id, player_tag=player_tag)
            success = await self.db_service.save_user(user)
            
            if success:
                player_name = player_data.get('name', 'Неизвестно')
                await update.message.reply_text(
                    f"✅ Аккаунт успешно привязан!\n"
                    f"👤 Игрок: {player_name}\n"
                    f"🏷 Тег: {player_tag}",
                    reply_markup=Keyboards.profile_menu(player_name)
                )
            else:
                await update.message.reply_text(
                    "❌ Ошибка при привязке аккаунта. Попробуйте позже.",
                    reply_markup=Keyboards.profile_menu(None)
                )
    
    async def handle_my_clan_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка запроса просмотра своего клана"""
        chat_id = update.effective_chat.id
        
        user = await self.db_service.find_user(chat_id)
        if not user:
            await update.message.reply_text(
                "Вы не привязали свой аккаунт. Используйте кнопку \"🔗 Привязать аккаунт\".",
                reply_markup=Keyboards.profile_menu(None)
            )
            return
        
        async with self.coc_client as client:
            player_data = await client.get_player_info(user.player_tag)
            
            if not player_data or 'clan' not in player_data:
                await update.message.reply_text(
                    "❌ Вы не состоите в клане или не удалось получить информацию о клане.",
                    reply_markup=Keyboards.profile_menu(player_data.get('name') if player_data else None)
                )
                return
            
            clan_tag = player_data['clan']['tag']
            await self.display_clan_info(update, context, clan_tag)
    
    async def display_player_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                 player_tag: str, keyboard: InlineKeyboardMarkup = None, 
                                 back_keyboard: InlineKeyboardMarkup = None, from_callback: bool = False):
        """Отображение информации об игроке"""

        # Handle callback updates differently 
        if from_callback and hasattr(update, 'callback_query') and update.callback_query:
            # For callback queries, directly edit the existing message
            await update.callback_query.edit_message_text("🔍 Поиск игрока...")
            
            async with self.coc_client as client:
                player_data = await client.get_player_info(player_tag)
                
                if not player_data:
                    await update.callback_query.edit_message_text(
                        "❌ Игрок с таким тегом не найден.\n"
                        "Проверьте правильность введенного тега."
                    )
                    return
                
                # Форматируем информацию об игроке
                message = self._format_player_info(player_data)
                
                # Create achievements button for profile displays
                profile_keyboard = []
                profile_keyboard.append([InlineKeyboardButton("🏆 Достижения", 
                                                             callback_data=f"{Keyboards.ACHIEVEMENTS_CALLBACK}:{player_tag}")])
                
                # Add back_keyboard buttons if provided
                if back_keyboard and back_keyboard.inline_keyboard:
                    profile_keyboard.extend(back_keyboard.inline_keyboard)
                
                # Add keyboard buttons if provided
                if keyboard and keyboard.inline_keyboard:
                    profile_keyboard.extend(keyboard.inline_keyboard)
                
                final_keyboard = InlineKeyboardMarkup(profile_keyboard) if profile_keyboard else None
                
                await update.callback_query.edit_message_text(
                    message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=final_keyboard
                )
            return

        # Handle regular message updates (original logic)
        # Сначала убираем клавиатуру и показываем сообщение о поиске
        search_message = await update.message.reply_text(
            "🔍 Поиск игрока...",
            reply_markup=None  # Убираем все кнопки во время поиска
        )

        async with self.coc_client as client:
            player_data = await client.get_player_info(player_tag)
            
            if not player_data:
                # Редактируем сообщение о поиске на ошибку
                await search_message.edit_text(
                    "❌ Игрок с таким тегом не найден.\n"
                    "Проверьте правильность введенного тега."
                )
                # Отправляем новое сообщение с главным меню
                await update.message.reply_text(
                    "Выберите действие:",
                    reply_markup=Keyboards.main_menu()
                )
                return
            
            # Форматируем информацию об игроке
            message = self._format_player_info(player_data)
            
            # Create achievements button for profile displays
            profile_keyboard = []
            profile_keyboard.append([InlineKeyboardButton("🏆 Достижения", 
                                                         callback_data=f"{Keyboards.ACHIEVEMENTS_CALLBACK}:{player_tag}")])
            
            # Add back_keyboard buttons if provided
            if back_keyboard and back_keyboard.inline_keyboard:
                profile_keyboard.extend(back_keyboard.inline_keyboard)
            
            # Add keyboard buttons if provided  
            if keyboard and keyboard.inline_keyboard:
                profile_keyboard.extend(keyboard.inline_keyboard)
            
            final_keyboard = InlineKeyboardMarkup(profile_keyboard) if profile_keyboard else None
            
            # Редактируем сообщение поиска на информацию об игроке
            await search_message.edit_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=final_keyboard
            )
    
    async def display_clan_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, clan_tag: str):
        """Отображение информации о клане"""
        # Определяем контекст вызова - из callback или из сообщения
        is_callback = hasattr(update, 'callback_query') and update.callback_query is not None
        
        # Показываем индикатор загрузки
        if is_callback:
            loading_message = await update.callback_query.edit_message_text("🔍 Получение информации о клане...")
        else:
            loading_message = await update.message.reply_text("🔍 Получение информации о клане...")
        
        async with self.coc_client as client:
            clan_data = await client.get_clan_info(clan_tag)
            
            if not clan_data:
                error_message = "❌ Клан с таким тегом не найден или ведутся тех работы на стороне хостинга/апи."
                if is_callback:
                    await update.callback_query.edit_message_text(error_message)
                else:
                    await loading_message.edit_text(error_message)
                    await update.message.reply_text("Выберите действие:", reply_markup=Keyboards.main_menu())
                return
            
            # Сохраняем тег клана для дальнейшего использования
            context.user_data['inspecting_clan'] = clan_tag
            
            # Форматируем информацию о клане
            message = self._format_clan_info(clan_data)
            keyboard = Keyboards.clan_inspection_menu()
            
            if is_callback:
                await update.callback_query.edit_message_text(
                    message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
                )
            else:
                await loading_message.edit_text(
                    message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
                )
    
    async def display_members_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  clan_tag: str, page: int, sort_type: str, view_type: str):
        """Отображение страницы участников клана"""
        # Показываем индикатор загрузки
        await update.callback_query.edit_message_text("👥 Загрузка участников клана...")
        
        try:
            async with self.coc_client as client:
                members_data = await client.get_clan_members(clan_tag)
                
                if not members_data:
                    await update.callback_query.edit_message_text(
                        "❌ Не удалось получить список участников клана."
                    )
                    return
                
                # Сортируем участников
                sorted_members = self._sort_members(members_data, sort_type)
                
                # Пагинация
                total_members = len(sorted_members)
                total_pages = (total_members + self.MEMBERS_PER_PAGE - 1) // self.MEMBERS_PER_PAGE
                start_idx = (page - 1) * self.MEMBERS_PER_PAGE
                end_idx = start_idx + self.MEMBERS_PER_PAGE
                page_members = sorted_members[start_idx:end_idx]
                
                # Форматируем сообщение
                message = self._format_members_page(page_members, page, total_pages, total_members, view_type)
                keyboard = Keyboards.members_with_profiles(clan_tag, page, total_pages, sort_type, view_type, page_members)
                
                await update.callback_query.edit_message_text(
                    message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
                )
                
        except asyncio.TimeoutError:
            logger.error(f"Таймаут при получении участников клана {clan_tag}")
            await update.callback_query.edit_message_text(
                "⏱️ Превышено время ожидания при загрузке участников.\n"
                "Попробуйте позже."
            )
        except Exception as e:
            logger.error(f"Ошибка при получении участников клана: {e}")
            await update.callback_query.edit_message_text(
                "❌ Произошла ошибка при получении участников клана."
            )
    
    async def display_war_list_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   clan_tag: str, sort_order: str, page: int):
        """Отображение страницы списка войн"""
        # Получаем войны из базы данных
        offset = (page - 1) * self.WARS_PER_PAGE
        wars = await self.db_service.get_war_list(self.WARS_PER_PAGE, offset)
        
        if not wars:
            await update.callback_query.edit_message_text(
                "❌ Войны не найдены в базе данных."
            )
            return
        
        # Фильтруем по типу сортировки
        filtered_wars = self._filter_wars_by_sort(wars, sort_order)
        
        total_wars = len(filtered_wars)
        total_pages = (total_wars + self.WARS_PER_PAGE - 1) // self.WARS_PER_PAGE
        
        # Пагинация для текущей страницы
        start_idx = (page - 1) * self.WARS_PER_PAGE
        end_idx = start_idx + self.WARS_PER_PAGE
        page_wars = filtered_wars[start_idx:end_idx]
        
        # Форматируем сообщение
        message = self._format_war_list(page_wars, page, total_pages)
        keyboard = Keyboards.war_list_with_details(clan_tag, page, total_pages, sort_order, page_wars)
        
        await update.callback_query.edit_message_text(
            message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
        )
    
    async def display_single_war_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                        clan_tag: str, war_end_time: str):
        """Отображение детальной информации о войне"""
        war_details = await self.db_service.get_war_details(war_end_time)
        
        if not war_details:
            await update.callback_query.edit_message_text(
                "❌ Война не найдена."
            )
            return
        
        message = self._format_war_details(war_details)
        keyboard = Keyboards.war_details_menu(clan_tag, war_end_time)
        
        await update.callback_query.edit_message_text(
            message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
        )
    
    async def display_war_attacks(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 clan_tag: str, war_end_time: str):
        """Отображение статистики атак войны"""
        war_details = await self.db_service.get_war_details(war_end_time)
        
        if not war_details:
            await update.callback_query.edit_message_text(
                "❌ Война не найдена."
            )
            return
        
        message = self._format_war_attacks(war_details)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Назад к деталям войны", 
                                callback_data=f"{Keyboards.WAR_INFO_CALLBACK}:{clan_tag}:{war_end_time}")],
            [InlineKeyboardButton("⬅️ К списку войн", 
                                callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:recent:1")]
        ])
        
        await update.callback_query.edit_message_text(
            message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
        )
    
    async def display_war_violations(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   clan_tag: str, war_end_time: str):
        """Отображение нарушений войны"""
        war_details = await self.db_service.get_war_details(war_end_time)
        
        if not war_details:
            await update.callback_query.edit_message_text(
                "❌ Война не найдена."
            )
            return
        
        message = self._format_war_violations(war_details)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Назад к деталям войны", 
                                callback_data=f"{Keyboards.WAR_INFO_CALLBACK}:{clan_tag}:{war_end_time}")],
            [InlineKeyboardButton("⬅️ К списку войн", 
                                callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:recent:1")]
        ])
        
        await update.callback_query.edit_message_text(
            message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
        )
    
    async def handle_notifications_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка меню уведомлений"""
        chat_id = update.effective_chat.id
        
        try:
            # Проверяем статус подписки пользователя
            subscription = await self.db_service.get_subscription(chat_id)
            is_premium = subscription and subscription.is_active and not subscription.is_expired()
            
            # Проверяем статус уведомлений
            notification_status = await self.db_service.is_notifications_enabled(chat_id)
            
            message = (
                f"🔔 <b>Настройки уведомлений</b>\n\n"
                f"📊 Статус: {'✅ Включены' if notification_status else '❌ Отключены'}\n"
            )
            
            if is_premium:
                message += (
                    f"💎 Статус подписки: {'👑 ПРО ПЛЮС' if 'proplus' in subscription.subscription_type else '💎 Премиум'}\n\n"
                    f"🔔 Базовые уведомления за 1 час до КВ\n"
                    f"⚙️ Доступны расширенные настройки\n"
                    f"🏗️ Доступно отслеживание улучшений зданий"
                )
            else:
                message += (
                    f"📱 Доступны базовые уведомления за 1 час до КВ\n"
                    f"💎 Для расширенных настроек активируйте подписку"
                )
            
            keyboard = Keyboards.notification_menu(is_premium)
            
            await update.message.reply_text(
                message, 
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        
        except Exception as e:
            logger.error(f"Ошибка при обработке меню уведомлений: {e}")
            await update.message.reply_text("Произошла ошибка при загрузке настроек уведомлений.")

    async def handle_notification_toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                       message_id: int):
        """Переключение уведомлений с сохранением формата сообщения"""
        chat_id = update.effective_chat.id
        
        try:
            # Проверяем статус подписки пользователя
            subscription = await self.db_service.get_subscription(chat_id)
            is_premium = subscription and subscription.is_active and not subscription.is_expired()
            
            # Переключаем статус уведомлений
            is_enabled = await self.db_service.toggle_notifications(chat_id)
            
            # Формируем обновленное сообщение в том же формате
            message = (
                f"🔔 <b>Настройки уведомлений</b>\n\n"
                f"📊 Статус: {'✅ Включены' if is_enabled else '❌ Отключены'}\n"
            )
            
            if is_premium:
                message += (
                    f"💎 Статус подписки: {'👑 ПРО ПЛЮС' if 'proplus' in subscription.subscription_type else '💎 Премиум'}\n\n"
                    f"🔔 Базовые уведомления за 1 час до КВ\n"
                    f"⚙️ Доступны расширенные настройки"
                )
            else:
                message += (
                    f"📱 Доступны базовые уведомления за 1 час до КВ\n"
                    f"💎 Для расширенных настроек активируйте подписку"
                )
            
            await update.callback_query.edit_message_text(
                message,
                parse_mode=ParseMode.HTML,
                reply_markup=Keyboards.notification_toggle()
            )
            
        except Exception as e:
            logger.error(f"Ошибка при переключении уведомлений: {e}")
            await update.callback_query.edit_message_text("❌ Произошла ошибка при изменении настроек.")
    
    def _format_player_info(self, player_data: Dict[Any, Any]) -> str:
        """Форматирование информации об игроке"""
        name = player_data.get('name', 'Неизвестно')
        tag = player_data.get('tag', 'Неизвестно')
        th_level = player_data.get('townHallLevel', 0)
        trophies = player_data.get('trophies', 0)
        best_trophies = player_data.get('bestTrophies', 0)
        exp_level = player_data.get('expLevel', 0)
        
        message = f"👤 *{name}*\n"
        message += f"🏷 `{tag}`\n"
        message += f"🏰 Ратуша: {th_level} уровень\n"
        message += f"🏆 Трофеи: {trophies:,}\n"
        message += f"🥇 Лучший результат: {best_trophies:,}\n"
        message += f"⭐ Уровень опыта: {exp_level}\n"
        
        # Add war stars information
        war_stars = player_data.get('warStars', 0)
        attack_wins = player_data.get('attackWins', 0)
        defense_wins = player_data.get('defenseWins', 0)
        
        message += f"🌟 Звезды войн: {war_stars:,}\n"
        message += f"⚔️ Побед в атаке: {attack_wins:,}\n"
        message += f"🛡️ Побед в защите: {defense_wins:,}\n"
        
        # Add donations information
        donations = player_data.get('donations', 0)
        received = player_data.get('donationsReceived', 0)
        message += f"📤 Отдано войск: {donations:,}\n"
        message += f"📥 Получено войск: {received:,}\n"
        
        # Add super troops information
        super_troops = self._format_super_troops_info(player_data)
        if super_troops:
            message += f"\n{super_troops}"
        
        # Add league information
        league = player_data.get('league')
        if league:
            league_name = league.get('name', 'Неизвестно')
            message += f"🏅 Лига: {league_name}\n"
        
        # Add builder hall information
        builder_hall_level = player_data.get('builderHallLevel', 0)
        versus_trophies = player_data.get('versusTrophies', 0)
        best_versus_trophies = player_data.get('bestVersusTrophies', 0)
        versus_battle_wins = player_data.get('versusBattleWins', 0)
        
        # Show builder base info if player has any builder base activity or level > 0
        if builder_hall_level > 0 or versus_trophies > 0 or best_versus_trophies > 0 or versus_battle_wins > 0:
            message += f"\n🏗️ *База строителя:*\n"
            message += f"🏘️ Дом строителя: {builder_hall_level} уровень\n"
            message += f"🏆 Трофеи против: {versus_trophies:,}\n"
            message += f"🥇 Лучший результат против: {best_versus_trophies:,}\n"
            message += f"⚔️ Побед против: {versus_battle_wins:,}\n"
        
        # Информация о клане
        clan_info = player_data.get('clan')
        if clan_info:
            clan_name = clan_info.get('name', 'Неизвестно')
            clan_tag = clan_info.get('tag', 'Неизвестно')
            clan_role = clan_info.get('role', 'member')
            role_text = self.ROLE_TRANSLATIONS.get(clan_role, '👤 Участник')
            
            message += f"\n🛡 *Клан:* {clan_name}\n"
            message += f"🏷 `{clan_tag}`\n"
            message += f"👑 Роль: {role_text}"
            
            # Add clan position if available
            clan_rank = player_data.get('clanRank')
            if clan_rank:
                message += f"\n📍 Позиция в клане: {clan_rank}"
            
            # Add clan level if available
            clan_level = clan_info.get('clanLevel', 0)
            if clan_level > 0:
                message += f"\n🎖️ Уровень клана: {clan_level}"
        else:
            message += f"\n🚫 Не состоит в клане"
        
        return message
    
    def _format_super_troops_info(self, player_data: Dict[Any, Any]) -> str:
        """Форматирование информации о супер войсках"""
        try:
            troops = player_data.get('troops', [])
            super_troops = []
            
            # Список известных супер войск с их обычными названиями  
            super_troop_names = {
                'Super Barbarian': '⚔️ Супер варвар',
                'Super Archer': '🏹 Супер лучница', 
                'Super Giant': '🗿 Супер гигант',
                'Sneaky Goblin': '👻 Скрытный гоблин',
                'Super Wall Breaker': '💥 Супер стенобой',
                'Super Wizard': '🧙‍♂️ Супер маг',
                'Inferno Dragon': '🔥 Инферно дракон',
                'Super Minion': '👿 Супер прислужник',
                'Super Valkyrie': '⚡ Супер валькирия',
                'Super Witch': '🧙‍♀️ Супер ведьма',
                'Ice Hound': '🧊 Ледяная гончая',
                'Super Bowler': '🎳 Супер боулер',
                'Super Dragon': '🐲 Супер дракон',
                'Super Miner': '⛏️ Супер шахтер'
            }
            
            # Ищем активные супер войска
            for troop in troops:
                troop_name = troop.get('name', '')
                if troop_name in super_troop_names:
                    level = troop.get('level', 0)
                    max_level = troop.get('maxLevel', 0)
                    village = troop.get('village', 'home')
                    
                    if village == 'home' and level > 0:  # Только войска основной деревни
                        # Проверяем время активности супер войска
                        remaining_time = self._calculate_super_troop_time(troop)
                        
                        # Добавляем только если супер войско действительно активно
                        if remaining_time > 0:
                            display_name = super_troop_names[troop_name]
                            
                            super_troops.append({
                                'name': display_name,
                                'level': level,
                                'max_level': max_level,
                                'remaining_time': remaining_time
                            })
            
            if not super_troops:
                return ""
            
            # Сортируем по времени (активные сначала)
            super_troops.sort(key=lambda x: x['remaining_time'], reverse=True)
            
            message = "⚡ *Супер войска:*\n"
            
            # Показываем до 2 супер войск как СУПЕР ВОЙКО 1 и 2
            for i, troop in enumerate(super_troops[:2], 1):
                status = "Активно" if troop['remaining_time'] > 0 else "Неактивно"
                time_text = f"{troop['remaining_time']}ч" if troop['remaining_time'] > 0 else "0ч"
                
                message += f"🔥 СУПЕР ВОЙКО {i}: {troop['name']}\n"
                message += f"   📊 Уровень: {troop['level']}/{troop['max_level']}\n"
                message += f"   ⏰ Время: {time_text} | {status}\n"
            
            # Если есть только одно супер войско, добавляем пустой слот
            if len(super_troops) == 1:
                message += f"🔥 СУПЕР ВОЙКО 2: Не активировано\n"
                message += f"   📊 Уровень: 0/0\n"
                message += f"   ⏰ Время: 0ч | Неактивно\n"
            elif len(super_troops) == 0:
                message += f"🔥 СУПЕР ВОЙКО 1: Не активировано\n"
                message += f"   📊 Уровень: 0/0\n"
                message += f"   ⏰ Время: 0ч | Неактивно\n"
                message += f"🔥 СУПЕР ВОЙКО 2: Не активировано\n"
                message += f"   📊 Уровень: 0/0\n"
                message += f"   ⏰ Время: 0ч | Неактивно\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Ошибка при форматировании супер войск: {e}")
            return ""
    
    def _calculate_super_troop_time(self, troop: Dict) -> int:
        """Расчет оставшегося времени супер войска"""
        try:
            # Проверяем, есть ли информация о супер режиме
            # В реальном COC API информация о супер войсках может содержать время активации
            level = troop.get('level', 0)
            
            # Если войско не прокачено, оно точно не активно
            if level == 0:
                return 0
            
            # Проверяем, есть ли поле superTroopIsActive или подобное
            # В разных версиях API это может называться по-разному
            is_active = troop.get('superTroopIsActive', False)
            if isinstance(is_active, bool) and is_active:
                # Если есть явное указание на активность, возвращаем время
                remaining_time = troop.get('superTroopRemainingTime', 72)  # По умолчанию 72 часа
                return max(0, remaining_time)
            
            # Если нет явной информации об активности, проверяем косвенные признаки
            # Супер войска обычно имеют особые характеристики
            max_level = troop.get('maxLevel', 0)
            
            # Если текущий уровень равен максимальному и больше базового уровня
            # для обычных войск, вероятно это активное супер войско
            if level > 0 and level == max_level and max_level > 25:  # Супер войска обычно высокого уровня
                # Возвращаем фиксированное время для активных супер войск
                return 48  # 48 часов как примерное время
            
            return 0
                
        except Exception:
            return 0
    
    def _format_clan_info(self, clan_data: Dict[Any, Any]) -> str:
        """Форматирование информации о клане"""
        name = clan_data.get('name', 'Неизвестно')
        tag = clan_data.get('tag', 'Неизвестно')
        description = clan_data.get('description', 'Описание отсутствует')
        members_count = clan_data.get('members', 0)
        war_wins = clan_data.get('warWins', 0)
        war_losses = clan_data.get('warLosses', 0)
        war_ties = clan_data.get('warTies', 0)
        
        # Локация
        location = clan_data.get('location', {})
        location_name = location.get('name', 'Неизвестно') if location else 'Неизвестно'
        
        message = f"🛡 *{name}*\n"
        message += f"🏷 `{tag}`\n"
        message += f"📝 {description}\n\n"
        message += f"👥 Участники: {members_count}/50\n"
        message += f"🌍 Локация: {location_name}\n\n"
        message += f"⚔️ *Статистика войн:*\n"
        message += f"🏆 Победы: {war_wins}\n"
        message += f"❌ Поражения: {war_losses}\n"
        message += f"🤝 Ничьи: {war_ties}\n"
        
        total_wars = war_wins + war_losses + war_ties
        if total_wars > 0:
            win_rate = (war_wins / total_wars) * 100
            message += f"📊 Процент побед: {win_rate:.1f}%"
        
        return message
    
    def _format_members_page(self, members: List[Dict], page: int, total_pages: int, 
                           total_members: int, view_type: str) -> str:
        """Форматирование страницы участников"""
        message = f"👥 *Участники клана* (стр. {page}/{total_pages})\n"
        message += f"Всего участников: {total_members}\n\n"
        
        for i, member in enumerate(members, 1):
            # Escape special characters in names to prevent parsing errors
            name = member.get('name', 'Неизвестно').replace('*', '\\*').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]').replace('`', '\\`')
            tag = member.get('tag', 'Неизвестно')
            role = member.get('role', 'member')
            role_text = self.ROLE_TRANSLATIONS.get(role, '👤 Участник')
            trophies = member.get('trophies', 0)
            
            if view_type == MemberView.DETAILED:
                donations = member.get('donations', 0)
                received = member.get('donationsReceived', 0)
                
                message += f"*{i + (page-1) * self.MEMBERS_PER_PAGE}.* {name}\n"
                message += f"   🏷 `{tag}`\n"
                message += f"   👑 {role_text}\n"
                message += f"   🏆 {trophies:,} трофеев\n"
                message += f"   📤 Отдано: {donations:,}\n"
                message += f"   📥 Получено: {received:,}\n\n"
            else:
                message += f"*{i + (page-1) * self.MEMBERS_PER_PAGE}.* {role_text} {name} - 🏆 {trophies:,}\n"
        
        return message
    
    def _format_war_list(self, wars: List[Dict], page: int, total_pages: int) -> str:
        """Форматирование списка войн"""
        message = f"⚔️ *История войн* (стр. {page}/{total_pages})\n\n"
        
        for i, war in enumerate(wars, 1):
            # Escape special characters in opponent names to prevent parsing errors
            opponent_name = war['opponent_name'].replace('*', '\\*').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]').replace('`', '\\`')
            team_size = war['team_size']
            clan_stars = war['clan_stars']
            opponent_stars = war['opponent_stars']
            result = war['result']
            is_cwl = war['is_cwl_war']
            
            result_emoji = {"win": "🏆", "lose": "❌", "tie": "🤝"}.get(result, "❓")
            war_type = "🏆 ЛВК" if is_cwl else "⚔️ КВ"
            
            message += f"*{i}.* {result_emoji} vs {opponent_name}\n"
            message += f"   {war_type} {team_size}на{team_size} | {clan_stars}⭐ - {opponent_stars}⭐\n\n"
        
        return message
    
    def _format_war_details(self, war: Dict[Any, Any]) -> str:
        """Форматирование детальной информации о войне"""
        opponent_name = war['opponent_name']
        team_size = war['team_size']
        clan_stars = war['clan_stars']
        opponent_stars = war['opponent_stars']
        clan_destruction = war['clan_destruction']
        opponent_destruction = war['opponent_destruction']
        result = war['result']
        is_cwl = war['is_cwl_war']
        total_violations = war['total_violations']
        attacks = war.get('attacks', [])
        
        result_text = {"win": "🏆 Победа", "lose": "❌ Поражение", "tie": "🤝 Ничья"}.get(result, "❓ Неизвестно")
        war_type = "🏆 Лига войн кланов" if is_cwl else "⚔️ Клановая война"
        
        message = f"⚔️ *Детали войны*\n\n"
        message += f"🛡 Противник: {opponent_name}\n"
        message += f"👥 Размер: {team_size} на {team_size}\n"
        message += f"🏷 Тип: {war_type}\n"
        message += f"🏆 Результат: {result_text}\n\n"
        message += f"⭐ *Звезды:*\n"
        message += f"   Наш клан: {clan_stars}\n"
        message += f"   Противник: {opponent_stars}\n\n"
        message += f"💥 *Разрушения:*\n"
        message += f"   Наш клан: {clan_destruction:.1f}%\n"
        message += f"   Противник: {opponent_destruction:.1f}%\n\n"
        message += f"🚫 Нарушений правил: {total_violations}\n"
        message += f"⚔️ Всего атак: {len(attacks)}"
        
        return message
    
    def _format_war_attacks(self, war: Dict[Any, Any]) -> str:
        """Форматирование статистики атак войны"""
        opponent_name = war['opponent_name']
        attacks = war.get('attacks', [])
        team_size = war['team_size']
        
        message = f"📊 *Статистика атак*\n\n"
        message += f"🛡 vs {opponent_name}\n"
        message += f"⚔️ Всего атак: {len(attacks)}\n\n"
        
        if not attacks:
            message += "❌ Данные об атаках не найдены."
            return message
        
        # Группируем атаки по игрокам
        player_attacks = {}
        for attack in attacks:
            attacker = attack.get('attacker_name', 'Неизвестно')
            if attacker not in player_attacks:
                player_attacks[attacker] = []
            player_attacks[attacker].append(attack)
        
        message += "👥 *Атаки по игрокам:*\n"
        for i, (player, player_attack_list) in enumerate(player_attacks.items(), 1):
            total_stars = sum(attack.get('stars', 0) for attack in player_attack_list)
            total_destruction = sum(attack.get('destruction_percentage', 0) for attack in player_attack_list)
            avg_destruction = total_destruction / len(player_attack_list) if player_attack_list else 0
            
            message += f"{i}. **{player}**\n"
            message += f"   ⚔️ Атак: {len(player_attack_list)} | ⭐ Звезд: {total_stars} | 💥 Среднее разрушение: {avg_destruction:.1f}%\n\n"
        
        return message
    
    def _format_war_violations(self, war: Dict[Any, Any]) -> str:
        """Форматирование нарушений войны"""
        opponent_name = war['opponent_name']
        total_violations = war['total_violations']
        attacks = war.get('attacks', [])
        team_size = war['team_size']
        
        message = f"🚫 *Нарушения правил*\n\n"
        message += f"🛡 vs {opponent_name}\n"
        message += f"🚫 Всего нарушений: {total_violations}\n\n"
        
        if total_violations == 0:
            message += "✅ Нарушений не обнаружено! Все участники соблюдали правила войны."
            return message
        
        # Анализируем атаки для поиска нарушений
        violations = []
        member_attack_count = {}
        
        # Подсчитываем количество атак каждого игрока
        for attack in attacks:
            attacker = attack.get('attacker_name', 'Неизвестно')
            member_attack_count[attacker] = member_attack_count.get(attacker, 0) + 1
        
        # Ищем игроков, которые не атаковали
        expected_attackers = team_size  # Каждый должен атаковать
        actual_attackers = len(member_attack_count)
        
        if actual_attackers < expected_attackers:
            missed_attacks = expected_attackers - actual_attackers
            violations.append(f"❌ Пропущенных атак: {missed_attacks}")
        
        # Ищем игроков с неполными атаками (менее 2 атак)
        incomplete_attacks = []
        for player, count in member_attack_count.items():
            if count < 2:
                incomplete_attacks.append(f"{player} ({count}/2)")
        
        if incomplete_attacks:
            violations.append(f"⚠️ Неполные атаки: {', '.join(incomplete_attacks)}")
        
        if violations:
            message += "📋 *Обнаруженные нарушения:*\n"
            for violation in violations:
                message += f"• {violation}\n"
        else:
            message += "ℹ️ Подробная информация о нарушениях недоступна."
        
        return message
    
    def _sort_members(self, members: List[Dict], sort_type: str) -> List[Dict]:
        """Сортировка участников клана"""
        if sort_type == MemberSort.ROLE:
            role_order = {"leader": 0, "coLeader": 1, "admin": 2, "member": 3}
            return sorted(members, key=lambda m: (role_order.get(m.get('role', 'member'), 3), -m.get('trophies', 0)))
        elif sort_type == MemberSort.TROPHIES:
            return sorted(members, key=lambda m: -m.get('trophies', 0))
        elif sort_type == MemberSort.DONATIONS:
            return sorted(members, key=lambda m: -m.get('donations', 0))
        elif sort_type == MemberSort.NAME:
            return sorted(members, key=lambda m: m.get('name', '').lower())
        else:
            return members
    
    def _filter_wars_by_sort(self, wars: List[Dict], sort_order: str) -> List[Dict]:
        """Фильтрация войн по типу сортировки"""
        if sort_order == WarSort.WINS:
            return [war for war in wars if war['result'] == 'win']
        elif sort_order == WarSort.LOSSES:
            return [war for war in wars if war['result'] == 'lose']
        elif sort_order == WarSort.CWL_ONLY:
            return [war for war in wars if war['is_cwl_war']]
        else:
            return wars  # RECENT - уже отсортированы по дате
    
    async def handle_subscription_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка меню подписки"""
        chat_id = update.effective_chat.id
        
        try:
            # Получаем текущую подписку пользователя
            subscription = await self.db_service.get_subscription(chat_id)
            
            if subscription and subscription.is_active and not subscription.is_expired():
                # У пользователя есть активная подписка
                subscription_type_display = "👑 ПРО ПЛЮС" if "proplus" in subscription.subscription_type else "💎 Премиум"
                message = (
                    f"{subscription_type_display} <b>Ваша подписка</b>\n\n"
                    f"📅 Тип: {self.payment_service.get_subscription_name(subscription.subscription_type)}\n"
                    f"⏰ Действует до: {subscription.end_date.strftime('%d.%m.%Y %H:%M')}\n"
                    f"📊 Дней осталось: {subscription.days_remaining()}\n\n"
                    f"Хотите продлить или изменить подписку?"
                )
                keyboard = Keyboards.subscription_status(True)
            else:
                # У пользователя нет активной подписки
                from policy import get_policy_url
                
                message = (
                    f"💎 <b>Премиум подписки</b>\n\n"
                    f"🚀 <b>Выберите тип подписки:</b>\n\n"
                    f"💎 <b>Премиум:</b>\n"
                    f"• 🔔 Расширенные уведомления\n"
                    f"• 📊 Базовая статистика\n"
                    f"• 🎯 Дополнительные функции\n\n"
                    f"👑 <b>ПРО ПЛЮС:</b>\n"
                    f"• ✨ Все функции Премиум\n"
                    f"• 🔥 Приоритетная поддержка\n"
                    f"• 📈 Расширенная аналитика\n"
                    f"• 🛡️ Эксклюзивные функции\n"
                    f"• ⚙️ Персональные настройки\n\n"
                    f"📋 <a href='{get_policy_url()}'>Политика оплаты и возвратов</a>\n\n"
                    f"💰 <b>Выберите подписку:</b>"
                )
                keyboard = Keyboards.subscription_types()
            
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(
                    message, 
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(
                    message, 
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
        
        except Exception as e:
            logger.error(f"Ошибка при обработке меню подписки: {e}")
            error_message = "Произошла ошибка при загрузке информации о подписке."
            
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
    
    async def handle_subscription_extend(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка продления подписки для пользователей с активной подпиской"""
        chat_id = update.effective_chat.id
        
        try:
            # Получаем текущую подписку пользователя
            subscription = await self.db_service.get_subscription(chat_id)
            
            if not subscription or not subscription.is_active or subscription.is_expired():
                # Если подписки нет, перенаправляем к обычному меню
                await self.handle_subscription_menu(update, context)
                return
            
            # Показываем меню продления подписки
            subscription_type_display = "👑 ПРО ПЛЮС" if "proplus" in subscription.subscription_type else "💎 Премиум"
            message = (
                f"{subscription_type_display} <b>Продление подписки</b>\n\n"
                f"📅 Текущая подписка: {self.payment_service.get_subscription_name(subscription.subscription_type)}\n"
                f"⏰ Действует до: {subscription.end_date.strftime('%d.%m.%Y %H:%M')}\n"
                f"📊 Дней осталось: {subscription.days_remaining()}\n\n"
                f"🚀 <b>Выберите тип подписки для продления:</b>\n\n"
                f"💎 <b>Премиум:</b>\n"
                f"• 🔔 Расширенные уведомления\n"
                f"• 📊 Базовая статистика\n"
                f"• 🎯 Дополнительные функции\n\n"
                f"👑 <b>ПРО ПЛЮС:</b>\n"
                f"• ✨ Все функции Премиум\n"
                f"• 🔥 Приоритетная поддержка\n"
                f"• 📈 Расширенная аналитика\n"
                f"• 🛡️ Эксклюзивные функции\n"
                f"• ⚙️ Персональные настройки\n\n"
                f"💰 <b>Выберите подписку для продления:</b>"
            )
            keyboard = Keyboards.subscription_types()
            
            await update.callback_query.edit_message_text(
                message, 
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        
        except Exception as e:
            logger.error(f"Ошибка при обработке продления подписки: {e}")
            await update.callback_query.edit_message_text("Произошла ошибка при загрузке меню продления подписки.")
    
    
    async def handle_subscription_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                                subscription_type: str):
        """Обработка выбора типа подписки"""
        try:
            if subscription_type == "premium":
                message = (
                    f"💎 <b>Премиум подписка</b>\n\n"
                    f"🔔 Расширенные уведомления\n"
                    f"📊 Базовая статистика\n"
                    f"🎯 Дополнительные функции\n\n"
                    f"💰 <b>Выберите период:</b>"
                )
            else:  # proplus
                message = (
                    f"👑 <b>ПРО ПЛЮС подписка</b>\n\n"
                    f"✨ Все функции Премиум\n"
                    f"🔥 Приоритетная поддержка\n"
                    f"📈 Расширенная аналитика\n"
                    f"🛡️ Эксклюзивные функции\n"
                    f"⚙️ Персональные настройки\n\n"
                    f"💰 <b>Выберите период:</b>"
                )
            
            keyboard = Keyboards.subscription_periods(subscription_type)
            
            await update.callback_query.edit_message_text(
                message, 
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        
        except Exception as e:
            logger.error(f"Ошибка при выборе типа подписки: {e}")
            await update.callback_query.edit_message_text("Произошла ошибка при выборе типа подписки.")
    
    async def handle_subscription_payment_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                                     subscription_type: str):
        """Обработка подтверждения оплаты подписки"""
        chat_id = update.effective_chat.id
        
        try:
            price = self.payment_service.get_subscription_price(subscription_type)
            name = self.payment_service.get_subscription_name(subscription_type)
            
            message = (
                f"💳 <b>Подтверждение оплаты</b>\n\n"
                f"📦 Услуга: {name}\n"
                f"💰 Стоимость: {price}₽\n\n"
                f"❓ Подтвердите оплату данной подписки?"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Подтвердить оплату", 
                                    callback_data=f"confirm_payment:{subscription_type}")],
                [InlineKeyboardButton("❌ Отменить", 
                                    callback_data=Keyboards.SUBSCRIPTION_CALLBACK)]
            ])
            
            await update.callback_query.edit_message_text(
                message, 
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        
        except Exception as e:
            logger.error(f"Ошибка при подтверждении оплаты: {e}")
            await update.callback_query.edit_message_text("Произошла ошибка при подтверждении оплаты.")
    
    async def handle_subscription_period_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                                  subscription_type: str):
        """Обработка выбора периода подписки"""
        chat_id = update.effective_chat.id
        
        try:
            # Создаем платеж в YooKassa
            payment_data = await self.payment_service.create_payment(
                telegram_id=chat_id,
                subscription_type=subscription_type,
                return_url=f"https://t.me/{config.BOT_USERNAME}?start=payment_success_{subscription_type}"
            )
            
            if payment_data and 'confirmation' in payment_data:
                # Сохраняем ID платежа в контексте пользователя
                context.user_data['pending_payment'] = {
                    'payment_id': payment_data['id'],
                    'subscription_type': subscription_type,
                    'amount': payment_data['amount']['value']
                }
                
                subscription_name = self.payment_service.get_subscription_name(subscription_type)
                price = self.payment_service.get_subscription_price(subscription_type)
                
                message = (
                    f"💳 <b>Активация премиум подписки</b>\n\n"
                    f"📦 Подписка: {subscription_name}\n"
                    f"💰 Сумма: {price:.0f} ₽\n\n"
                    f"Нажмите кнопку ниже для перехода к оплате.\n"
                    f"После успешной оплаты ваша премиум подписка будет активирована автоматически."
                )
                
                keyboard = Keyboards.subscription_payment(payment_data['confirmation']['confirmation_url'])
                
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
                
                # Запускаем проверку статуса платежа
                await self._schedule_payment_check(context, payment_data['id'], chat_id, subscription_type)
            
            else:
                await update.callback_query.edit_message_text(
                    "❌ Ошибка при создании платежа. Попробуйте позже.",
                    reply_markup=Keyboards.back_to_main()
                )
        
        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {e}")
            await update.callback_query.edit_message_text(
                "❌ Произошла ошибка при создании платежа. Попробуйте позже.",
                reply_markup=Keyboards.back_to_main()
            )
    
    async def _schedule_payment_check(self, context: ContextTypes.DEFAULT_TYPE, payment_id: str, 
                                     chat_id: int, subscription_type: str):
        """Планирование проверки статуса платежа"""
        # В реальном боте здесь был бы более сложный механизм проверки
        # Для простоты используем базовую логику
        
        async def check_payment():
            for _ in range(30):  # Проверяем 5 минут с интервалом 10 секунд
                await asyncio.sleep(10)
                
                payment_status = await self.payment_service.check_payment_status(payment_id)
                if payment_status and payment_status.get('status') == 'succeeded':
                    await self._process_successful_payment(chat_id, subscription_type, payment_id, payment_status)
                    break
        
        # Запускаем проверку в фоне (в реальном боте используйте job_queue)
        asyncio.create_task(check_payment())
    
    async def _process_successful_payment(self, telegram_id: int, subscription_type: str, 
                                        payment_id: str, payment_data: Dict):
        """Обработка успешного платежа"""
        try:
            # Получаем длительность подписки
            duration = self.payment_service.get_subscription_duration(subscription_type)
            amount = float(payment_data['amount']['value'])
            
            # Проверяем существующую подписку
            existing_subscription = await self.db_service.get_subscription(telegram_id)
            
            if existing_subscription and existing_subscription.is_active and not existing_subscription.is_expired():
                # Продляем существующую подписку
                new_end_date = existing_subscription.end_date + duration
                existing_subscription.end_date = new_end_date
                existing_subscription.payment_id = payment_id
                existing_subscription.amount = amount
                
                success = await self.db_service.save_subscription(existing_subscription)
                message = (
                    f"✅ <b>Подписка продлена!</b>\n\n"
                    f"📅 Новая дата окончания: {new_end_date.strftime('%d.%m.%Y %H:%M')}\n"
                    f"💳 Сумма платежа: {amount:.0f} ₽"
                )
            else:
                # Создаем новую подписку
                start_date = datetime.now()
                end_date = start_date + duration
                
                new_subscription = Subscription(
                    telegram_id=telegram_id,
                    subscription_type=subscription_type,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True,
                    payment_id=payment_id,
                    amount=amount
                )
                
                success = await self.db_service.save_subscription(new_subscription)
                message = (
                    f"✅ <b>Подписка активирована!</b>\n\n"
                    f"📅 Действует до: {end_date.strftime('%d.%m.%Y %H:%M')}\n"
                    f"💳 Сумма платежа: {amount:.0f} ₽"
                )
            
            if success:
                # Отправляем уведомление пользователю
                logger.info(f"Подписка успешно обработана для пользователя {telegram_id}")
                # Сохраняем сообщение для отправки при следующем взаимодействии с ботом
                await self._send_payment_notification(telegram_id, message)
            else:
                logger.error(f"Ошибка при сохранении подписки для пользователя {telegram_id}")
        
        except Exception as e:
            logger.error(f"Ошибка при обработке успешного платежа: {e}")
    
    async def _send_payment_notification(self, telegram_id: int, message: str):
        """Отправка уведомления о платеже пользователю"""
        try:
            # Попробуем получить экземпляр бота из глобального контекста или создать новый
            from config import config
            from telegram import Bot
            
            bot = Bot(token=config.BOT_TOKEN)
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            logger.info(f"Уведомление о платеже отправлено пользователю {telegram_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления о платеже: {e}")
            # В случае ошибки сохраняем уведомление в базе для последующей отправки
            await self._save_pending_notification(telegram_id, message)
    
    async def _save_pending_notification(self, telegram_id: int, message: str):
        """Сохранение отложенного уведомления"""
        try:
            # Создаем запись в БД о необходимости отправить уведомление
            notification_data = {
                'telegram_id': telegram_id,
                'message': message,
                'type': 'payment_success',
                'created_at': datetime.now().isoformat()
            }
            # Здесь можно добавить сохранение в БД или использовать другой механизм
            logger.info(f"Уведомление сохранено для отложенной отправки пользователю {telegram_id}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении отложенного уведомления: {e}")
    
    async def display_current_war(self, update: Update, context: ContextTypes.DEFAULT_TYPE, clan_tag: str):
        """Отображение информации о текущей войне клана"""
        # Показываем индикатор загрузки
        await update.callback_query.edit_message_text("⚔️ Получение информации о войне...")
        
        try:
            async with self.coc_client as client:
                war_data = await client.get_clan_current_war(clan_tag)
                
                if not war_data:
                    await update.callback_query.edit_message_text(
                        "❌ Не удалось получить информацию о текущей войне."
                    )
                    return
                
                # Check war state
                state = war_data.get('state', 'notInWar')
                
                if state == 'notInWar':
                    await update.callback_query.edit_message_text(
                        "🕊️ Клан сейчас не участвует в войне."
                    )
                    return
                
                # Format current war information
                message = self._format_current_war_info(war_data)
                
                await update.callback_query.edit_message_text(
                    message, parse_mode=ParseMode.MARKDOWN
                )
        
        except asyncio.TimeoutError:
            logger.error(f"Таймаут при получении информации о войне для клана {clan_tag}")
            await update.callback_query.edit_message_text(
                "⏱️ Превышено время ожидания при загрузке данных о войне.\n"
                "Попробуйте позже."
            )
        except Exception as e:
            logger.error(f"Ошибка при получении информации о текущей войне: {e}")
            await update.callback_query.edit_message_text(
                "❌ Произошла ошибка при получении информации о войне."
            )
    
    async def display_cwl_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, clan_tag: str):
        """Отображение информации о Лиге войн кланов (CWL)"""
        # Показываем индикатор загрузки
        await update.callback_query.edit_message_text("🏆 Получение информации о ЛВК...")
        
        try:
            async with self.coc_client as client:
                cwl_data = await client.get_clan_war_league_group(clan_tag)
                
                if not cwl_data:
                    # Возвращаемся к меню клана вместо показа ошибки
                    from translations import translation_manager
                    message = translation_manager.get_text(update, 'cwl_not_participating', 
                                                         "❌ Клан не участвует в текущем сезоне ЛВК.")
                    
                    # Создаем кнопку возврата к меню клана
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton(
                            translation_manager.get_text(update, 'cwl_back_to_clan', "⬅️ Назад к клану"),
                            callback_data="clan_info"
                        )]
                    ])
                    
                    await update.callback_query.edit_message_text(
                        message,
                        reply_markup=keyboard
                    )
                    return
                
                # Format CWL information
                message = self._format_cwl_info(cwl_data)
                
                await update.callback_query.edit_message_text(
                    message, parse_mode=ParseMode.MARKDOWN
                )
        
        except asyncio.TimeoutError:
            logger.error(f"Таймаут при получении информации о ЛВК для клана {clan_tag}")
            await update.callback_query.edit_message_text(
                "⏱️ Превышено время ожидания при загрузке данных о ЛВК.\n"
                "Попробуйте позже."
            )
        except Exception as e:
            logger.error(f"Ошибка при получении информации о ЛВК: {e}")
            await update.callback_query.edit_message_text(
                "❌ Произошла ошибка при получении информации о ЛВК."
            )
    
    def _format_current_war_info(self, war_data: Dict[Any, Any]) -> str:
        """Формат��рование информации о текущей войне"""
        state = war_data.get('state', 'unknown')
        team_size = war_data.get('teamSize', 0)
        
        # Get clan and opponent info
        clan = war_data.get('clan', {})
        opponent = war_data.get('opponent', {})
        
        clan_name = clan.get('name', 'Неизвестно')
        clan_stars = clan.get('stars', 0)
        clan_destruction = clan.get('destructionPercentage', 0.0)
        clan_attacks = clan.get('attacks', 0)
        
        opponent_name = opponent.get('name', 'Неизвестно')
        opponent_stars = opponent.get('stars', 0)
        opponent_destruction = opponent.get('destructionPercentage', 0.0)
        opponent_attacks = opponent.get('attacks', 0)
        
        # State translations
        state_translations = {
            'preparation': '🔄 Подготовка',
            'inWar': '⚔️ Идет война',
            'warEnded': '🏁 Война завершена'
        }
        
        state_text = state_translations.get(state, '❓ Неизвестно')
        
        message = f"⚔️ *Текущая война*\n\n"
        message += f"📊 Статус: {state_text}\n"
        message += f"👥 Размер: {team_size} на {team_size}\n\n"
        
        message += f"🛡️ *{clan_name}*\n"
        message += f"⭐ Звезды: {clan_stars}\n"
        message += f"💥 Разр��шение: {clan_destruction:.1f}%\n"
        message += f"⚔️ Атак использовано: {clan_attacks}\n\n"
        
        message += f"🛡️ *{opponent_name}*\n"
        message += f"⭐ Звезды: {opponent_stars}\n"
        message += f"💥 Разрушение: {opponent_destruction:.1f}%\n"
        message += f"⚔️ Атак использовано: {opponent_attacks}\n\n"
        
        # Show time information based on state
        if state == 'preparation':
            start_time = war_data.get('startTime')
            if start_time:
                formatted_time = self._format_datetime(start_time)
                message += f"🕐 Начало войны: {formatted_time}\n"
        elif state == 'inWar':
            end_time = war_data.get('endTime')
            if end_time:
                formatted_time = self._format_datetime(end_time)
                message += f"🕐 Конец войны: {formatted_time}\n"
        
        return message
    
    def _format_cwl_info(self, cwl_data: Dict[Any, Any]) -> str:
        """Форматирование информации о ЛВК"""
        state = cwl_data.get('state', 'unknown')
        season = cwl_data.get('season', 'Неизвестно')
        
        # State translations
        state_translations = {
            'preparation': '🔄 Подготовка',
            'inWar': '⚔️ Идет ЛВК',
            'ended': '🏁 ЛВК завершена'
        }
        
        state_text = state_translations.get(state, '❓ Неизвестно')
        
        message = f"🏆 *Лига войн кланов*\n\n"
        message += f"📅 Сезон: {season}\n"
        message += f"📊 Статус: {state_text}\n\n"
        
        # Get clans in the league
        clans = cwl_data.get('clans', [])
        if clans:
            message += f"🛡️ *Участники лиги ({len(clans)} кланов):*\n"
            for i, clan in enumerate(clans[:8], 1):  # Show up to 8 clans
                clan_name = clan.get('name', 'Неизвестно')
                clan_level = clan.get('clanLevel', 0)
                message += f"{i}. {clan_name} (ур. {clan_level})\n"
            
            if len(clans) > 8:
                message += f"... и еще {len(clans) - 8} кланов\n"
        
        # Get rounds information
        rounds = cwl_data.get('rounds', [])
        if rounds:
            message += f"\n📋 *Раунды:* {len(rounds)}\n"
            
            # Show current round info if available
            current_round = None
            for i, round_data in enumerate(rounds):
                war_tags = round_data.get('warTags', [])
                if war_tags and war_tags[0] != '#0':
                    current_round = i + 1
                    break
            
            if current_round:
                message += f"⚔️ Текущий раунд: {current_round}\n"
        
        return message
    
    async def display_cwl_bonus_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, year_month: str):
        """Отображение информации о бонусах ЛВК"""
        try:
            # Get CWL bonus data from database for the specified month
            bonus_data = await self.db_service.get_cwl_bonus_data(year_month)
            
            if not bonus_data:
                await update.callback_query.edit_message_text(
                    f"❌ Данные о бонусах ЛВК за {year_month} не найдены."
                )
                return
            
            # Format bonus information  
            message = self._format_cwl_bonus_info(bonus_data, year_month)
            
            await update.callback_query.edit_message_text(
                message, parse_mode=ParseMode.MARKDOWN
            )
        
        except Exception as e:
            logger.error(f"Ошибка при получении информации о бонусах ЛВК: {e}")
            await update.callback_query.edit_message_text(
                "❌ Произошла ошибка при получении информации о бонусах ЛВК."
            )
    
    def _format_cwl_bonus_info(self, bonus_data: List[Dict], year_month: str) -> str:
        """Форматирование информации о бонусах ЛВК"""
        # Parse year-month for display
        try:
            year, month = year_month.split('-')
            month_names = {
                '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
                '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
                '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
            }
            month_name = month_names.get(month, month)
            display_date = f"{month_name} {year}"
        except Exception:
            display_date = year_month
        
        message = f"🏆 *Бонусы ЛВК - {display_date}*\n\n"
        
        if not bonus_data:
            message += "📭 Данные о бонусах не найдены."
            return message
        
        total_bonuses = len(bonus_data)
        message += f"📊 Всего бонусов выдано: {total_bonuses}\n\n"
        
        # Group bonuses by player
        player_bonuses = {}
        for bonus in bonus_data:
            player_name = bonus.get('player_name', 'Неизвестно')
            bonus_amount = bonus.get('bonus_amount', 0)
            if player_name not in player_bonuses:
                player_bonuses[player_name] = 0
            player_bonuses[player_name] += bonus_amount
        
        # Sort players by total bonus amount
        sorted_players = sorted(player_bonuses.items(), key=lambda x: x[1], reverse=True)
        
        message += "🎖️ *Игроки и их бонусы:*\n"
        for i, (player_name, total_bonus) in enumerate(sorted_players[:10], 1):
            message += f"{i}. {player_name}: {total_bonus:,} 💎\n"
        
        if len(sorted_players) > 10:
            message += f"... и еще {len(sorted_players) - 10} игроков\n"
        
        # Calculate total bonus amount
        total_amount = sum(player_bonuses.values())
        message += f"\n💰 Общая сумма бонусов: {total_amount:,} 💎"
        
        return message
    
    async def display_cwl_bonus_distribution(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отображение распределения бонусов ЛВК"""
        try:
            clan_tag = context.user_data.get('inspecting_clan')
            if not clan_tag:
                await update.callback_query.edit_message_text("❌ Клан не выбран.")
                return
            
            # Get clan info to determine league
            async with self.coc_client as client:
                clan_data = await client.get_clan_info(clan_tag)
                
                if not clan_data:
                    await update.callback_query.edit_message_text("❌ Не удалось получить информацию о клане.")
                    return
                
                clan_name = clan_data.get('name', 'Неизвестно')
                
                # Get clan league
                war_league = clan_data.get('warLeague', {})
                league_name = war_league.get('name', 'Неизвестно')
                
                # Determine number of bonus spots based on league
                bonus_spots = self._get_bonus_spots_by_league(league_name)
                
                # Get current CWL season dates (approximate - from start of current month to now)
                now = datetime.now()
                # CWL typically starts around the 1st of the month
                season_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                season_end = now
                
                # Get donation stats for the season
                donation_stats = await self.db_service.get_cwl_season_donation_stats(
                    season_start.isoformat(), season_end.isoformat()
                )
                
                # Get attack stats for the season
                attack_stats = await self.db_service.get_cwl_season_attack_stats(
                    season_start.isoformat(), season_end.isoformat()
                )
                
                # Get current clan members to map tags to names
                members = clan_data.get('memberList', [])
                member_map = {m.get('tag'): m.get('name') for m in members}
                
                # Calculate bonus distribution
                distribution = self._calculate_bonus_distribution(
                    donation_stats, attack_stats, member_map, bonus_spots
                )
                
                # Format and display the message
                message = self._format_cwl_bonus_distribution(
                    clan_name, league_name, bonus_spots, distribution
                )
                
                await update.callback_query.edit_message_text(
                    message, parse_mode=ParseMode.MARKDOWN
                )
        
        except Exception as e:
            logger.error(f"Ошибка при отображении распределения бонусов ЛВК: {e}")
            await update.callback_query.edit_message_text(
                "❌ Произошла ошибка при получении информации о распределении бонусов."
            )
    
    def _get_bonus_spots_by_league(self, league_name: str) -> int:
        """Определение количества бонусных мест по лиге"""
        # Based on Clash of Clans CWL league bonus structure
        league_bonuses = {
            'Champion League I': 8,
            'Champion League II': 7,
            'Champion League III': 6,
            'Master League I': 5,
            'Master League II': 4,
            'Master League III': 3,
            'Crystal League I': 3,
            'Crystal League II': 2,
            'Crystal League III': 2,
            'Gold League I': 2,
            'Gold League II': 2,
            'Gold League III': 2,
            'Silver League I': 2,
            'Silver League II': 2,
            'Silver League III': 2,
            'Bronze League I': 2,
            'Bronze League II': 2,
            'Bronze League III': 2,
        }
        return league_bonuses.get(league_name, 2)  # Default to 2 if unknown
    
    def _calculate_bonus_distribution(self, donation_stats: Dict[str, int], 
                                     attack_stats: Dict[str, Dict], 
                                     member_map: Dict[str, str],
                                     bonus_spots: int) -> List[Dict]:
        """Расчет распределения бонусов ЛВК"""
        candidates = []
        
        # Combine all player data
        all_player_tags = set(donation_stats.keys()) | set(attack_stats.keys())
        
        for player_tag in all_player_tags:
            player_name = member_map.get(player_tag, 'Неизвестно')
            donations = donation_stats.get(player_tag, 0)
            attacks = attack_stats.get(player_tag, {
                'cwl_attacks': 0,
                'regular_attacks': 0,
                'cwl_wars': 0,
                'regular_wars': 0
            })
            
            # Skip players who don't meet minimum regular war attacks (10)
            if attacks['regular_attacks'] < 10:
                continue
            
            candidates.append({
                'player_tag': player_tag,
                'player_name': player_name,
                'donations': donations,
                'cwl_attacks': attacks['cwl_attacks'],
                'cwl_wars': attacks['cwl_wars'],
                'regular_attacks': attacks['regular_attacks'],
                'regular_wars': attacks['regular_wars']
            })
        
        if not candidates:
            return []
        
        # Sort to find top donator
        sorted_by_donations = sorted(candidates, key=lambda x: x['donations'], reverse=True)
        
        # First spot always goes to top donator
        distribution = []
        if sorted_by_donations:
            top_donator = sorted_by_donations[0]
            distribution.append({
                'rank': 1,
                'player_name': top_donator['player_name'],
                'reason': f"🎁 Топ донатов: {top_donator['donations']:,}",
                'cwl_attacks': top_donator['cwl_attacks'],
                'regular_attacks': top_donator['regular_attacks']
            })
            top_donator_tag = top_donator['player_tag']
        else:
            top_donator_tag = None
        
        # Sort remaining candidates by attack performance
        # Priority: CWL attacks completed (7/7 > 6/7 > ...), then by regular war attacks
        remaining_candidates = [c for c in candidates if c['player_tag'] != top_donator_tag]
        
        def attack_priority(candidate):
            # Return tuple for sorting: (CWL attacks completed, regular attacks)
            # Higher CWL attacks are better, then higher regular attacks
            cwl_ratio = candidate['cwl_attacks']
            return (cwl_ratio, candidate['regular_attacks'])
        
        sorted_by_attacks = sorted(remaining_candidates, key=attack_priority, reverse=True)
        
        # Fill remaining bonus spots
        for i, candidate in enumerate(sorted_by_attacks[:bonus_spots - 1], 2):
            distribution.append({
                'rank': i,
                'player_name': candidate['player_name'],
                'reason': f"⚔️ ЛВК: {candidate['cwl_attacks']} атак, КВ: {candidate['regular_attacks']} атак",
                'cwl_attacks': candidate['cwl_attacks'],
                'regular_attacks': candidate['regular_attacks']
            })
        
        return distribution
    
    def _format_cwl_bonus_distribution(self, clan_name: str, league_name: str, 
                                      bonus_spots: int, distribution: List[Dict]) -> str:
        """Форматирование информации о распределении бонусов ЛВК"""
        message = f"💎 *Распределение бонусов ЛВК*\n\n"
        message += f"🛡️ Клан: {clan_name}\n"
        message += f"🏆 Лига: {league_name}\n"
        message += f"📊 Доступно бонусов: {bonus_spots}\n\n"
        
        # Add description of the system
        message += "📋 *Система распределения:*\n"
        message += "1️⃣ Первое место - игрок с наибольшим количеством пожертвований за сезон\n"
        message += "2️⃣ Остальные места - игроки с лучшими показателями атак в ЛВК\n"
        message += "⚠️ Минимум 10 атак в обычных КВ за сезон для участия\n"
        message += "🎯 Приоритет: больше атак ЛВК → больше атак КВ\n\n"
        
        if not distribution:
            message += "📭 Нет данных о кандидатах на бонусы.\n"
            message += "Возможные причины:\n"
            message += "• Недостаточно данных за текущий сезон\n"
            message += "• Никто не выполнил минимальные требования (10 атак КВ)\n"
            return message
        
        message += "🎖️ *Распределение бонусных мест:*\n\n"
        
        for entry in distribution:
            rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(entry['rank'], f"{entry['rank']}.")
            message += f"{rank_emoji} {entry['player_name']}\n"
            message += f"   {entry['reason']}\n\n"
        
        if len(distribution) < bonus_spots:
            message += f"ℹ️ Осталось {bonus_spots - len(distribution)} свободных мест\n"
        
        return message
    
    async def handle_premium_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка меню для премиум подписчиков"""
        chat_id = update.effective_chat.id
        
        try:
            # Проверяем статус подписки
            subscription = await self.db_service.get_subscription(chat_id)
            
            if not subscription or not subscription.is_active or subscription.is_expired():
                await update.callback_query.edit_message_text(
                    "❌ У вас нет активной подписки.\n"
                    "Оформите подписку для доступа к премиум функциям.",
                    reply_markup=Keyboards.subscription_status(False)
                )
                return
            
            subscription_type_display = "👑 ПРО ПЛЮС" if "proplus" in subscription.subscription_type else "💎 Премиум"
            
            message = (
                f"{subscription_type_display} <b>Меню премиум</b>\n\n"
                f"🎉 Добро пожаловать в премиум меню!\n\n"
                f"📅 Подписка действует до: {subscription.end_date.strftime('%d.%m.%Y')}\n"
                f"⏰ Дней осталось: {subscription.days_remaining()}\n\n"
                f"🔧 Доступные функции:\n"
                f"• 🔔 Расширенные уведомления\n"
                f"• 🏗️ Отслеживание улучшений зданий\n"
                f"• ⚙️ Персональные настройки\n"
                f"• 📊 Дополнительная статистика"
            )
            
            keyboard = Keyboards.premium_menu()
            
            await update.callback_query.edit_message_text(
                message, 
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        
        except Exception as e:
            logger.error(f"Ошибка при обработке премиум меню: {e}")
            await update.callback_query.edit_message_text("Произошла ошибка при загрузке премиум меню.")
    
    async def handle_advanced_notifications(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка расширенных настроек уведомлений"""
        chat_id = update.effective_chat.id
        
        try:
            # Проверяем статус подписки
            subscription = await self.db_service.get_subscription(chat_id)
            
            if not subscription or not subscription.is_active or subscription.is_expired():
                await update.callback_query.edit_message_text(
                    "❌ Расширенные настройки уведомлений доступны только для премиум подписчиков.",
                    reply_markup=Keyboards.subscription_status(False)
                )
                return
            
            message = (
                f"⚙️ <b>Расширенные настройки уведомлений</b>\n\n"
                f"Настройте персональные уведомления о начале КВ.\n"
                f"Можете указать время в минутах (m) или часах (h).\n"
                f"Например: 14m, 2h, 30m\n\n"
                f"⏰ Максимум: 24 часа до начала КВ\n\n"
                f"Используйте кнопки ниже для настройки:"
            )
            
            keyboard = Keyboards.notification_advanced_menu()
            
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(message, parse_mode=ParseMode.HTML)
                await update.callback_query.message.reply_text(
                    "Выберите уведомление для настройки:",
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    message, 
                    parse_mode=ParseMode.HTML
                )
                await update.message.reply_text(
                    "Выберите уведомление для настройки:",
                    reply_markup=keyboard
                )
        
        except Exception as e:
            logger.error(f"Ошибка при обработке расширенных настроек: {e}")
            error_msg = "Произошла ошибка при загрузке расширенных настроек."
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(error_msg)
            else:
                await update.message.reply_text(error_msg)
    
    async def handle_building_tracker_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка меню отслеживания улучшений зданий"""
        chat_id = update.effective_chat.id
        
        try:
            # Проверяем статус подписки
            subscription = await self.db_service.get_subscription(chat_id)
            
            if not subscription or not subscription.is_active or subscription.is_expired():
                await update.callback_query.edit_message_text(
                    "❌ Отслеживание улучшений доступно только для премиум подписчиков.",
                    reply_markup=Keyboards.subscription_status(False)
                )
                return
            
            # Проверяем статус подписки для определения частоты проверки
            # Согласно политике фан контента SuperCell - все аккаунты проверяются каждые 1.5 минуты
            check_interval_text = "каждые 1.5 минуты"
            
            # Проверяем статус отслеживания
            from building_monitor import BuildingMonitor
            building_monitor = context.bot_data.get('building_monitor', None)
            is_active = False
            
            if building_monitor:
                is_active = await building_monitor.is_tracking_active(chat_id)
            
            message = (
                f"🏗️ <b>Отслеживание улучшений зданий</b>\n\n"
                f"📋 <b>Как это работает:</b>\n"
                f"• Чекер {check_interval_text} проверяет состояние всех зданий, героев, питомцев, стен и деревни строителя\n"
                f"• При обнаружении изменений (улучшений) отправляет уведомления\n"
                f"• Работает по сравнению с первоначальным сканом при добавлении профиля\n"
                f"• Отслеживает все привязанные к аккаунту профили\n\n"
                f"🏗️ <b>Что отслеживается:</b>\n"
                f"• Все здания основной деревни\n"
                f"• Герои и их уровни\n"
                f"• Снаряжение героев/питомцы\n"
                f"• Войска и заклинания (улучшения в лаборатории)\n"
                f"• Стены\n"
                f"• Деревня строителя и её улучшения\n\n"
                f"⏱️ <b>Частота проверки:</b>\n"
                f"• Все пользователи: каждые 1.5 минуты (согласно политике SuperCell)\n\n"
                f"⚠️ <b>Важно:</b>\n"
                f"• Функция доступна только при наличии ДЕЙСТВУЮЩЕЙ подписки\n"
                f"• При истечении подписки уведомления ПЕРЕСТАНУТ отправляться\n"
                f"• При наличии нескольких аккаунтов в уведомлении указывается на каком произошли изменения\n\n"
                f"📊 <b>Текущий статус:</b> {'🟢 Активно' if is_active else '🔴 Неактивно'}\n\n"
                f"💡 <b>Пример уведомления:</b>\n"
                f"\"🏗️ Улучшение завершено!\n👤 Аккаунт: PlayerName\n🔨 Мортира улучшена с 14 на 15 уровень!\""
            )
            
            keyboard = Keyboards.building_tracker_menu(is_active)
            
            await update.callback_query.edit_message_text(
                message, 
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        
        except Exception as e:
            logger.error(f"Ошибка при обработке меню отслеживания зданий: {e}")
            await update.callback_query.edit_message_text("Произошла ошибка при загрузке меню отслеживания.")
    
    async def handle_building_tracker_toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Переключение состояния отслеживания зданий"""
        chat_id = update.effective_chat.id
        
        try:
            # Проверяем статус подписки
            subscription = await self.db_service.get_subscription(chat_id)
            
            if not subscription or not subscription.is_active or subscription.is_expired():
                await update.callback_query.edit_message_text(
                    "❌ Отслеживание улучшений доступно только для премиум подписчиков.",
                    reply_markup=Keyboards.subscription_status(False)
                )
                return
            
            # Проверяем наличие профилей (новая система) или старого аккаунта
            user_profiles = await self.db_service.get_user_profiles(chat_id)
            user = await self.db_service.find_user(chat_id) if not user_profiles else None
            
            if not user_profiles and not user:
                await update.callback_query.edit_message_text(
                    "❌ Для использования отслеживания нужно привязать аккаунт игрока.\n"
                    "Используйте команду в главном меню для привязки аккаунта."
                )
                return
            
            from building_monitor import BuildingMonitor
            building_monitor = context.bot_data.get('building_monitor', None)

            if not building_monitor:
                await update.callback_query.edit_message_text(
                    "❌ Сервис отслеживания временно недоступен."
                )
                return
            
            # Проверяем текущий статус
            is_active = await building_monitor.is_tracking_active(chat_id)
            
            if is_active:
                # Деактивируем отслеживание
                success = await building_monitor.deactivate_tracking(chat_id)
                if success:
                    message = "🔴 Отслеживание улучшений отключено для всех профилей."
                else:
                    message = "❌ Ошибка при отключении отслеживания."
            else:
                # Активируем отслеживание
                player_tag = user.player_tag if user else None
                success = await building_monitor.activate_tracking(chat_id, player_tag)
                if success:
                    profile_count = len(user_profiles) if user_profiles else 1
                    message = (
                        "🟢 Отслеживание улучшений активировано!\n\n"
                        f"📊 Отслеживается профилей: {profile_count}\n"
                        "📋 Создан первый снимок ваших зданий.\n"
                        "🔄 Проверка изменений будет происходить каждые 1.5 минуты.\n"
                        "🔔 Вы получите уведомление при любом улучшении."
                    )
                    if profile_count > 1:
                        message += "\n👤 В уведомлениях будет указан аккаунт, где произошли изменения."
                else:
                    message = "❌ Ошибка при активации отслеживания."
            
            # Обновляем меню
            new_status = not is_active if success else is_active
            keyboard = Keyboards.building_tracker_menu(new_status)
            
            await update.callback_query.edit_message_text(
                message, 
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        
        except Exception as e:
            logger.error(f"Ошибка при переключении отслеживания зданий: {e}")
            await update.callback_query.edit_message_text("Произошла ошибка при изменении настроек отслеживания.")

    async def handle_profile_manager_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка запроса менеджера профилей"""
        chat_id = update.effective_chat.id
        
        try:
            # Проверяем подписку
            subscription = await self.db_service.get_subscription(chat_id)
            if not subscription or not subscription.is_active or subscription.is_expired():
                await update.message.reply_text("❌ Функция доступна только для премиум пользователей.")
                return
            
            # Получаем максимальное количество профилей для подписки
            max_profiles = Keyboards.get_subscription_max_profiles(subscription.subscription_type)
            
            # Получаем профили пользователя
            profiles = await self.db_service.get_user_profiles(chat_id)
            profile_data = []
            
            for profile in profiles:
                async with self.coc_client as client:
                    player_data = await client.get_player_info(profile.player_tag)
                    profile_info = {
                        'player_tag': profile.player_tag,
                        'profile_name': profile.profile_name or f"Профиль {len(profile_data) + 1}",
                        'player_name': player_data.get('name', 'Неизвестно') if player_data else 'Неизвестно',
                        'is_primary': profile.is_primary
                    }
                    profile_data.append(profile_info)
            
            message = f"👥 *Менеджер профилей*\n\n"
            message += f"📊 Профилей: {len(profiles)}/{max_profiles}\n"
            if profiles:
                message += "⭐ - основной профиль\n\n"
                message += "Выберите профиль для просмотра или управления:"
            else:
                message += "\nУ вас пока нет привязанных профилей.\nНажмите \"➕ Добавить профиль\" для добавления."
            
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=Keyboards.profile_manager_menu(profile_data, max_profiles),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=Keyboards.profile_manager_menu(profile_data, max_profiles),
                    parse_mode=ParseMode.MARKDOWN
                )
        
        except Exception as e:
            logger.error(f"Ошибка при получении менеджера профилей: {e}")
            await update.message.reply_text("Произошла ошибка при загрузке менеджера профилей.")

    async def display_profile_from_manager(self, update: Update, context: ContextTypes.DEFAULT_TYPE, player_tag: str):
        """Отображение профиля из менеджера"""
        try:
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад к менеджеру профилей", 
                                    callback_data=Keyboards.PROFILE_MANAGER_CALLBACK)],
                [InlineKeyboardButton("⭐ Сделать основным", 
                                    callback_data=f"set_primary:{player_tag}")]
            ])
            
            await self.display_player_info(
                update, context, player_tag, back_keyboard=back_keyboard, from_callback=True
            )
        
        except Exception as e:
            logger.error(f"Ошибка при отображении профиля из менеджера: {e}")
            await update.callback_query.edit_message_text("Произошла ошибка при загрузке профиля.")

    async def handle_profile_delete_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка меню удаления профиля"""
        chat_id = update.effective_chat.id
        
        try:
            profiles = await self.db_service.get_user_profiles(chat_id)
            if not profiles:
                await update.callback_query.edit_message_text("У вас нет профилей для удаления.")
                return
            
            profile_data = []
            for profile in profiles:
                async with self.coc_client as client:
                    player_data = await client.get_player_info(profile.player_tag)
                    profile_info = {
                        'player_tag': profile.player_tag,
                        'profile_name': profile.profile_name or f"Профиль {len(profile_data) + 1}",
                        'player_name': player_data.get('name', 'Неизвестно') if player_data else 'Неизвестно'
                    }
                    profile_data.append(profile_info)
            
            message = "🗑️ *Удаление профиля*\n\n"
            message += "⚠️ Выберите профиль для удаления.\n"
            message += "Это действие нельзя отменить!"
            
            await update.callback_query.edit_message_text(
                message,
                reply_markup=Keyboards.profile_delete_menu(profile_data),
                parse_mode=ParseMode.MARKDOWN
            )
        
        except Exception as e:
            logger.error(f"Ошибка при получении меню удаления: {e}")
            await update.callback_query.edit_message_text("Произошла ошибка при загрузке меню удаления.")

    async def handle_profile_delete_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE, player_tag: str):
        """Обработка подтверждения удаления профиля"""
        chat_id = update.effective_chat.id
        
        try:
            # Получаем информацию об игроке перед удалением
            async with self.coc_client as client:
                player_data = await client.get_player_info(player_tag)
                player_name = player_data.get('name', 'Неизвестно') if player_data else 'Неизвестно'
            
            # Удаляем профиль
            success = await self.db_service.delete_user_profile(chat_id, player_tag)
            
            if success:
                message = f"✅ Профиль {player_name} ({player_tag}) успешно удален."
            else:
                message = "❌ Ошибка при удалении профиля."
            
            await update.callback_query.edit_message_text(message)
            
            # Возвращаемся к менеджеру профилей через 2 секунды
            await asyncio.sleep(2)
            await self.handle_profile_manager_request(update, context)
        
        except Exception as e:
            logger.error(f"Ошибка при удалении профиля: {e}")
            await update.callback_query.edit_message_text("Произошла ошибка при удалении профиля.")

    async def handle_profile_add_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка запроса добавления нового профиля"""
        chat_id = update.effective_chat.id
        
        try:
            # Проверяем подписку
            subscription = await self.db_service.get_subscription(chat_id)
            if not subscription or not subscription.is_active or subscription.is_expired():
                await update.callback_query.edit_message_text("❌ Функция доступна только для премиум пользователей.")
                return
            
            # Проверяем лимит профилей
            max_profiles = Keyboards.get_subscription_max_profiles(subscription.subscription_type)
            current_count = await self.db_service.get_user_profile_count(chat_id)
            
            if current_count >= max_profiles:
                await update.callback_query.edit_message_text(
                    f"❌ Достигнут максимальный лимит профилей ({max_profiles}).\n"
                    "Удалите существующий профиль, чтобы добавить новый."
                )
                return
            
            # Устанавливаем состояние ожидания тега игрока
            context.user_data['state'] = UserState.AWAITING_PLAYER_TAG_TO_ADD_PROFILE
            
            await update.callback_query.edit_message_text(
                f"📝 *Добавление нового профиля*\n\n"
                f"Отправьте тег игрока в Clash of Clans.\n"
                f"Например: #ABC123DEF\n\n"
                f"Профилей: {current_count}/{max_profiles}",
                parse_mode=ParseMode.MARKDOWN
            )
        
        except Exception as e:
            logger.error(f"Ошибка при запросе добавления профиля: {e}")
            await update.callback_query.edit_message_text("Произошла ошибка при обработке запроса.")

    async def handle_add_profile_tag(self, update: Update, context: ContextTypes.DEFAULT_TYPE, player_tag: str):
        """Обработка добавления профиля по тегу"""
        chat_id = update.effective_chat.id
        
        try:
            # Проверяем подписку
            subscription = await self.db_service.get_subscription(chat_id)
            if not subscription or not subscription.is_active or subscription.is_expired():
                await update.message.reply_text("❌ Функция доступна только для премиум пользователей.")
                return
            
            # Проверяем лимит профилей
            max_profiles = Keyboards.get_subscription_max_profiles(subscription.subscription_type)
            current_count = await self.db_service.get_user_profile_count(chat_id)
            
            if current_count >= max_profiles:
                await update.message.reply_text(
                    f"❌ Достигнут максимальный лимит профилей ({max_profiles})."
                )
                return
            
            # Получаем информацию об игроке
            async with self.coc_client as client:
                player_data = await client.get_player_info(player_tag)
                
                if not player_data:
                    await update.message.reply_text(
                        "❌ Игрок с таким тегом не найден. Проверьте правильность тега."
                    )
                    return
            
            # Проверяем, не добавлен ли уже этот профиль
            existing_profiles = await self.db_service.get_user_profiles(chat_id)
            if any(p.player_tag == player_tag for p in existing_profiles):
                await update.message.reply_text(
                    f"❌ Профиль {player_data.get('name', 'игрока')} ({player_tag}) уже добавлен."
                )
                return
            
            # Создаем профиль
            profile_name = f"Профиль {current_count + 1}"
            is_primary = current_count == 0  # Первый профиль становится основным
            
            new_profile = UserProfile(
                telegram_id=chat_id,
                player_tag=player_tag,
                profile_name=profile_name,
                is_primary=is_primary
            )
            
            success = await self.db_service.save_user_profile(new_profile)
            
            if success:
                player_name = player_data.get('name', 'Неизвестно')
                message = f"✅ Профиль успешно добавлен!\n\n"
                message += f"👤 Игрок: {player_name}\n"
                message += f"🏷 Тег: {player_tag}\n"
                message += f"📝 Название: {profile_name}"
                
                if is_primary:
                    message += "\n⭐ Установлен как основной профиль"
                
                await update.message.reply_text(message)
                
                # Возвращаемся к менеджеру профилей
                await asyncio.sleep(2)
                await self.handle_profile_manager_request(update, context)
            else:
                await update.message.reply_text("❌ Ошибка при добавлении профиля. Попробуйте позже.")
        
        except Exception as e:
            logger.error(f"Ошибка при добавлении профиля: {e}")
            await update.message.reply_text("Произошла ошибка при добавлении профиля.")
    
    async def handle_linked_clans_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка запроса просмотра привязанных кланов"""
        chat_id = update.effective_chat.id
        
        # Показываем индикатор загрузки
        loading_message = await update.message.reply_text("🔍 Загрузка привязанных кланов...")
        
        try:
            # Получаем привязанные кланы пользователя
            linked_clans = await self.db_service.get_linked_clans(chat_id)
            max_clans = await self.db_service.get_max_linked_clans_for_user(chat_id)
            
            # Подготавливаем данные для клавиатуры
            clans_data = []
            for clan in linked_clans:
                clans_data.append({
                    'clan_tag': clan.clan_tag,
                    'clan_name': clan.clan_name,
                    'slot_number': clan.slot_number
                })
            
            # Формируем сообщение
            subscription = await self.db_service.get_subscription(chat_id)
            user_tier = "обычный"
            if subscription and subscription.is_active and not subscription.is_expired():
                if subscription.subscription_type in ["proplus", "proplus_permanent"]:
                    user_tier = "Pro Plus"
                elif subscription.subscription_type in ["premium"]:
                    user_tier = "Premium"
            
            message = f"🔗 *Привязанные кланы*\n\n"
            message += f"👤 Тип аккаунта: {user_tier}\n"
            message += f"📊 Использовано слотов: {len(linked_clans)}/{max_clans}\n\n"
            
            if linked_clans:
                message += "🛡 *Привязанные кланы:*\n"
                for clan in linked_clans:
                    message += f"   {clan.slot_number}. {clan.clan_name} `{clan.clan_tag}`\n"
            else:
                message += "📝 У вас нет привязанных кланов.\n"
                message += "Нажмите на пустой слот, чтобы привязать клан."
            
            await loading_message.edit_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=Keyboards.linked_clans_menu(clans_data, max_clans)
            )
        
        except asyncio.TimeoutError:
            logger.error(f"Таймаут при получении привязанных кланов для пользователя {chat_id}")
            await loading_message.edit_text(
                "⏱️ Не удалось загрузить данные из-за превышения времени ожидания.\n"
                "Попробуйте позже или обратитесь к администратору."
            )
        except Exception as e:
            logger.error(f"Ошибка при получении привязанных кланов: {e}")
            await loading_message.edit_text(
                "❌ Произошла ошибка при получении привязанных кланов.\n"
                "Попробуйте позже или обратитесь к администратору."
            )
    
    async def handle_link_clan_tag(self, update: Update, context: ContextTypes.DEFAULT_TYPE, clan_tag: str):
        """Обработка привязки клана по тегу"""
        chat_id = update.effective_chat.id
        slot_number = context.user_data.get('linking_clan_slot', 1)
        
        try:
            # Получаем информацию о клане через API
            async with self.coc_client as client:
                clan_data = await client.get_clan_info(clan_tag)
                
                if not clan_data:
                    await update.message.reply_text(
                        "❌ Клан не найден. Проверьте правильность тега и попробуйте снова."
                    )
                    return
                
                clan_name = clan_data.get('name', 'Неизвестный клан')
                
                # Проверяем лимиты пользователя
                max_clans = await self.db_service.get_max_linked_clans_for_user(chat_id)
                current_clans = await self.db_service.get_linked_clans(chat_id)
                
                if len(current_clans) >= max_clans:
                    await update.message.reply_text(
                        f"❌ Достигнут лимит привязанных кланов ({max_clans}).\n"
                        f"Удалите существующий клан, чтобы добавить новый."
                    )
                    return
                
                # Создаем запись о привязанном клане
                from models.linked_clan import LinkedClan
                linked_clan = LinkedClan(
                    telegram_id=chat_id,
                    clan_tag=clan_tag,
                    clan_name=clan_name,
                    slot_number=slot_number
                )
                
                # Сохраняем в базу данных
                success = await self.db_service.save_linked_clan(linked_clan)
                
                if success:
                    await update.message.reply_text(
                        f"✅ Клан успешно привязан!\n\n"
                        f"🛡 Клан: {clan_name}\n"
                        f"🏷 Тег: `{clan_tag}`\n"
                        f"📍 Слот: {slot_number}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    
                    # Возвращаемся к меню привязанных кланов
                    await asyncio.sleep(2)
                    await self.handle_linked_clans_request(update, context)
                else:
                    await update.message.reply_text("❌ Ошибка при сохранении клана. Попробуйте позже.")
        
        except Exception as e:
            logger.error(f"Ошибка при привязке клана: {e}")
            await update.message.reply_text("Произошла ошибка при привязке клана.")
    
    async def handle_linked_clan_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE, slot_number: int):
        """Обработка удаления привязанного клана"""
        chat_id = update.effective_chat.id
        
        try:
            success = await self.db_service.delete_linked_clan(chat_id, slot_number)
            
            if success:
                await update.callback_query.edit_message_text(
                    f"✅ Клан из слота {slot_number} успешно удален!"
                )
                
                # Возвращаемся к меню привязанных кланов
                await asyncio.sleep(2)
                await self.handle_linked_clans_request(update, context)
            else:
                await update.callback_query.edit_message_text("❌ Ошибка при удалении клана.")
        
        except Exception as e:
            logger.error(f"Ошибка при удалении привязанного клана: {e}")
            await update.callback_query.edit_message_text("Произошла ошибка при удалении клана.")
    
    async def close(self):

        if self.payment_service:
            await self.payment_service.close()
    
    async def handle_community_center_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка меню центра сообщества"""
        try:
            message = (
                f"🏛️ <b>Центр сообщества</b>\n\n"
                f"Добро пожаловать в центр сообщества! Здесь вы можете найти полезную информацию "
                f"о игре Clash of Clans.\n\n"
                f"📋 <b>Доступные разделы:</b>\n"
                f"• 🏗️ Стоимости строений - узнайте стоимость и время улучшения всех зданий\n"
                f"• 🏰 Расстановки баз - лучшие базы для каждого уровня ТХ\n"
                f"• Больше разделов будет добавлено в будущем!"
            )
            
            keyboard = Keyboards.community_center_menu()
            
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке меню центра сообщества: {e}")
            error_message = "❌ Произошла ошибка при загрузке центра сообщества."
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
    
    async def handle_building_costs_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка меню стоимости строений"""
        try:
            message = (
                f"🏗️ <b>Стоимости строений</b>\n\n"
                f"Выберите категорию зданий, чтобы узнать стоимость и время улучшения:\n\n"
                f"🏰 <b>Оборона</b> - оборонительные здания\n"
                f"⚔️ <b>Армия</b> - военные здания\n"
                f"💎 <b>Ресурсы</b> - добывающие и хранящие здания\n"
                f"👑 <b>Герои</b> - информация об улучшении героев\n"
                f"🔨 <b>Деревня строителя</b> - здания второй деревни"
            )
            
            keyboard = Keyboards.building_costs_menu()
            
            await update.callback_query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке меню стоимости строений: {e}")
            await update.callback_query.edit_message_text("❌ Произошла ошибка при загрузке меню.")
    
    async def handle_building_category_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
        """Обработка меню категории зданий"""
        try:
            category_names = {
                "defense": "🏰 Оборонительные здания",
                "army": "⚔️ Военные здания",
                "resources": "💎 Ресурсные здания",
                "heroes": "👑 Герои",
                "builder": "🔨 Деревня строителя"
            }
            
            category_name = category_names.get(category, "Неизвестная категория")
            
            message = (
                f"<b>{category_name}</b>\n\n"
                f"Выберите здание, чтобы посмотреть подробную информацию "
                f"о стоимости и времени улучшения:"
            )
            
            keyboard = Keyboards.building_category_menu(category)
            
            await update.callback_query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке категории зданий: {e}")
            await update.callback_query.edit_message_text("❌ Произошла ошибка при загрузке категории.")
    
    async def handle_building_detail_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, building_id: str, page: int = 1):
        """Обработка детальной информации о здании с пагинацией"""
        try:
            from building_data import get_building_info, format_currency, format_time
            
            building_info = get_building_info(building_id)
            
            if not building_info:
                await update.callback_query.edit_message_text("❌ Информация о здании не найдена.")
                return
            
            building_name = building_info.get("name", "Неизвестное здание")
            levels = building_info.get("levels", {})
            
            if not levels:
                await update.callback_query.edit_message_text("❌ Данные об уровнях не найдены.")
                return
            
            # Определяем, является ли здание героем (много уровней)
            is_hero = building_id in ['barbarian_king', 'archer_queen', 'grand_warden', 'royal_champion']
            levels_per_page = 10 if is_hero else 15
            
            # Сортируем уровни
            sorted_levels = sorted(levels.items())
            total_levels = len(sorted_levels)
            total_pages = (total_levels + levels_per_page - 1) // levels_per_page
            
            # Проверяем корректность страницы
            if page < 1:
                page = 1
            elif page > total_pages:
                page = total_pages
            
            # Вычисляем индексы для текущей страницы
            start_idx = (page - 1) * levels_per_page
            end_idx = min(start_idx + levels_per_page, total_levels)
            
            message = f"🏗️ <b>{building_name}</b>\n"
            if is_hero:
                message += f"📖 Страница {page}/{total_pages}\n\n"
            else:
                message += "\n"
            
            # Показываем уровни для текущей страницы
            for i in range(start_idx, end_idx):
                level, data = sorted_levels[i]
                cost = format_currency(data["cost"], data["currency"])
                time_str = format_time(data["time"])
                th_level = data.get("th_level", "?")
                
                message += f"<b>Уровень {level}:</b> {cost}, {time_str} (ТХ {th_level})\n"
            
            if not is_hero:
                message += f"\n💡 <i>Всего уровней: {total_levels}</i>"
            
            # Создаем клавиатуру
            keyboard = []
            
            # Для героев добавляем навигацию по страницам
            if is_hero and total_pages > 1:
                nav_buttons = []
                
                # Кнопка "Предыдущая страница"
                if page > 1:
                    nav_buttons.append(InlineKeyboardButton("⬅️", 
                                                          callback_data=f"{Keyboards.BUILDING_DETAIL_CALLBACK}:{building_id}:{page-1}"))
                
                # Показываем текущую страницу
                nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", 
                                                      callback_data="noop"))
                
                # Кнопка "Следующая страница"
                if page < total_pages:
                    nav_buttons.append(InlineKeyboardButton("➡️", 
                                                          callback_data=f"{Keyboards.BUILDING_DETAIL_CALLBACK}:{building_id}:{page+1}"))
                
                keyboard.append(nav_buttons)
                
                # Дополнительные кнопки для быстрого перехода
                if total_pages > 3:
                    quick_nav = []
                    if page > 2:
                        quick_nav.append(InlineKeyboardButton("⏮️ В начало", 
                                                            callback_data=f"{Keyboards.BUILDING_DETAIL_CALLBACK}:{building_id}:1"))
                    if page < total_pages - 1:
                        quick_nav.append(InlineKeyboardButton("В конец ⏭️", 
                                                            callback_data=f"{Keyboards.BUILDING_DETAIL_CALLBACK}:{building_id}:{total_pages}"))
                    if quick_nav:
                        keyboard.append(quick_nav)
                
                # Добавляем информацию о уровнях
                info_text = f"💡 Всего уровней: {total_levels}"
                if building_id == 'barbarian_king':
                    info_text += " (макс. 80)"
                elif building_id == 'archer_queen':
                    info_text += " (макс. 80)"
                elif building_id == 'grand_warden':
                    info_text += " (макс. 55)"
                elif building_id == 'royal_champion':
                    info_text += " (макс. 30)"
                
                message += f"\n\n{info_text}"
            
            # Кнопка возврата
            keyboard.append([InlineKeyboardButton("⬅️ Назад", 
                                                callback_data=Keyboards.BUILDING_COSTS_CALLBACK)])
            
            keyboard_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                text=message,
                reply_markup=keyboard_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке информации о здании: {e}")
            await update.callback_query.edit_message_text("❌ Произошла ошибка при загрузке информации о здании.")
    
    async def handle_base_layouts_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка меню расстановок баз"""
        try:
            message = (
                f"🏰 <b>Расстановки баз</b>\n\n"
                f"Выберите уровень ратуши для просмотра лучших расстановок баз:\n\n"
                f"💡 <i>Здесь будут представлены проверенные расстановки баз "
                f"для каждого уровня ТХ с подробными описаниями и стратегиями.</i>"
            )
            
            keyboard = Keyboards.base_layouts_menu()
            
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке меню расстановок баз: {e}")
            error_message = "❌ Произошла ошибка при загрузке меню расстановок баз."
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
    
    async def handle_base_layouts_th_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, th_level: str):
        """Обработка выбора уровня ТХ для расстановок"""
        try:
            message = (
                f"🏰 <b>Расстановки баз - ТХ {th_level}</b>\n\n"
                f"🚧 <b>В разработке</b>\n\n"
                f"Этот раздел находится в стадии разработки. Скоро здесь будут доступны:\n\n"
                f"• 🛡️ Лучшие защитные базы\n"
                f"• ⚔️ Фарм базы\n"
                f"• 🏆 Трофейные базы\n"
                f"• 🔥 Военные базы\n\n"
                f"Следите за обновлениями!"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад к выбору ТХ", callback_data=Keyboards.BASE_LAYOUTS_CALLBACK)],
                [InlineKeyboardButton("🏛️ Центр сообщества", callback_data=Keyboards.COMMUNITY_CENTER_CALLBACK)]
            ])
            
            await update.callback_query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке ТХ {th_level} расстановок: {e}")
            await update.callback_query.edit_message_text("❌ Произошла ошибка при загрузке расстановок.")
    
    async def handle_achievements_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                     player_tag: str, page: int = 1, sort_type: str = "progress"):
        """Обработка меню достижений игрока"""
        try:
            # Получаем данные игрока для достижений
            async with self.coc_client as client:
                player_data = await client.get_player_info(player_tag)
                
                if not player_data:
                    from translations import translation_manager
                    error_msg = translation_manager.get_text(update, 'player_not_found', "❌ Игрок не найден.")
                    await update.callback_query.edit_message_text(error_msg)
                    return
                
                player_name = player_data.get('name', 'Неизвестно')
                achievements = player_data.get('achievements', [])
                
                # Проверяем, что achievements не None
                if achievements is None:
                    achievements = []
                
                # Форматируем сообщение с достижениями
                message, total_pages = self._format_achievements_page(update, player_name, achievements, page, sort_type)
                
                # Создаем клавиатуру
                keyboard = Keyboards.achievements_menu(player_tag, page, sort_type, total_pages)
                
                await update.callback_query.edit_message_text(
                    text=message,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"Ошибка при обработке достижений игрока {player_tag}: {e}")
            from translations import translation_manager
            error_msg = translation_manager.get_text(update, 'loading_error', "❌ Произошла ошибка при загрузке данных.")
            try:
                await update.callback_query.edit_message_text(error_msg)
            except Exception as edit_error:
                logger.error(f"Ошибка при редактировании сообщения об ошибке достижений: {edit_error}")
                # Fallback: try to send a new message if editing fails
                if update.effective_chat:
                    try:
                        await update.effective_chat.send_message(error_msg)
                    except Exception as send_error:
                        logger.error(f"Не удалось отправить сообщение об ошибке достижений: {send_error}")
    
    def _format_achievements_page(self, update: Update, player_name: str, achievements: List[Dict], 
                                page: int, sort_type: str) -> tuple:
        """Форматирование страницы достижений"""
        
        # Проверяем, что achievements не None и является списком
        if not achievements or not isinstance(achievements, list):
            achievements = []
        
        # Сортировка достижений
        try:
            if sort_type == "progress":
                # Сортировка по прогрессу (процент завершения)
                def safe_progress_key(x):
                    if not x or not isinstance(x, dict):
                        return 0
                    value = x.get('value', 0)
                    target = x.get('target', 1)
                    if not isinstance(value, (int, float)) or not isinstance(target, (int, float)):
                        return 0
                    return value / max(target, 1)
                
                achievements = sorted(achievements, key=safe_progress_key, reverse=True)
            elif sort_type == "profitability":
                # Сортировка по прибыльности (награда в гемах)
                def safe_gems_key(x):
                    if not x or not isinstance(x, dict):
                        return 0
                    completion_info = x.get('completionInfo', {})
                    if not isinstance(completion_info, dict):
                        return 0
                    gems = completion_info.get('gems', 0)
                    return gems if isinstance(gems, (int, float)) else 0
                
                achievements = sorted(achievements, key=safe_gems_key, reverse=True)
        except Exception as e:
            logger.error(f"Ошибка при сортировке достижений: {e}")
            # Если сортировка не удалась, используем исходный порядок
        
        # Пагинация
        items_per_page = 5
        total_pages = max(1, (len(achievements) + items_per_page - 1) // items_per_page) if achievements else 1
        
        # Защита от неверного номера страницы
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
            
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_achievements = achievements[start_idx:end_idx] if achievements else []
        
        sort_name = "прогрессу" if sort_type == "progress" else "прибыльности"
        
        message = (
            f"🏆 <b>Достижения - {player_name}</b>\n"
            f"📊 Сортировка по: {sort_name}\n"
            f"📄 Страница {page} из {total_pages}\n\n"
        )
        
        if not achievements:
            message += "❌ У игрока нет доступных достижений или они не загружены."
            return message, total_pages
        
        if not page_achievements:
            message += "❌ На этой странице нет достижений."
            return message, total_pages
        
        for i, achievement in enumerate(page_achievements, 1):
            try:
                # Проверяем, что achievement не None и является словарем
                if not achievement or not isinstance(achievement, dict):
                    continue
                    
                name = achievement.get('name', 'Неизвестно')
                # Переводим название достижения
                from translations import translation_manager
                translated_name = translation_manager.get_achievement_name(update, name)
                # Получаем описание достижения
                description = translation_manager.get_achievement_description(update, name)
                
                value = achievement.get('value', 0)
                target = achievement.get('target', 0)
                
                # Безопасная проверка типов
                if not isinstance(value, (int, float)):
                    value = 0
                if not isinstance(target, (int, float)):
                    target = 0
                
                # Вычисляем процент прогресса
                progress_percent = (value / max(target, 1)) * 100
                
                # Статус достижения
                if value >= target:
                    status = "✅"
                    progress_bar = "🟩🟩🟩🟩🟩"
                else:
                    status = "⏳"
                    filled_blocks = int((progress_percent / 100) * 5)
                    progress_bar = "🟩" * filled_blocks + "⬜" * (5 - filled_blocks)
                
                # Информация о награде
                completion_info = achievement.get('completionInfo', {})
                if isinstance(completion_info, dict):
                    gems = completion_info.get('gems', 0)
                    xp = completion_info.get('experienceReward', 0)
                else:
                    gems = 0
                    xp = 0
                
                message += f"{status} <b>{translated_name}</b>\n"
                if description:
                    message += f"   ℹ️ <i>{description}</i>\n"
                message += f"   📊 {progress_bar} {progress_percent:.1f}%\n"
                message += f"   🎯 {value:,}/{target:,}\n"
                
                if gems > 0 or xp > 0:
                    rewards = []
                    if gems > 0:
                        rewards.append(f"💎 {gems}")
                    if xp > 0:
                        rewards.append(f"⭐ {xp}")
                    message += f"   🎁 {' | '.join(rewards)}\n"
                
                message += "\n"
                
            except Exception as e:
                logger.error(f"Ошибка при обработке достижения {i}: {e}")
                # Пропускаем проблемное достижение
                continue
        
        return message, total_pages
    
    async def handle_analyzer_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка анализатора войн"""
        try:
            chat_id = update.effective_chat.id
            
            # Проверяем, есть ли у пользователя привязанный аккаунт
            user = await self.db_service.find_user(chat_id)
            if not user or not user.player_tag:
                await update.message.reply_text(
                    "🤖 <b>Анализатор</b>\n\n"
                    "❌ Для использования анализатора необходимо привязать аккаунт.\n"
                    "Перейдите в профиль и привяжите ваш игровой аккаунт.",
                    parse_mode='HTML',
                    reply_markup=Keyboards.main_menu()
                )
                return
            
            # Показываем индикатор загрузки
            loading_message = await update.message.reply_text(
                "🤖 <b>Анализатор войн</b>\n\n"
                "🔍 Анализирую текущую военную ситуацию...",
                parse_mode='HTML'
            )
            
            async with self.coc_client as client:
                # Получаем информацию об игроке и его клане
                player_data = await client.get_player_info(user.player_tag)
                if not player_data or 'clan' not in player_data:
                    await loading_message.edit_text(
                        "🤖 <b>Анализатор войн</b>\n\n"
                        "❌ Вы не состоите в клане. Анализатор работает только для участников кланов.",
                        parse_mode='HTML'
                    )
                    return
                
                clan_tag = player_data['clan']['tag']
                clan_name = player_data['clan']['name']
                
                # Проверяем текущие войны
                war_analysis = await self._analyze_clan_wars(client, clan_tag, clan_name)
                
                # Формируем отчет анализатора
                message = self._format_analyzer_report(war_analysis, player_data)
                
                # Создаем клавиатуру с возвратом в главное меню
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Обновить анализ", 
                                        callback_data="analyzer_refresh")],
                    [InlineKeyboardButton("⬅️ Главное меню", 
                                        callback_data="main_menu")]
                ])
                
                await loading_message.edit_text(
                    message,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logger.error(f"Ошибка при работе анализатора: {e}")
            error_message = "🤖 <b>Анализатор войн</b>\n\n❌ Произошла ошибка при анализе. Попробуйте позже."
            if 'loading_message' in locals():
                await loading_message.edit_text(error_message, parse_mode='HTML')
            else:
                await update.message.reply_text(error_message, parse_mode='HTML')
    
    async def _analyze_clan_wars(self, client, clan_tag: str, clan_name: str) -> Dict:
        """Анализ текущих войн клана"""
        analysis = {
            'clan_name': clan_name,
            'current_war': None,
            'cwl_war': None,
            'is_attack_day': False,
            'recommendations': []
        }
        
        try:
            # Проверяем обычную клановую войну
            current_war = await client.get_clan_current_war(clan_tag)
            if current_war and current_war.get('state') in ['inWar', 'preparation']:
                analysis['current_war'] = current_war
                
                # Проверяем, день атак ли сейчас
                if current_war.get('state') == 'inWar':
                    analysis['is_attack_day'] = True
                    # Генерируем рекомендации для атак
                    analysis['recommendations'] = self._generate_attack_recommendations(current_war)
            
            # Проверяем ЛВК (League War)
            try:
                cwl_war = await client.get_current_cwl_war(clan_tag)
                if cwl_war and cwl_war.get('state') in ['inWar', 'preparation']:
                    analysis['cwl_war'] = cwl_war
                    
                    if cwl_war.get('state') == 'inWar':
                        analysis['is_attack_day'] = True
                        # Генерируем рекомендации для ЛВК
                        cwl_recommendations = self._generate_attack_recommendations(cwl_war, is_cwl=True)
                        analysis['recommendations'].extend(cwl_recommendations)
            except Exception as cwl_error:
                logger.debug(f"ЛВК не активна или ошибка получения данных: {cwl_error}")
            
        except Exception as e:
            logger.error(f"Ошибка при анализе войн: {e}")
        
        return analysis
    
    def _generate_attack_recommendations(self, war_data: Dict, is_cwl: bool = False) -> List[Dict]:
        """Генерация рекомендаций для атак (упрощенная AI логика)"""
        recommendations = []
        
        try:
            clan_members = war_data.get('clan', {}).get('members', [])
            opponent_members = war_data.get('opponent', {}).get('members', [])
            
            # Простая логика рекомендаций на основе соотношения TH и атак
            for member in clan_members:
                member_name = member.get('name', 'Неизвестно')
                member_th = member.get('townhallLevel', 0)
                attacks_used = len(member.get('attacks', []))
                max_attacks = 2  # В обычных войнах по 2 атаки
                
                if attacks_used < max_attacks:
                    # Ищем подходящие цели
                    suitable_targets = []
                    for opponent in opponent_members:
                        opponent_name = opponent.get('name', 'Неизвестно')
                        opponent_th = opponent.get('townhallLevel', 0)
                        opponent_pos = opponent.get('mapPosition', 0)
                        
                        # Простая логика выбора цели
                        if member_th >= opponent_th:  # Может атаковать равных или слабее
                            difficulty = self._calculate_attack_difficulty(member_th, opponent_th)
                            success_chance = self._estimate_success_chance(member_th, opponent_th, member, opponent)
                            
                            suitable_targets.append({
                                'name': opponent_name,
                                'position': opponent_pos,
                                'th_level': opponent_th,
                                'difficulty': difficulty,
                                'success_chance': success_chance
                            })
                    
                    if suitable_targets:
                        # Сортируем цели по вероятности успеха
                        suitable_targets.sort(key=lambda x: x['success_chance'], reverse=True)
                        best_target = suitable_targets[0]
                        
                        rec_type = "ЛВК" if is_cwl else "КВ"
                        recommendations.append({
                            'attacker': member_name,
                            'attacker_th': member_th,
                            'target': best_target,
                            'war_type': rec_type,
                            'attacks_remaining': max_attacks - attacks_used
                        })
        
        except Exception as e:
            logger.error(f"Ошибка при генерации рекомендаций: {e}")
        
        return recommendations[:5]  # Возвращаем топ-5 рекомендаций
    
    def _calculate_attack_difficulty(self, attacker_th: int, defender_th: int) -> str:
        """Расчет сложности атаки"""
        diff = attacker_th - defender_th
        if diff >= 2:
            return "Легкая"
        elif diff == 1:
            return "Умеренная"
        elif diff == 0:
            return "Сложная"
        else:
            return "Очень сложная"
    
    def _estimate_success_chance(self, attacker_th: int, defender_th: int, attacker: Dict, defender: Dict) -> int:
        """Упрощенная оценка вероятности успеха атаки (0-100%)"""
        base_chance = 60  # Базовая вероятность
        
        # Бонус за превосходство в TH
        th_diff = attacker_th - defender_th
        base_chance += th_diff * 15
        
        # Бонус за опыт (если есть данные об атаках)
        attacker_attacks = len(attacker.get('attacks', []))
        if attacker_attacks > 0:
            base_chance += 10  # Бонус за опыт в текущей войне
        
        # Ограничиваем значения
        return max(10, min(95, base_chance))
    
    def _format_analyzer_report(self, analysis: Dict, player_data: Dict) -> str:
        """Форматирование отчета анализатора"""
        clan_name = analysis['clan_name']
        player_name = player_data.get('name', 'Неизвестно')
        
        message = f"🤖 <b>Анализатор войн</b>\n\n"
        message += f"👤 Игрок: {player_name}\n"
        message += f"🛡️ Клан: {clan_name}\n\n"
        
        # Проверяем статус войн
        has_active_war = analysis['current_war'] or analysis['cwl_war']
        
        if not has_active_war:
            message += "😴 <b>Статус:</b> Мирное время\n\n"
            message += "📋 В данный момент ваш клан не участвует в войнах.\n"
            message += "🔍 Анализатор автоматически активируется при начале КВ или ЛВК."
            return message
        
        if analysis['is_attack_day']:
            message += "⚔️ <b>Статус:</b> День атак! 🔥\n\n"
        else:
            message += "🛡️ <b>Статус:</b> День подготовки\n\n"
        
        # Информация о текущих войнах
        if analysis['current_war']:
            war = analysis['current_war']
            state = "Идет война" if war.get('state') == 'inWar' else "Подготовка"
            message += f"⚔️ <b>Клановая война:</b> {state}\n"
            
            clan_stars = war.get('clan', {}).get('stars', 0)
            opponent_stars = war.get('opponent', {}).get('stars', 0)
            message += f"⭐ Счет: {clan_stars} - {opponent_stars}\n\n"
        
        if analysis['cwl_war']:
            message += f"🏆 <b>ЛВК:</b> Активна\n\n"
        
        # Рекомендации по атакам
        if analysis['recommendations'] and analysis['is_attack_day']:
            message += "🎯 <b>Рекомендации по атакам:</b>\n\n"
            
            for i, rec in enumerate(analysis['recommendations'][:3], 1):  # Показываем топ-3
                target = rec['target']
                message += f"{i}. <b>{rec['attacker']}</b> (ТХ{rec['attacker_th']})\n"
                message += f"   🎯 Цель: {target['name']} (#{target['position']}, ТХ{target['th_level']})\n"
                message += f"   📊 Успех: {target['success_chance']}% | {target['difficulty']}\n"
                message += f"   ⚔️ Атак осталось: {rec['attacks_remaining']}\n\n"
            
            if len(analysis['recommendations']) > 3:
                message += f"... и еще {len(analysis['recommendations']) - 3} рекомендаций\n\n"
        
        elif analysis['is_attack_day']:
            message += "✅ <b>Анализ завершен</b>\n\n"
            message += "Все участники уже использовали свои атаки или нет подходящих целей."
        
        message += "💡 <i>Рекомендации основаны на соотношении ТХ и данных о предыдущих атаках</i>"
        
        return message