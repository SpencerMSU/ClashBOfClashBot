"""
Генератор сообщений - аналог Java MessageGenerator
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database import DatabaseService
from coc_api import CocApiClient, format_clan_tag, format_player_tag
from keyboards import Keyboards, WarSort, MemberSort, MemberView
from models.user import User
from config import config

logger = logging.getLogger(__name__)


class MessageGenerator:
    """Генератор сообщений и форматирование данных"""
    
    def __init__(self, db_service: DatabaseService, coc_client: CocApiClient):
        self.db_service = db_service
        self.coc_client = coc_client
        
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
        
        await self.display_player_info(update, context, user.player_tag, 
                                     Keyboards.clan_inspection_menu())
    
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
        async with self.coc_client as client:
            player_data = await client.get_player_info(player_tag)
            
            if not player_data:
                await update.message.reply_text(
                    "❌ Игрок с таким тегом не найден.",
                    reply_markup=Keyboards.main_menu()
                )
                return
            
            # Форматируем информацию об игроке
            message = self._format_player_info(player_data)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
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
            
            # Форматируем информацию о клане
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
            keyboard = Keyboards.members_pagination(clan_tag, page, total_pages, sort_type, view_type)
            
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
        
        # Форматируем сообщение
        message = self._format_war_list(filtered_wars, page, total_pages)
        keyboard = Keyboards.war_list_pagination(clan_tag, page, total_pages, sort_order)
        
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