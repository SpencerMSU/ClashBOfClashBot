"""
Обработчики сообщений и callback-запросов для Python версии бота Clash of Clans.

Этот модуль содержит всю логику обработки пользовательских взаимодействий,
портированную с Java версии бота с использованием асинхронного программирования.

Основные компоненты:
1. MessageHandler - обработка текстовых сообщений и команд
2. CallbackHandler - обработка callback-запросов от inline-кнопок
3. Вспомогательные утилиты для обработки данных

Функциональность:
- Асинхронная обработка всех запросов
- Обработка тегов игроков и кланов
- Управление состояниями пользователей
- Отображение информации о клане и игроках
- Работа с войнами и ЛВК
- Управление уведомлениями

Пример использования:
    from bot.handlers import setup_handlers
    
    # В main.py
    app = Application.builder().token(TOKEN).build()
    setup_handlers(app, bot_instance, message_generator)
    app.run_polling()
"""

import logging
from typing import TYPE_CHECKING, Dict, Any
import re

# Импорты локальных модулей
from .user_state import UserState
from .war_sort import WarSort
from .keyboards import Keyboards
from .handlers.message_handler import MessageHandler
from .handlers.callback_handler import CallbackHandler

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes, Application

logger = logging.getLogger(__name__)


class BotHandlers:
    """
    Основной класс для управления всеми обработчиками бота.
    
    Объединяет MessageHandler и CallbackHandler в единый интерфейс
    для упрощения использования и настройки.
    """
    
    def __init__(self, bot_instance, message_generator):
        """
        Инициализация обработчиков.
        
        Args:
            bot_instance: Экземпляр бота
            message_generator: Генератор сообщений
        """
        self.bot = bot_instance
        self.message_generator = message_generator
        
        # Создаем экземпляры обработчиков
        self.message_handler = MessageHandler(bot_instance, message_generator)
        self.callback_handler = CallbackHandler(bot_instance, message_generator)
        
        logger.info("BotHandlers инициализирован")
    
    async def handle_message(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE") -> None:
        """
        Обработка входящих сообщений.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
        """
        await self.message_handler.handle(update, context)
    
    async def handle_callback(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE") -> None:
        """
        Обработка callback-запросов.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
        """
        await self.callback_handler.handle(update, context)


def setup_handlers(application: "Application", bot_instance, message_generator) -> BotHandlers:
    """
    Настройка и регистрация всех обработчиков в приложении.
    
    Args:
        application: Экземпляр Telegram Application
        bot_instance: Экземпляр бота
        message_generator: Генератор сообщений
        
    Returns:
        Экземпляр BotHandlers для дополнительного управления
    """
    # Создаем главный объект обработчиков
    handlers = BotHandlers(bot_instance, message_generator)
    
    # Импортируем необходимые классы для регистрации
    from telegram.ext import MessageHandler as TGMessageHandler, CallbackQueryHandler
    from telegram.ext import filters
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(
        TGMessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handlers.handle_message
        )
    )
    
    # Регистрируем обработчик команд
    application.add_handler(
        TGMessageHandler(
            filters.COMMAND,
            handlers.handle_message
        )
    )
    
    # Регистрируем обработчик callback-запросов
    application.add_handler(
        CallbackQueryHandler(handlers.handle_callback)
    )
    
    logger.info("Все обработчики зарегистрированы в приложении")
    return handlers


def validate_clan_tag(tag: str) -> bool:
    """
    Валидация тега клана по правилам Clash of Clans.
    
    Args:
        tag: Тег для проверки
        
    Returns:
        True если тег валиден, False иначе
    """
    if not tag or len(tag) < 4:
        return False
    
    # Убираем # в начале для проверки
    clean_tag = tag[1:] if tag.startswith('#') else tag
    
    # Проверяем длину (обычно 8-9 символов)
    if len(clean_tag) < 3 or len(clean_tag) > 9:
        return False
    
    # Проверяем на допустимые символы (буквы, цифры)
    if not re.match(r'^[A-Z0-9]+$', clean_tag):
        return False
    
    return True


def validate_player_tag(tag: str) -> bool:
    """
    Валидация тега игрока по правилам Clash of Clans.
    
    Args:
        tag: Тег для проверки
        
    Returns:
        True если тег валиден, False иначе
    """
    return validate_clan_tag(tag)  # Используем те же правила


def process_tag(text: str) -> str:
    """
    Обработка и нормализация тега игрока или клана.
    
    Args:
        text: Исходный текст
        
    Returns:
        Обработанный и нормализованный тег
    """
    # Удаляем пробелы и приводим к верхнему регистру
    tag = text.strip().upper()
    
    # Заменяем часто путаемые символы
    tag = tag.replace('O', '0').replace('І', 'I').replace('Ӏ', 'I')
    
    # Добавляем # в начало если его нет
    if not tag.startswith('#'):
        tag = '#' + tag
    
    return tag


# Экспорт основных классов и функций
__all__ = [
    'BotHandlers',
    'MessageHandler', 
    'CallbackHandler',
    'setup_handlers',
    'validate_clan_tag',
    'validate_player_tag', 
    'process_tag',
    'UserState',
    'WarSort',
    'Keyboards'
]