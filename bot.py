"""
Основной класс бота - аналог Java ClashBot
"""
import logging
from typing import Dict, Any
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from config import config
from database import DatabaseService
from coc_api import CocApiClient
from handlers import MessageHandler as BotMessageHandler, CallbackHandler as BotCallbackHandler
from message_generator import MessageGenerator
from war_archiver import WarArchiver
from keyboards import Keyboards

logger = logging.getLogger(__name__)


class ClashBot:
    """Основной класс Telegram бота для Clash of Clans"""
    
    def __init__(self):
        # Инициализация компонентов
        self.token = config.BOT_TOKEN
        self.db_service = DatabaseService()
        self.coc_client = CocApiClient()
        self.message_generator = MessageGenerator(self.db_service, self.coc_client)
        
        # Обработчики
        self.message_handler = BotMessageHandler(self.message_generator)
        self.callback_handler = BotCallbackHandler(self.message_generator)
        
        # Архиватор войн
        self.war_archiver = None
        
        # Приложение Telegram
        self.application = None
        self.bot_instance = None
    
    async def initialize(self):
        """Инициализация бота"""
        try:
            # Инициализация базы данных
            await self.db_service.init_db()
            
            # Создание приложения бота
            self.application = Application.builder().token(self.token).build()
            self.bot_instance = self.application.bot
            
            # Регистрация обработчиков
            self._register_handlers()
            
            # Запуск архиватора войн
            await self._start_war_archiver()
            
            logger.info("Бот успешно инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации бота: {e}")
            raise
    
    def _register_handlers(self):
        """Регистрация обработчиков команд и сообщений"""
        app = self.application
        
        # Команда /start
        app.add_handler(CommandHandler("start", self._start_command))
        
        # Обработчик текстовых сообщений
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.message_handler.handle_message
        ))
        
        # Обработчик callback-запросов
        app.add_handler(CallbackQueryHandler(self.callback_handler.handle_callback))
    
    async def _start_command(self, update, context):
        """Обработчик команды /start"""
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
    
    async def _start_war_archiver(self):
        """Запуск архиватора войн"""
        try:
            self.war_archiver = WarArchiver(
                clan_tag=config.OUR_CLAN_TAG,
                db_service=self.db_service,
                coc_client=self.coc_client,
                bot_instance=self.bot_instance
            )
            await self.war_archiver.start()
            logger.info(f"Архиватор войн запущен для клана {config.OUR_CLAN_TAG}")
            
        except Exception as e:
            logger.error(f"Ошибка при запуске архиватора войн: {e}")
    
    async def run(self):
        """Запуск бота"""
        try:
            await self.initialize()
            
            logger.info("Запуск бота...")
            await self.application.run_polling(
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True
            )
            
        except KeyboardInterrupt:
            logger.info("Получен сигнал завершения")
        except Exception as e:
            logger.error(f"Ошибка при работе бота: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Завершение работы бота"""
        try:
            logger.info("Завершение работы бота...")
            
            # Остановка архиватора
            if self.war_archiver:
                await self.war_archiver.stop()
            
            # Закрытие клиента COC API
            if hasattr(self.coc_client, 'close'):
                await self.coc_client.close()
            
            # Закрытие сервиса платежей
            if hasattr(self.message_generator, 'close'):
                await self.message_generator.close()
            
            # Остановка приложения
            if self.application:
                await self.application.shutdown()
            
            logger.info("Бот успешно завершил работу")
            
        except Exception as e:
            logger.error(f"Ошибка при завершении работы бота: {e}")
    
    async def send_message(self, chat_id: int, text: str, reply_markup=None, parse_mode=None):
        """Отправка сообщения"""
        if self.bot_instance:
            await self.bot_instance.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
    
    async def edit_message(self, chat_id: int, message_id: int, text: str, 
                          reply_markup=None, parse_mode=None):
        """Редактирование сообщения"""
        if self.bot_instance:
            await self.bot_instance.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )