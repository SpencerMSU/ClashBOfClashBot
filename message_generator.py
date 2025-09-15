"""
Генератор сообщений - аналог Java MessageGenerator
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database import DatabaseService
from coc_api import CocApiClient, format_clan_tag, format_player_tag
from keyboards import Keyboards, WarSort, MemberSort, MemberView
from models.user import User
from models.subscription import Subscription
from payment_service import YooKassaService
from config import config

logger = logging.getLogger(__name__)


class MessageGenerator:
    """Генератор сообщений и форматирование данных"""
    
    def __init__(self, db_service: DatabaseService, coc_client: CocApiClient):
        self.db_service = db_service
        self.coc_client = coc_client
        self.payment_service = YooKassaService()
        
        # Константы для форматирования
        self.MEMBERS_PER_PAGE = 10
        self.WARS_PER_PAGE = 10
        
        self.ROLE_TRANSLATIONS = {
            "leader": "👑 Глава",
            "coLeader": "⚜️ Соруководитель", 
            "admin": "🔰 Старейшина",
            "member": "👤 Участник"
        }
    
    async def handle_profile_menu_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка запроса меню профиля"""
        chat_id = update.effective_chat.id
        
        try:
            user = await self.db_service.find_user(chat_id)
            if user:
                async with self.coc_client as client:
                    player_data = await client.get_player_info(user.player_tag)
                    player_name = player_data.get('name') if player_data else None
                    
                    await update.message.reply_text(
                        "Меню профиля:",
                        reply_markup=Keyboards.profile_menu(player_name)
                    )
            else:
                await update.message.reply_text(
                    "Меню профиля:",
                    reply_markup=Keyboards.profile_menu(None)
                )
        except Exception as e:
            logger.error(f"Ошибка при получении меню профиля: {e}")
            await update.message.reply_text(
                "Меню профиля:",
                reply_markup=Keyboards.profile_menu(None)
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
                                 player_tag: str, keyboard: InlineKeyboardMarkup = None):
        """Отображение информации об игроке"""

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
            
            # Редактируем сообщение поиска на информацию об игроке
            if keyboard:
                await search_message.edit_text(
                    message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            else:
                await search_message.edit_text(
                    message,
                    parse_mode=ParseMode.MARKDOWN
                )
    
    async def display_clan_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, clan_tag: str):
        """Отображение информации о клане"""
        async with self.coc_client as client:
            clan_data = await client.get_clan_info(clan_tag)
            
            if not clan_data:
                await update.message.reply_text(
                    "❌ Клан с таким тегом не найден.",
                    reply_markup=Keyboards.main_menu()
                )
                return
            
            # Сохраняем тег клана для дальнейшего использования
            context.user_data['inspecting_clan'] = clan_tag
            
            # Форматируем информацию о ��лане
            message = self._format_clan_info(clan_data)
            keyboard = Keyboards.clan_inspection_menu()
            
            await update.message.reply_text(
                message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
            )
    
    async def display_members_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  clan_tag: str, page: int, sort_type: str, view_type: str):
        """Отображение страницы участников клана"""
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
    
    async def handle_notifications_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка меню уведомлений"""
        chat_id = update.effective_chat.id
        
        # Проверяем текущий статус уведомлений
        subscribed_users = await self.db_service.get_subscribed_users()
        is_subscribed = chat_id in subscribed_users
        
        status_text = "включены" if is_subscribed else "отключены"
        message = f"🔔 Уведомления о клановых войнах: *{status_text}*\n\n" \
                 f"Нажмите кнопку ниже для изменения настроек."
        
        await update.message.reply_text(
            message, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=Keyboards.notification_toggle()
        )
    
    async def handle_notification_toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                       message_id: int):
        """Переключение уведомлений"""
        chat_id = update.effective_chat.id
        
        is_enabled = await self.db_service.toggle_notifications(chat_id)
        
        status_text = "включены" if is_enabled else "отключены"
        message = f"🔔 Уведомления о клановых войнах: *{status_text}*\n\n" \
                 f"Нажмите кнопку ниже для изменения настроек."
        
        await update.callback_query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=Keyboards.notification_toggle()
        )
    
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
        
        if builder_hall_level > 0:
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
            
            # Add clan level if available
            clan_level = clan_info.get('clanLevel', 0)
            if clan_level > 0:
                message += f"\n🎖️ Уровень клана: {clan_level}"
        else:
            message += f"\n🚫 Не состоит в клане"
        
        return message
    
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
            name = member.get('name', 'Неизвестно')
            tag = member.get('tag', 'Неизвестно')
            role = member.get('role', 'member')
            role_text = self.ROLE_TRANSLATIONS.get(role, '👤 Участник')
            trophies = member.get('trophies', 0)
            
            if view_type == MemberView.DETAILED:
                donations = member.get('donations', 0)
                received = member.get('donationsReceived', 0)
                
                message += f"**{i + (page-1) * self.MEMBERS_PER_PAGE}.** {name}\n"
                message += f"   🏷 `{tag}`\n"
                message += f"   👑 {role_text}\n"
                message += f"   🏆 {trophies:,} трофеев\n"
                message += f"   📤 Отдано: {donations:,}\n"
                message += f"   📥 Получено: {received:,}\n\n"
            else:
                message += f"**{i + (page-1) * self.MEMBERS_PER_PAGE}.** {role_text} {name} - 🏆 {trophies:,}\n"
        
        return message
    
    def _format_war_list(self, wars: List[Dict], page: int, total_pages: int) -> str:
        """Форматирование списка войн"""
        message = f"⚔️ *История войн* (стр. {page}/{total_pages})\n\n"
        
        for i, war in enumerate(wars, 1):
            opponent_name = war['opponent_name']
            team_size = war['team_size']
            clan_stars = war['clan_stars']
            opponent_stars = war['opponent_stars']
            result = war['result']
            is_cwl = war['is_cwl_war']
            
            result_emoji = {"win": "🏆", "lose": "❌", "tie": "🤝"}.get(result, "❓")
            war_type = "🏆 ЛВК" if is_cwl else "⚔️ КВ"
            
            message += f"**{i}.** {result_emoji} vs {opponent_name}\n"
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
                message = (
                    f"💎 <b>Ваша премиум подписка</b>\n\n"
                    f"📅 Тип: {self.payment_service.get_subscription_name(subscription.subscription_type)}\n"
                    f"⏰ Действует до: {subscription.end_date.strftime('%d.%m.%Y %H:%M')}\n"
                    f"📊 Дней осталось: {subscription.days_remaining()}\n\n"
                    f"Хотите продлить премиум подписку?"
                )
                keyboard = Keyboards.subscription_status()
            else:
                # У пользователя нет активной подписки
                message = (
                    f"💎 <b>Премиум подписка</b>\n\n"
                    f"🚀 <b>Активируйте премиум и получите:</b>\n\n"
                    f"✨ <b>Эксклюзивные возможности:</b>\n"
                    f"• 🔥 Приоритетная поддержка\n"
                    f"• 📊 Расширенная статистика войн\n"
                    f"• 🔔 Персональные уведомления\n"
                    f"• 🎯 Дополнительные инструменты\n"
                    f"• 🛡️ Премиум функции клана\n\n"
                    f"💰 <b>Выберите период активации:</b>"
                )
                keyboard = Keyboards.subscription_periods()
            
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
    
    async def handle_subscription_period_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                                  subscription_type: str):
        """Обработка выбора периода подписки"""
        chat_id = update.effective_chat.id
        
        try:
            # Создаем платеж в YooKassa
            payment_data = await self.payment_service.create_payment(
                telegram_id=chat_id,
                subscription_type=subscription_type,
                return_url=f"https://t.me/your_bot?start=payment_success"
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
                # Отправляем уведомление пользователю (нужен доступ к боту)
                logger.info(f"Подписка успешно обработана для пользователя {telegram_id}")
                # В реальном боте здесь отправляется сообщение пользователю
            else:
                logger.error(f"Ошибка при сохранении подписки для пользователя {telegram_id}")
        
        except Exception as e:
            logger.error(f"Ошибка при обработке успешного платежа: {e}")
    
    async def display_current_war(self, update: Update, context: ContextTypes.DEFAULT_TYPE, clan_tag: str):
        """Отображение информации о текущей войне клана"""
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
        
        except Exception as e:
            logger.error(f"Ошибка при получении информации о текущей войне: {e}")
            await update.callback_query.edit_message_text(
                "❌ Произошла ошибка при получении информации о войне."
            )
    
    async def display_cwl_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, clan_tag: str):
        """Отображение информации о Лиге войн кланов (CWL)"""
        try:
            async with self.coc_client as client:
                cwl_data = await client.get_clan_war_league_group(clan_tag)
                
                if not cwl_data:
                    await update.callback_query.edit_message_text(
                        "❌ Клан не участвует в текущем сезоне ЛВК."
                    )
                    return
                
                # Format CWL information
                message = self._format_cwl_info(cwl_data)
                
                await update.callback_query.edit_message_text(
                    message, parse_mode=ParseMode.MARKDOWN
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
                message += f"🕐 Начало войны: {start_time}\n"
        elif state == 'inWar':
            end_time = war_data.get('endTime')
            if end_time:
                message += f"🕐 Конец войны: {end_time}\n"
        
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
    
    async def close(self):
        """Закрытие ресурсов"""
        if self.payment_service:
            await self.payment_service.close()