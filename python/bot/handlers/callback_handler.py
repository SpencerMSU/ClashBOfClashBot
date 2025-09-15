"""
Обработчик callback-запросов для бота Clash of Clans.
"""
import logging
from typing import TYPE_CHECKING

from ..keyboards import Keyboards
from ..war_sort import WarSort

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class CallbackHandler:
    """
    Класс для обработки callback-запросов от inline-кнопок.
    """
    
    def __init__(self, bot, message_generator):
        """
        Инициализация обработчика callback-запросов.
        
        Args:
            bot: Экземпляр бота
            message_generator: Генератор сообщений
        """
        self.bot = bot
        self.message_generator = message_generator
    
    async def handle(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE") -> None:
        """
        Асинхронная обработка callback-запроса.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
        """
        query = update.callback_query
        
        if not query or not query.data:
            return
            
        # Подтверждаем получение callback-запроса
        await query.answer()
        
        # Игнорируем "noop" callback
        if query.data == "noop":
            return
        
        # Парсим данные callback
        data = query.data.split(":")
        if len(data) < 2:
            logger.warning(f"Неверный формат callback данных: {query.data}")
            return
        
        callback_type = data[0]
        chat_id = query.message.chat_id
        message_id = query.message.message_id
        
        logger.info(f"Обработка callback от {chat_id}: {query.data}")
        
        try:
            await self._process_callback(callback_type, data, chat_id, message_id)
        except Exception as e:
            logger.error(f"Ошибка обработки callback '{query.data}': {e}")
            # Опционально отправляем сообщение об ошибке пользователю
            await context.bot.send_message(
                chat_id=chat_id,
                text="Произошла ошибка при обработке запроса. Попробуйте еще раз."
            )
    
    async def _process_callback(self, callback_type: str, data: list, 
                               chat_id: int, message_id: int) -> None:
        """
        Обработка различных типов callback-запросов.
        
        Args:
            callback_type: Тип callback-запроса
            data: Данные callback-запроса
            chat_id: ID чата
            message_id: ID сообщения
        """
        if callback_type == Keyboards.MEMBERS_SORT_CALLBACK:
            await self._handle_members_sort_callback(data, chat_id, message_id)
            
        elif callback_type == Keyboards.WAR_LIST_CALLBACK:
            await self._handle_war_list_callback(data, chat_id, message_id)
            
        elif callback_type == Keyboards.WAR_INFO_CALLBACK:
            await self._handle_war_info_callback(data, chat_id, message_id)
            
        elif callback_type == Keyboards.PROFILE_CALLBACK:
            await self._handle_profile_callback(data, chat_id)
            
        elif callback_type == Keyboards.NOTIFY_TOGGLE_CALLBACK:
            await self._handle_notification_toggle_callback(chat_id, message_id)
            
        elif callback_type == Keyboards.CWL_BONUS_CALLBACK:
            await self._handle_cwl_bonus_callback(data, chat_id, message_id)
            
        else:
            logger.warning(f"Неизвестный тип callback: {callback_type}")
    
    async def _handle_members_sort_callback(self, data: list, chat_id: int, message_id: int) -> None:
        """
        Обработка callback для сортировки участников клана.
        
        Args:
            data: Данные callback-запроса
            chat_id: ID чата
            message_id: ID сообщения
        """
        if len(data) < 5:
            logger.error(f"Недостаточно данных для members_sort callback: {data}")
            return
            
        clan_tag = data[1]
        sort_type = data[2]
        view_type = data[3]
        
        try:
            page = int(data[4])
        except ValueError:
            logger.error(f"Неверный номер страницы: {data[4]}")
            return
            
        await self.message_generator.display_members_page(
            chat_id, message_id, clan_tag, page, sort_type, view_type
        )
    
    async def _handle_war_list_callback(self, data: list, chat_id: int, message_id: int) -> None:
        """
        Обработка callback для списка войн.
        
        Args:
            data: Данные callback-запроса
            chat_id: ID чата
            message_id: ID сообщения
        """
        if len(data) < 4:
            logger.error(f"Недостаточно данных для war_list callback: {data}")
            return
            
        clan_tag = data[1]
        
        try:
            sort_order = WarSort(data[2])
            page = int(data[3])
        except (ValueError, KeyError):
            logger.error(f"Неверные данные для war_list callback: {data[2:]}")
            return
            
        await self.message_generator.display_war_list_page(
            chat_id, message_id, clan_tag, sort_order, page
        )
    
    async def _handle_war_info_callback(self, data: list, chat_id: int, message_id: int) -> None:
        """
        Обработка callback для информации о войне.
        
        Args:
            data: Данные callback-запроса
            chat_id: ID чата
            message_id: ID сообщения
        """
        if len(data) < 3:
            logger.error(f"Недостаточно данных для war_info callback: {data}")
            return
            
        clan_tag = data[1]
        war_end_time = data[2]
        
        await self.message_generator.display_single_war_details(
            chat_id, message_id, clan_tag, war_end_time
        )
    
    async def _handle_profile_callback(self, data: list, chat_id: int) -> None:
        """
        Обработка callback для отображения профиля игрока.
        
        Args:
            data: Данные callback-запроса
            chat_id: ID чата
        """
        if len(data) < 2:
            logger.error(f"Недостаточно данных для profile callback: {data}")
            return
            
        player_tag = data[1]
        
        await self.message_generator.display_player_info(
            chat_id, player_tag, None  # Используем clan inspection menu
        )
    
    async def _handle_notification_toggle_callback(self, chat_id: int, message_id: int) -> None:
        """
        Обработка callback для переключения уведомлений.
        
        Args:
            chat_id: ID чата
            message_id: ID сообщения
        """
        await self.message_generator.handle_notification_toggle(chat_id, message_id)
    
    async def _handle_cwl_bonus_callback(self, data: list, chat_id: int, message_id: int) -> None:
        """
        Обработка callback для бонусов ЛВК.
        
        Args:
            data: Данные callback-запроса
            chat_id: ID чата
            message_id: ID сообщения
        """
        if len(data) < 2:
            logger.error(f"Недостаточно данных для cwl_bonus callback: {data}")
            return
            
        year_month = data[1]
        
        await self.message_generator.handle_cwl_bonus_request(
            chat_id, message_id, year_month
        )