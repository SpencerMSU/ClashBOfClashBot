"""
Обработчики сообщений и callback-запросов - аналог Java MessageHandler и CallbackHandler
"""
import logging
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from keyboards import Keyboards, WarSort, MemberSort, MemberView
from user_state import UserState
from message_generator import MessageGenerator
from coc_api import format_clan_tag, format_player_tag

logger = logging.getLogger(__name__)


class MessageHandler:
    """Обработчик текстовых сообщений"""
    
    def __init__(self, message_generator: MessageGenerator):
        self.message_generator = message_generator
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстового сообщения"""
        if not update.message or not update.message.text:
            return
        
        chat_id = update.effective_chat.id
        text = update.message.text.strip()
        
        # Получаем состояние пользователя
        user_state = context.user_data.get('state')
        
        if user_state:
            await self._handle_state_message(update, context, text, user_state)
        else:
            await self._handle_menu_command(update, context, text)
    
    async def _handle_state_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   text: str, state: UserState):
        """Обработка сообщения в состоянии ожидания ввода"""
        chat_id = update.effective_chat.id
        
        # Форматируем тег
        tag = format_player_tag(text) if 'PLAYER' in state.value else format_clan_tag(text)
        
        try:
            if state == UserState.AWAITING_PLAYER_TAG_TO_LINK:
                await self.message_generator.handle_link_account(update, context, tag)
            
            elif state == UserState.AWAITING_PLAYER_TAG_TO_SEARCH:
                await self.message_generator.display_player_info(update, context, tag, 
                                                                Keyboards.clan_inspection_menu())
            
            elif state == UserState.AWAITING_CLAN_TAG_TO_SEARCH:
                await self.message_generator.display_clan_info(update, context, tag)
        
        except Exception as e:
            logger.error(f"Ошибка при обработке состояния {state}: {e}")
            await update.message.reply_text("Произошла ошибка при обработке запроса.")
        
        finally:
            # Очищаем состояние
            context.user_data.pop('state', None)
    
    async def _handle_menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Обработка команд главного меню"""
        chat_id = update.effective_chat.id
        
        try:
            if text.startswith(Keyboards.MY_PROFILE_PREFIX):
                await self.message_generator.handle_my_profile_request(update, context)
            
            elif text == Keyboards.PROFILE_BTN:
                await self.message_generator.handle_profile_menu_request(update, context)
            
            elif text == Keyboards.CLAN_BTN:
                await update.message.reply_text("Меню клана:", 
                                               reply_markup=Keyboards.clan_menu())
            
            elif text == Keyboards.LINK_ACC_BTN:
                context.user_data['state'] = UserState.AWAITING_PLAYER_TAG_TO_LINK
                await update.message.reply_text(
                    "Отправьте тег вашего игрока в Clash of Clans.\n"
                    "Например: #ABC123DEF"
                )
            
            elif text == Keyboards.SEARCH_PROFILE_BTN:
                context.user_data['state'] = UserState.AWAITING_PLAYER_TAG_TO_SEARCH
                await update.message.reply_text(
                    "Отправьте тег игрока для поиска.\n"
                    "Например: #ABC123DEF"
                )
            
            elif text == Keyboards.MY_CLAN_BTN:
                await self.message_generator.handle_my_clan_request(update, context)
            
            elif text == Keyboards.SEARCH_CLAN_BTN:
                context.user_data['state'] = UserState.AWAITING_CLAN_TAG_TO_SEARCH
                await update.message.reply_text(
                    "Отправьте тег клана для поиска.\n"
                    "Например: #ABC123DEF"
                )
            
            elif text == Keyboards.NOTIFICATIONS_BTN:
                await self.message_generator.handle_notifications_menu(update, context)
            
            elif text == Keyboards.SUBSCRIPTION_BTN:
                await self.message_generator.handle_subscription_menu(update, context)
            
            elif text == Keyboards.BACK_BTN or text == Keyboards.BACK_TO_CLAN_MENU_BTN:
                await update.message.reply_text("Главное меню:", 
                                               reply_markup=Keyboards.main_menu())
            
            elif text == "/start":
                await update.message.reply_text(
                    "🎮 Добро пожаловать в бота для Clash of Clans!\n\n"
                    "Этот бот поможет вам:\n"
                    "• Просматривать профили игроков\n"
                    "• Получать информацию о кланах\n"
                    "• Отслеживать войны и статистику\n"
                    "• Получать уведомления о клановых войнах\n\n"
                    "Выберите действие в меню ниже:",
                    reply_markup=Keyboards.main_menu()
                )
            
            else:
                await update.message.reply_text(
                    "Команда не распознана. Используйте кнопки меню.",
                    reply_markup=Keyboards.main_menu()
                )
        
        except Exception as e:
            logger.error(f"Ошибка при обработке команды меню '{text}': {e}")
            await update.message.reply_text(
                "Произошла ошибка при обработке команды.",
                reply_markup=Keyboards.main_menu()
            )


class CallbackHandler:
    """Обработчик callback-запросов"""
    
    def __init__(self, message_generator: MessageGenerator):
        self.message_generator = message_generator
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback-запроса"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "noop":
            return
        
        data_parts = query.data.split(":")
        if len(data_parts) < 2:
            return
        
        callback_type = data_parts[0]
        chat_id = query.message.chat_id
        message_id = query.message.message_id
        
        try:
            if callback_type == Keyboards.MEMBERS_CALLBACK:
                await self._handle_members_callback(update, context)
            
            elif callback_type == Keyboards.MEMBERS_SORT_CALLBACK:
                await self._handle_members_sort(update, context, data_parts)
            
            elif callback_type == Keyboards.MEMBERS_VIEW_CALLBACK:
                await self._handle_members_view(update, context, data_parts)
            
            elif callback_type == Keyboards.WAR_LIST_CALLBACK:
                await self._handle_war_list(update, context, data_parts)
            
            elif callback_type == Keyboards.WAR_INFO_CALLBACK:
                await self._handle_war_info(update, context, data_parts)
            
            elif callback_type == Keyboards.PROFILE_CALLBACK:
                await self._handle_profile_callback(update, context, data_parts)
            
            elif callback_type == Keyboards.NOTIFY_TOGGLE_CALLBACK:
                await self.message_generator.handle_notification_toggle(update, context, message_id)
            
            elif callback_type == Keyboards.CWL_BONUS_CALLBACK:
                await self._handle_cwl_bonus(update, context, data_parts)
            
            elif callback_type == "current_war":
                await self._handle_current_war(update, context)
            
            elif callback_type == "cwl_info":
                await self._handle_cwl_info(update, context)
            
            elif callback_type == Keyboards.SUBSCRIPTION_CALLBACK:
                await self._handle_subscription_menu(update, context)
            
            elif callback_type == Keyboards.SUBSCRIPTION_PERIOD_CALLBACK:
                await self._handle_subscription_period(update, context, data_parts)
            
            elif callback_type == "main_menu":
                await query.edit_message_text("Главное меню:")
                await query.message.reply_text("Выберите действие:", 
                                              reply_markup=Keyboards.main_menu())
        
        except Exception as e:
            logger.error(f"Ошибка при обработке callback '{query.data}': {e}")
            await query.edit_message_text("Произошла ошибка при обработке запроса.")
    
    async def _handle_members_sort(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                  data_parts: list):
        """Обработка сортировки участников"""
        if len(data_parts) < 5:
            return
        
        clan_tag = data_parts[1]
        sort_type = data_parts[2]
        view_type = data_parts[3]
        page = int(data_parts[4])
        
        await self.message_generator.display_members_page(
            update, context, clan_tag, page, sort_type, view_type
        )
    
    async def _handle_members_view(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                  data_parts: list):
        """Обработка изменения вида участников"""
        if len(data_parts) < 5:
            return
        
        clan_tag = data_parts[1]
        sort_type = data_parts[2]
        view_type = data_parts[3]
        page = int(data_parts[4])
        
        await self.message_generator.display_members_page(
            update, context, clan_tag, page, sort_type, view_type
        )
    
    async def _handle_war_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                              data_parts: list):
        """Обработка списка войн"""
        # Handle initial war list button click (just "warlist")
        if len(data_parts) == 1:
            clan_tag = context.user_data.get('inspecting_clan')
            if clan_tag:
                await self.message_generator.display_war_list_page(
                    update, context, clan_tag, sort_order="recent", page=1
                )
            else:
                await update.callback_query.edit_message_text("Ошибка: клан не выбран.")
            return
        
        # Handle pagination and sorting (warlist:clan_tag:sort_order:page)
        if len(data_parts) < 4:
            return
        
        clan_tag = data_parts[1]
        sort_order = data_parts[2]
        page = int(data_parts[3])
        
        await self.message_generator.display_war_list_page(
            update, context, clan_tag, sort_order, page
        )
    
    async def _handle_war_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                              data_parts: list):
        """Обработка детальной информации о войне"""
        if len(data_parts) < 3:
            return
        
        clan_tag = data_parts[1]
        war_end_time = data_parts[2]
        
        await self.message_generator.display_single_war_details(
            update, context, clan_tag, war_end_time
        )
    
    async def _handle_profile_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                      data_parts: list):
        """Обработка профиля игрока"""
        if len(data_parts) < 2:
            return
        
        player_tag = data_parts[1]
        await self.message_generator.display_player_info(
            update, context, player_tag, Keyboards.clan_inspection_menu()
        )
    
    async def _handle_cwl_bonus(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               data_parts: list):
        """Обработка бонусов ЛВК"""
        if len(data_parts) < 2:
            return
        
        year_month = data_parts[1]
        await self.message_generator.display_cwl_bonus_info(update, context, year_month)
    
    async def _handle_members_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка просмотра участников клана"""
        # Получаем тег клана из контекста
        clan_tag = context.user_data.get('inspecting_clan')
        if clan_tag:
            # Отображаем первую страницу участников с сортировкой по роли по умолчанию
            await self.message_generator.display_members_page(
                update, context, clan_tag, page=1, sort_type="role", view_type="compact"
            )
        else:
            await update.callback_query.edit_message_text("Ошибка: клан не выбран.")
    
    async def _handle_current_war(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текущей войны"""
        # Получаем тег клана из контекста
        clan_tag = context.user_data.get('inspecting_clan')
        if clan_tag:
            await self.message_generator.display_current_war(update, context, clan_tag)
        else:
            await update.callback_query.edit_message_text("Ошибка: клан не выбран.")
    
    async def _handle_cwl_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка информации о ЛВК"""
        # Получаем тег клана из контекста
        clan_tag = context.user_data.get('inspecting_clan')
        if clan_tag:
            await self.message_generator.display_cwl_info(update, context, clan_tag)
        else:
            await update.callback_query.edit_message_text("Ошибка: клан не выбран.")
    
    async def _handle_subscription_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка меню подписки"""
        await self.message_generator.handle_subscription_menu(update, context)
    
    async def _handle_subscription_period(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                         data_parts: list):
        """Обработка выбора периода подписки"""
        if len(data_parts) < 2:
            return
        
        subscription_type = data_parts[1]
        await self.message_generator.handle_subscription_period_selection(
            update, context, subscription_type
        )