"""
Основной класс бота - аналог Java ClashBot
"""
import asyncio
import logging
from typing import Dict, Any
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.constants import ParseMode

from config import config
from database import DatabaseService
from coc_api import CocApiClient
from handlers import MessageHandler as BotMessageHandler, CallbackHandler as BotCallbackHandler
from message_generator import MessageGenerator
from war_archiver import WarArchiver
from building_monitor import BuildingMonitor
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
        
        # Монитор зданий
        self.building_monitor = None
        
        # Приложение Telegram
        self.application = None
        self.bot_instance = None
    
    async def initialize(self):
        """Инициализация бота"""
        await self._init_components()
        
        # Создание приложения бота
        self.application = Application.builder().token(self.token).build()
        self.bot_instance = self.application.bot
        
        # Регистрация обработчиков
        self._register_handlers()
        
        logger.info("Бот успешно инициализирован")
    
    async def _init_components(self):
        """Инициализация компонентов бота"""
        try:
            # Инициализация базы данных
            await self.db_service.init_db()
            
            # Создание приложения бота для проверки токена
            temp_app = Application.builder().token(self.token).build()
            
            # Проверяем валидность токена перед продолжением
            try:
                await temp_app.bot.get_me()
            except Exception as e:
                logger.error(f"Неверный токен бота или проблемы с сетью: {e}")
                raise ValueError(f"Не удается подключиться к Telegram API: {e}")
            finally:
                # Очищаем временное приложение
                await temp_app.shutdown()
            
            # Создание основного приложения бота
            self.application = Application.builder().token(self.token).build()
            self.bot_instance = self.application.bot
            
            # Регистрация обработчиков
            self._register_handlers()
            
            # Запуск архиватора войн
            await self._start_war_archiver()
            
            # Запуск монитора зданий
            await self._start_building_monitor()
            
            logger.info("Компоненты бота успешно инициализированы")
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации компонентов бота: {e}")
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
        # Проверяем, есть ли параметр команды (например, payment_success)
        if context.args:
            command_arg = context.args[0]
            if command_arg.startswith('payment_success'):
                await self._handle_payment_success(update, context, command_arg)
                return
        
        from policy import get_policy_url
        
        await update.message.reply_text(
            "🎮 Добро пожаловать в бота для Clash of Clans!\n\n"
            "Этот бот поможет вам:\n"
            "• Просматривать профили игроков\n"
            "• Получать информацию о кланах\n"
            "• Отслеживать войны и статистику\n"
            "• Получать уведомления о клановых войнах\n\n"
            f"📋 [Политика использования и возвратов]({get_policy_url()})\n\n"
            "Используя бота, вы соглашаетесь с политикой использования.\n\n"
            "Выберите действие в меню ниже:",
            reply_markup=Keyboards.main_menu(),
            parse_mode='Markdown'
        )
    
    async def _handle_payment_success(self, update, context, command_arg):
        """Обработка успешного платежа"""
        chat_id = update.effective_chat.id
        
        # Извлекаем тип подписки из параметра
        subscription_type = command_arg.replace('payment_success_', '') if '_' in command_arg else None
        
        # Получаем информацию о подписке пользователя
        subscription = await self.db_service.get_subscription(chat_id)
        
        if subscription and subscription.is_active and not subscription.is_expired():
            subscription_name = self.message_generator.payment_service.get_subscription_name(subscription.subscription_type)
            end_date = subscription.end_date.strftime('%d.%m.%Y %H:%M')
            
            success_message = (
                f"✅ <b>Платеж успешно обработан!</b>\n\n"
                f"🎉 Подписка <b>{subscription_name}</b> активирована\n"
                f"📅 Действует до: {end_date}\n"
                f"💰 Сумма: {subscription.amount:.0f} ₽\n\n"
                f"Спасибо за покупку! Теперь вам доступны все премиум функции."
            )
            
            await update.message.reply_text(
                success_message,
                parse_mode=ParseMode.HTML,
                reply_markup=Keyboards.main_menu()
            )
        else:
            await update.message.reply_text(
                "❌ Не удалось найти активную подписку.\n"
                "Если платеж был произведен, подписка будет активирована в течение нескольких минут.",
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
    
    async def _start_building_monitor(self):
        """Запуск монитора зданий"""
        try:
            self.building_monitor = BuildingMonitor(
                db_service=self.db_service,
                coc_client=self.coc_client,
                bot_instance=self.bot_instance
            )
            await self.building_monitor.start()
            logger.info("Монитор зданий запущен")
            
        except Exception as e:
            logger.error(f"Ошибка при запуске монитора зданий: {e}")
    
    async def run(self):
        """Запуск бота"""
        try:
            # Initialize components first to catch configuration errors early
            await self._init_components()
            
            # Initialize the telegram application
            await self.application.initialize()
            
            # Start the application
            await self.application.start()
            
            # Store building monitor in bot_data for access in handlers
            self.application.bot_data['building_monitor'] = self.building_monitor
            
            logger.info("Запуск бота...")
            # Start polling with proper lifecycle management
            await self.application.updater.start_polling(
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True
            )
            
            # Keep the bot running until interrupted
            try:
                # This will run indefinitely until stopped
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                logger.info("Получен сигнал завершения")
                
        except ValueError as e:
            # Validation errors (like invalid token) - don't initialize application
            logger.error(f"Ошибка конфигурации: {e}")
        except Exception as e:
            logger.error(f"Ошибка при работе бота: {e}")
        finally:
            # Always ensure proper cleanup
            await self._cleanup()
    
    async def _shutdown_external_components(self):
        """Завершение работы внешних компонентов (не управляемых application)"""
        try:
            logger.info("Завершение работы внешних компонентов...")
            
            # Остановка архиватора
            if self.war_archiver:
                await self.war_archiver.stop()
            
            # Остановка монитора зданий
            if self.building_monitor:
                await self.building_monitor.stop()
            
            # Закрытие клиента COC API
            if hasattr(self.coc_client, 'close'):
                await self.coc_client.close()
            
            # Закрытие сервиса платежей
            if hasattr(self.message_generator, 'close'):
                await self.message_generator.close()
            
            logger.info("Внешние компоненты успешно завершили работу")
            
        except Exception as e:
            logger.error(f"Ошибка при завершении работы внешних компонентов: {e}")

    async def _cleanup(self):
        """Безопасная очистка ресурсов"""
        try:
            logger.info("Завершение работы бота...")
            
            # Сначала завершаем внешние компоненты
            await self._shutdown_external_components()
            
            # Останавливаем Telegram приложение если оно запущено
            if self.application:
                try:
                    if hasattr(self.application, 'updater') and self.application.updater.running:
                        await self.application.updater.stop()
                    
                    if self.application.running:
                        await self.application.stop()
                    
                    await self.application.shutdown()
                except Exception as e:
                    logger.error(f"Ошибка при остановке приложения: {e}")
            
            logger.info("Бот успешно завершил работу")
            
        except Exception as e:
            logger.error(f"Ошибка при завершении работы бота: {e}")

    async def shutdown(self):
        """Завершение работы бота (для обратной совместимости)"""
        await self._cleanup()
    
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