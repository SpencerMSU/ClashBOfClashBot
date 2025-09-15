"""
Обработчик текстовых сообщений для бота Clash of Clans.
"""
import logging
from typing import TYPE_CHECKING

from ..user_state import UserState
from ..keyboards import Keyboards

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class MessageHandler:
    """
    Класс для обработки текстовых сообщений и команд.
    """
    
    def __init__(self, bot, message_generator):
        """
        Инициализация обработчика сообщений.
        
        Args:
            bot: Экземпляр бота
            message_generator: Генератор сообщений
        """
        self.bot = bot
        self.message_generator = message_generator
    
    async def handle(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE") -> None:
        """
        Асинхронная обработка входящего сообщения.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
        """
        if not update.message or not update.message.text:
            return
            
        chat_id = update.message.chat_id
        text = update.message.text
        user_state = context.user_data.get('state')
        
        logger.info(f"Обработка сообщения от {chat_id}: {text}")
        
        if user_state is None:
            await self._handle_menu_commands(update, context, chat_id, text)
            return
        
        # Обработка пользовательского ввода в зависимости от состояния
        tag = self._process_tag(text)
        
        try:
            if user_state == UserState.AWAITING_PLAYER_TAG_TO_LINK:
                await self.message_generator.handle_link_account(chat_id, tag)
            elif user_state == UserState.AWAITING_PLAYER_TAG_TO_SEARCH:
                await self.message_generator.display_player_info(chat_id, tag, None)
            elif user_state == UserState.AWAITING_CLAN_TAG_TO_SEARCH:
                await self.message_generator.display_clan_info(chat_id, tag)
        except Exception as e:
            logger.error(f"Ошибка обработки состояния {user_state}: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Произошла ошибка при обработке запроса. Попробуйте еще раз."
            )
        finally:
            # Очищаем состояние пользователя
            context.user_data.pop('state', None)
    
    async def _handle_menu_commands(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE", 
                                   chat_id: int, text: str) -> None:
        """
        Обработка команд меню.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            chat_id: ID чата
            text: Текст сообщения
        """
        if text.startswith(Keyboards.MY_PROFILE_PREFIX):
            await self.message_generator.handle_my_profile_request(chat_id)
            return
        
        try:
            if text == "/start":
                context.user_data.pop('inspecting_clan', None)
                await self.bot.send_main_menu(chat_id, "Добро пожаловать!")
                
            elif text == Keyboards.PROFILE_BTN:
                await self.message_generator.handle_profile_menu_request(chat_id)
                
            elif text in [Keyboards.CLAN_BTN, Keyboards.BACK_TO_CLAN_MENU_BTN]:
                context.user_data.pop('inspecting_clan', None)
                await self.bot.send_clan_menu(chat_id, "Меню клана:")
                
            elif text == Keyboards.MY_CLAN_BTN:
                await self.message_generator.handle_my_clan_request(chat_id)
                
            elif text == Keyboards.CLAN_MEMBERS_BTN:
                clan_tag = context.user_data.get('inspecting_clan')
                if clan_tag:
                    await self.message_generator.display_members_page(
                        chat_id, None, clan_tag, 0, "rank", "home"
                    )
                    
            elif text == Keyboards.CLAN_WARLOG_BTN:
                clan_tag = context.user_data.get('inspecting_clan')
                if clan_tag:
                    await self.bot.send_war_history_sort_menu(
                        chat_id, "Выберите, как отобразить историю войн:", clan_tag
                    )
                    
            elif text == Keyboards.CLAN_CURRENT_WAR_BTN:
                clan_tag = context.user_data.get('inspecting_clan')
                if clan_tag:
                    await self.message_generator.handle_current_war_request(chat_id, clan_tag)
                    
            elif text == Keyboards.CLAN_CURRENT_CWL_BTN:
                clan_tag = context.user_data.get('inspecting_clan')
                if clan_tag:
                    await self.message_generator.handle_current_cwl_request(chat_id, clan_tag)
                    
            elif text == Keyboards.CLAN_CWL_BONUS_BTN:
                await self.bot.send_cwl_bonus_menu(
                    chat_id, "🏆 Выберите месяц для подсчета бонусов ЛВК:"
                )
                
            elif text == Keyboards.NOTIFICATIONS_BTN:
                await self.message_generator.handle_notification_menu(chat_id)
                
            elif text == Keyboards.LINK_ACC_BTN:
                context.user_data['state'] = UserState.AWAITING_PLAYER_TAG_TO_LINK
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="Отправьте мне ваш тег игрока (например, 2V99V8J0)."
                )
                
            elif text == Keyboards.SEARCH_PROFILE_BTN:
                context.user_data['state'] = UserState.AWAITING_PLAYER_TAG_TO_SEARCH
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="Отправьте тег игрока для поиска."
                )
                
            elif text == Keyboards.SEARCH_CLAN_BTN:
                context.user_data['state'] = UserState.AWAITING_CLAN_TAG_TO_SEARCH
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="Отправьте тег клана для поиска."
                )
                
            elif text == Keyboards.BACK_BTN:
                context.user_data.pop('inspecting_clan', None)
                await self.bot.send_main_menu(chat_id, "Добро пожаловать!")
                
        except Exception as e:
            logger.error(f"Ошибка обработки команды меню '{text}': {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Произошла ошибка при обработке команды. Попробуйте еще раз."
            )
    
    def _process_tag(self, text: str) -> str:
        """
        Обработка и валидация тега игрока или клана.
        
        Args:
            text: Исходный текст
            
        Returns:
            Обработанный тег
        """
        # Удаляем пробелы, приводим к верхнему регистру, заменяем O на 0
        tag = text.strip().upper().replace('O', '0')
        
        # Добавляем # в начало, если его нет
        if not tag.startswith("#"):
            tag = "#" + tag
            
        return tag