"""
Обработчики сообщений и callback-запросов - аналог Java MessageHandler и CallbackHandler
"""
import logging
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

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
        
        # Проверяем, не является ли введенный текст командой меню
        # Если да, то очищаем состояние и обрабатываем как команду меню
        if (text == Keyboards.MY_CLAN_BTN or
            text == Keyboards.PROFILE_BTN or
            text == Keyboards.CLAN_BTN or
            text == Keyboards.BACK_BTN or
            text == Keyboards.BACK_TO_CLAN_MENU_BTN or
            text == Keyboards.NOTIFICATIONS_BTN or
            text == Keyboards.SUBSCRIPTION_BTN or
            text.startswith(Keyboards.MY_PROFILE_PREFIX)):
            # Очищаем состояние и обрабатываем как команду меню
            context.user_data.pop('state', None)
            await self._handle_menu_command(update, context, text)
            return

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
            
            elif state == UserState.AWAITING_NOTIFICATION_TIME:
                await self._handle_notification_time_input(update, context, text)
            
            elif state == UserState.AWAITING_PLAYER_TAG_TO_ADD_PROFILE:
                await self.message_generator.handle_add_profile_tag(update, context, tag)
        
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
            
            elif text == Keyboards.PROFILE_MANAGER_BTN:
                await self.message_generator.handle_profile_manager_request(update, context)
            
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
            
            elif text.startswith("🔔 Уведомление") and "(Нажмите для настройки)" in text:
                await self._handle_notification_setup(update, context, text)
            
            elif text == "✅ Включить все уведомления":
                await self._handle_enable_all_notifications(update, context)
            
            elif text == "⬅️ Назад в главное меню":
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
    
    async def _handle_notification_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Обработка настройки уведомления"""
        chat_id = update.effective_chat.id
        
        # Проверяем статус подписки
        subscription = await self.message_generator.db_service.get_subscription(chat_id)
        
        if not subscription or not subscription.is_active or subscription.is_expired():
            await update.message.reply_text(
                "❌ Настройка персональных уведомлений доступна только для премиум подписчиков.",
                reply_markup=Keyboards.main_menu()
            )
            return
        
        # Определяем номер уведомления
        if "Уведомление 1" in text:
            notification_number = 1
        elif "Уведомление 2" in text:
            notification_number = 2
        elif "Уведомление 3" in text:
            notification_number = 3
        else:
            return
        
        # Сохраняем в состояние пользователя
        context.user_data['configuring_notification'] = notification_number
        context.user_data['state'] = UserState.AWAITING_NOTIFICATION_TIME
        
        await update.message.reply_text(
            f"⚙️ Настройка уведомления {notification_number}\n\n"
            f"Введите время уведомления:\n"
            f"• Минуты: 15m, 30m, 45m\n"
            f"• Часы: 1h, 2h, 12h\n\n"
            f"⏰ Максимум: 24 часа (24h)\n"
            f"❌ Для отмены напишите 'отмена'"
        )
    
    async def _handle_enable_all_notifications(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка включения всех уведомлений"""
        chat_id = update.effective_chat.id
        
        # Проверяем статус подписки
        subscription = await self.message_generator.db_service.get_subscription(chat_id)
        
        if not subscription or not subscription.is_active or subscription.is_expired():
            await update.message.reply_text(
                "❌ Функция доступна только для премиум подписчиков.",
                reply_markup=Keyboards.main_menu()
            )
            return
        
        # Включаем базовые уведомления
        success = await self.message_generator.db_service.enable_notifications(chat_id)
        
        if success:
            await update.message.reply_text(
                "✅ Все уведомления включены!\n\n"
                "🔔 Базовые уведомления за 1 час до КВ\n"
                "⚙️ Персональные уведомления (если настроены)\n\n"
                "Вы будете получать оповещения о начале клановых войн.",
                reply_markup=Keyboards.main_menu()
            )
        else:
            await update.message.reply_text(
                "❌ Ошибка при включении уведомлений.",
                reply_markup=Keyboards.main_menu()
            )
    
    async def _handle_notification_time_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Обработка ввода времени для персонального уведомления"""
        chat_id = update.effective_chat.id
        
        if text.lower() == 'отмена':
            context.user_data.pop('configuring_notification', None)
            await update.message.reply_text(
                "❌ Настройка уведомления отменена.",
                reply_markup=Keyboards.main_menu()
            )
            return
        
        # Парсим время
        time_minutes = self._parse_notification_time(text)
        
        if time_minutes is None:
            await update.message.reply_text(
                "❌ Неверный формат времени.\n\n"
                "Используйте:\n"
                "• Минуты: 15m, 30m, 45m\n"
                "• Часы: 1h, 2h, 12h\n\n"
                "Попробуйте еще раз или напишите 'отмена':"
            )
            return
        
        if time_minutes > 1440:  # 24 часа
            await update.message.reply_text(
                "❌ Максимальное время уведомления: 24 часа.\n"
                "Попробуйте еще раз или напишите 'отмена':"
            )
            return
        
        notification_number = context.user_data.get('configuring_notification', 1)
        
        # Здесь в реальном боте нужно сохранить настройку в базу данных
        # Пока просто подтверждаем настройку
        
        time_display = self._format_time_display(time_minutes)
        
        await update.message.reply_text(
            f"✅ Уведомление {notification_number} настроено!\n\n"
            f"⏰ Время: {time_display} до начала КВ\n\n"
            f"Вы будете получать уведомление о начале клановых войн.",
            reply_markup=Keyboards.main_menu()
        )
        
        # Очищаем состояние
        context.user_data.pop('configuring_notification', None)
    
    def _parse_notification_time(self, text: str) -> Optional[int]:
        """Парсинг времени уведомления в минуты"""
        text = text.strip().lower()
        
        try:
            if text.endswith('m'):
                minutes = int(text[:-1])
                return minutes
            elif text.endswith('h'):
                hours = int(text[:-1])
                return hours * 60
            else:
                # Попробуем парсить как число минут
                return int(text)
        except ValueError:
            return None
    
    def _format_time_display(self, minutes: int) -> str:
        """Форматирование времени для отображения"""
        if minutes < 60:
            return f"{minutes} мин"
        elif minutes % 60 == 0:
            hours = minutes // 60
            return f"{hours} ч"
        else:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours} ч {mins} мин"


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
            
            elif callback_type == Keyboards.SUBSCRIPTION_EXTEND_CALLBACK:
                await self._handle_subscription_extend(update, context)
            
            elif callback_type == Keyboards.SUBSCRIPTION_PERIOD_CALLBACK:
                await self._handle_subscription_period(update, context, data_parts)
            
            elif callback_type == Keyboards.SUBSCRIPTION_TYPE_CALLBACK:
                await self._handle_subscription_type(update, context, data_parts)
            
            elif callback_type == Keyboards.SUBSCRIPTION_PAY_CALLBACK:
                await self._handle_subscription_payment(update, context, data_parts)
            
            elif callback_type == Keyboards.PREMIUM_MENU_CALLBACK:
                await self._handle_premium_menu(update, context)
            
            elif callback_type == Keyboards.NOTIFY_ADVANCED_CALLBACK:
                await self._handle_notify_advanced(update, context)
            
            elif callback_type == Keyboards.BUILDING_TRACKER_CALLBACK:
                await self._handle_building_tracker(update, context)
            
            elif callback_type == Keyboards.BUILDING_TOGGLE_CALLBACK:
                await self._handle_building_toggle(update, context)
            
            elif callback_type == Keyboards.PROFILE_MANAGER_CALLBACK:
                await self._handle_profile_manager(update, context)
            
            elif callback_type == Keyboards.PROFILE_SELECT_CALLBACK:
                await self._handle_profile_select(update, context, data_parts)
            
            elif callback_type == Keyboards.PROFILE_DELETE_CALLBACK:
                await self._handle_profile_delete_menu(update, context)
            
            elif callback_type == Keyboards.PROFILE_DELETE_CONFIRM_CALLBACK:
                await self._handle_profile_delete_confirm(update, context, data_parts)
            
            elif callback_type == Keyboards.PROFILE_ADD_CALLBACK:
                await self._handle_profile_add(update, context)
            
            elif callback_type == "confirm_payment":
                await self._handle_payment_confirmation(update, context, data_parts)
            
            elif callback_type == "clan_info":
                await self._handle_clan_info_callback(update, context)
            
            elif callback_type == "war_attacks":
                await self._handle_war_attacks(update, context, data_parts)
            
            elif callback_type == "war_violations":
                await self._handle_war_violations(update, context, data_parts)
            
            elif callback_type == "main_menu":
                await query.edit_message_text("Главное меню:")
                await query.message.reply_text("Выберите действие:", 
                                              reply_markup=Keyboards.main_menu())

            else:
                logger.warning(f"Неизвестный callback тип: {callback_type}")
                await query.edit_message_text("❌ Неизвестная команда.")

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
        """Обраб��тка детальной информации о войне"""
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
        
        # Со��даем кнопку "назад к участникам" если профиль просматривается из списка участников
        back_keyboard = None
        inspecting_clan = context.user_data.get('inspecting_clan')
        if inspecting_clan:
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад к участникам", 
                                    callback_data=Keyboards.MEMBERS_CALLBACK)],
                [InlineKeyboardButton("🛡 К информации о клане", 
                                    callback_data="clan_info")]
            ])
        
        await self.message_generator.display_player_info(
            update, context, player_tag, back_keyboard
        )
    
    async def _handle_clan_info_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обраб��тка возврат�� к информации о клане"""
        clan_tag = context.user_data.get('inspecting_clan')
        if clan_tag:
            # Получаем информацию о клане заново и отображаем
            async with self.message_generator.coc_client as client:
                clan_data = await client.get_clan_info(clan_tag)
                
                if clan_data:
                    message = self.message_generator._format_clan_info(clan_data)
                    keyboard = Keyboards.clan_inspection_menu()
                    
                    await update.callback_query.edit_message_text(
                        message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
                    )
                else:
                    await update.callback_query.edit_message_text("❌ Не удалось получить информацию о клане.")
        else:
            await update.callback_query.edit_message_text("Ошибка: клан не выбран.")
    
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
    
    async def _handle_subscription_extend(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка продления подписки"""
        await self.message_generator.handle_subscription_extend(update, context)
    
    async def _handle_subscription_period(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                         data_parts: list):
        """Обработка выбора периода подписки"""
        if len(data_parts) < 2:
            return
        
        subscription_type = data_parts[1]
        await self.message_generator.handle_subscription_period_selection(
            update, context, subscription_type
        )
    
    async def _handle_subscription_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                       data_parts: list):
        """Обработка выбора типа подписки"""
        if len(data_parts) < 2:
            return
        
        subscription_type = data_parts[1]
        await self.message_generator.handle_subscription_type_selection(
            update, context, subscription_type
        )
    
    async def _handle_subscription_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                         data_parts: list):
        """Обработка нажатия на кнопку с ценой для оплаты"""
        if len(data_parts) < 2:
            return
        
        subscription_type = data_parts[1]
        await self.message_generator.handle_subscription_payment_confirmation(
            update, context, subscription_type
        )
    
    async def _handle_premium_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка премиум меню"""
        await self.message_generator.handle_premium_menu(update, context)
    
    async def _handle_notify_advanced(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка расширенных настроек уведомлений"""
        await self.message_generator.handle_advanced_notifications(update, context)
    
    async def _handle_building_tracker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка меню отслеживания зданий"""
        await self.message_generator.handle_building_tracker_menu(update, context)
    
    async def _handle_building_toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка переключения отслеживания зданий"""
        await self.message_generator.handle_building_tracker_toggle(update, context)
    
    async def _handle_payment_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                         data_parts: list):
        """Обработка подтверждения платежа"""
        if len(data_parts) < 2:
            return
        
        subscription_type = data_parts[1]
        await self.message_generator.handle_subscription_period_selection(
            update, context, subscription_type
        )
    
    async def _handle_war_attacks(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                 data_parts: list):
        """Обработка статистики атак войны"""
        if len(data_parts) < 3:
            return
        
        clan_tag = data_parts[1]
        war_end_time = data_parts[2]
        
        await self.message_generator.display_war_attacks(
            update, context, clan_tag, war_end_time
        )
    
    async def _handle_war_violations(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   data_parts: list):
        """Обработка нарушений войны"""
        if len(data_parts) < 3:
            return
        
        clan_tag = data_parts[1]
        war_end_time = data_parts[2]
        
        await self.message_generator.display_war_violations(
            update, context, clan_tag, war_end_time
        )

    async def _handle_profile_manager(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка открытия менеджера профилей"""
        await self.message_generator.handle_profile_manager_request(update, context)

    async def _handle_profile_select(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   data_parts: list):
        """Обработка выбора профиля"""
        if len(data_parts) < 2:
            return
        
        player_tag = data_parts[1]
        await self.message_generator.display_profile_from_manager(update, context, player_tag)

    async def _handle_profile_delete_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка открытия меню удаления профиля"""
        await self.message_generator.handle_profile_delete_menu(update, context)

    async def _handle_profile_delete_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                           data_parts: list):
        """Обработка подтверждения удаления профиля"""
        if len(data_parts) < 2:
            return
        
        player_tag = data_parts[1]
        await self.message_generator.handle_profile_delete_confirm(update, context, player_tag)

    async def _handle_profile_add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка добавления нового профиля"""
        await self.message_generator.handle_profile_add_request(update, context)