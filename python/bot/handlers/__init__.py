"""
Главный модуль обработчиков для бота Clash of Clans.

Содержит:
- MessageHandler: Обработка текстовых сообщений и команд
- CallbackHandler: Обработка callback-запросов от inline-кнопок
- Вспомогательные функции для регистрации обработчиков

Использование:
    from bot.handlers import setup_handlers
    
    # В main.py бота
    setup_handlers(application, bot_instance, message_generator)
"""
import logging
from typing import TYPE_CHECKING

from .message_handler import MessageHandler
from .callback_handler import CallbackHandler

if TYPE_CHECKING:
    from telegram.ext import Application

logger = logging.getLogger(__name__)


def setup_handlers(application: "Application", bot_instance, message_generator) -> None:
    """
    Настройка и регистрация всех обработчиков бота.
    
    Args:
        application: Экземпляр Telegram Application
        bot_instance: Экземпляр бота
        message_generator: Генератор сообщений
    """
    # Создаем экземпляры обработчиков
    message_handler = MessageHandler(bot_instance, message_generator)
    callback_handler = CallbackHandler(bot_instance, message_generator)
    
    # Регистрируем обработчики
    from telegram.ext import MessageHandler as TGMessageHandler, CallbackQueryHandler
    from telegram import Update
    from telegram.ext import filters
    
    # Обработчик текстовых сообщений
    application.add_handler(
        TGMessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler.handle
        )
    )
    
    # Обработчик команд (включая /start)
    application.add_handler(
        TGMessageHandler(
            filters.COMMAND,
            message_handler.handle
        )
    )
    
    # Обработчик callback-запросов
    application.add_handler(
        CallbackQueryHandler(callback_handler.handle)
    )
    
    logger.info("Все обработчики успешно зарегистрированы")


# Экспортируем основные классы для прямого использования
__all__ = [
    'MessageHandler',
    'CallbackHandler', 
    'setup_handlers'
]