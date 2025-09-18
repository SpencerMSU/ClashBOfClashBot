"""
Основной класс бота - аналог Java ClashBot
"""
import asyncio
import logging
from typing import Dict, Any
import httpx
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.constants import ParseMode
from telegram.request import HTTPXRequest

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
    
    def _create_robust_http_client(self) -> HTTPXRequest:
        """Создание HTTP клиента с улучшенной сетевой устойчивостью"""
        # Настройки для более устойчивого соединения
        limits = httpx.Limits(
            max_keepalive_connections=20,  # Увеличиваем пул соединений
            max_connections=100,
            keepalive_expiry=30.0  # Держим соединения живыми 30 секунд
        )
        
        # Настройки таймаутов
        timeout = httpx.Timeout(
            connect=10.0,      # Таймаут на установку соединения
            read=30.0,         # Таймаут на чтение ответа
            write=10.0,        # Таймаут на запись
            pool=60.0          # Общий таймаут операции
        )
        
        # Создаем HTTPXRequest с улучшенными настройками
        return HTTPXRequest(
            connection_pool_size=100,
            read_timeout=30.0,
            write_timeout=10.0,
            connect_timeout=10.0,
            pool_timeout=60.0
        )

    async def _init_components(self):
        """Инициализация компонентов бота"""
        try:
            # Инициализация базы данных
            await self.db_service.init_db()
            
            # Создание HTTP запросника с улучшенной устойчивостью
            robust_request = self._create_robust_http_client()
            
            # Создание приложения бота для проверки токена с улучшенной сетевой устойчивостью
            temp_app = Application.builder().token(self.token).request(robust_request).build()
            
            # Проверяем валидность токена перед продолжением с retry механизмом
            max_retries = 3
            retry_delay = 5  # секунды
            token_validated = False
            
            try:
                for attempt in range(max_retries):
                    try:
                        logger.info(f"Проверка токена бота (попытка {attempt + 1}/{max_retries})...")
                        await temp_app.bot.get_me()
                        logger.info("Токен бота валидный, соединение с Telegram установлено")
                        token_validated = True
                        break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            # Последняя попытка - выбрасываем исключение
                            logger.error(f"Не удается подключиться к Telegram API после {max_retries} попыток: {e}")
                            raise ValueError(f"Не удается подключиться к Telegram API: {e}")
                        else:
                            logger.warning(f"Попытка {attempt + 1} не удалась: {e}. Повтор через {retry_delay} секунд...")
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Экспоненциальная задержка
            finally:
                # Очищаем временное приложение
                await temp_app.shutdown()
            
            # Создание основного приложения бота с улучшенной сетевой устойчивостью
            main_request = self._create_robust_http_client()
            self.application = Application.builder().token(self.token).request(main_request).build()
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
            "🎮 *Добро пожаловать в ClashBot!*\n\n"
            "🏆 *Все функции бота:*\n\n"
            "👤 *ПРОФИЛИ И ИГРОКИ*\n"
            "• Привязка и управление профилями игроков\n"
            "• Просмотр детальной статистики игрока\n"
            "• Поиск игроков по тегу\n"
            "• Менеджер нескольких профилей (Премиум)\n\n"
            "🛡 *КЛАНЫ И ВОЙНЫ*\n"
            "• Информация о клане и участниках\n"
            "• История клановых войн\n"
            "• Текущие войны и ЛВК\n"
            "• Анализ атак и нарушений\n"
            "• Привязка нескольких кланов\n\n"
            "🔔 *УВЕДОМЛЕНИЯ*\n"
            "• Автоматические уведомления о войнах\n"
            "• Персональная настройка времени (Премиум)\n"
            "• Уведомления об улучшениях зданий (Премиум)\n\n"
            "💎 *ПРЕМИУМ ФУНКЦИИ*\n"
            "• 🏗️ Отслеживание улучшений зданий в реальном времени\n"
            "• 👥 Управление несколькими профилями\n"
            "• ⚙️ Расширенные настройки уведомлений\n"
            "• 📊 Дополнительная статистика\n\n"
            f"📋 [Политика использования]({get_policy_url()})\n\n"
            "Используйте меню ниже для навигации:",
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
            
            # Store building monitor in bot_data for access in handlers
            self.application.bot_data['building_monitor'] = self.building_monitor
            
            logger.info("Монитор зданий запущен")
            
        except Exception as e:
            logger.error(f"Ошибка при запуске монитора зданий: {e}")
    
    async def run(self):
        """Запуск бота с улучшенной обработкой сетевых ошибок"""
        max_restart_attempts = 5
        restart_delay = 10  # начальная задержка между перезапусками
        
        for restart_attempt in range(max_restart_attempts):
            try:
                # Initialize components first to catch configuration errors early
                await self._init_components()
                
                # Initialize the telegram application
                await self.application.initialize()
                
                # Start the application
                await self.application.start()
                
                logger.info("Запуск бота...")
                
                # Start polling with proper error handling
                await self.application.updater.start_polling(
                    allowed_updates=['message', 'callback_query'],
                    drop_pending_updates=True,
                    # Увеличиваем таймауты для более стабильной работы
                    poll_interval=2.0,  # Интервал между запросами
                    timeout=20,         # Таймаут для long polling
                    read_timeout=25,    # Таймаут чтения
                    write_timeout=25,   # Таймаут записи
                    connect_timeout=15  # Таймаут соединения
                )
                
                # Keep the bot running until interrupted
                try:
                    # This will run indefinitely until stopped
                    await asyncio.Event().wait()
                except KeyboardInterrupt:
                    logger.info("Получен сигнал завершения")
                    break  # Выходим из цикла перезапусков
                    
            except ValueError as e:
                # Validation errors (like invalid token) - don't retry
                logger.error(f"Ошибка конфигурации: {e}")
                break  # Не перезапускаем при ошибках конфигурации
                
            except Exception as e:
                logger.error(f"Ошибка при работе бота (попытка {restart_attempt + 1}/{max_restart_attempts}): {e}")
                
                # Если это не последняя попытка, пытаемся перезапустить
                if restart_attempt < max_restart_attempts - 1:
                    logger.info(f"Попытка автоматического перезапуска через {restart_delay} секунд...")
                    
                    # Очищаем состояние перед перезапуском
                    await self._cleanup()
                    
                    # Ждем перед перезапуском
                    await asyncio.sleep(restart_delay)
                    restart_delay = min(restart_delay * 2, 300)  # Экспоненциальная задержка, максимум 5 минут
                    
                    # Сбрасываем компоненты для чистого перезапуска
                    self.application = None
                    self.bot_instance = None
                    self.war_archiver = None
                    self.building_monitor = None
                else:
                    logger.error("Достигнуто максимальное количество попыток перезапуска")
                    
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
        """Безопасная очистка ресурсов с улучшенной обработкой ошибок"""
        try:
            logger.info("Завершение работы бота...")
            
            # Сначала завершаем внешние компоненты
            await self._shutdown_external_components()
            
            # Останавливаем Telegram приложение если оно запущено
            if self.application:
                try:
                    # Остановка polling если работает
                    if hasattr(self.application, 'updater') and self.application.updater:
                        if self.application.updater.running:
                            logger.info("Остановка polling...")
                            await self.application.updater.stop()
                    
                    # Остановка приложения
                    if self.application.running:
                        logger.info("Остановка приложения...")
                        await self.application.stop()
                    
                    # Финальное завершение
                    logger.info("Завершение работы приложения...")
                    await self.application.shutdown()
                    
                except Exception as e:
                    logger.error(f"Ошибка при остановке приложения: {e}")
                    # Продолжаем очистку даже при ошибках
            
            logger.info("Бот успешно завершил работу")
            
        except Exception as e:
            logger.error(f"Ошибка при завершении работы бота: {e}")
            # Не перебрасываем исключение, чтобы не прерывать завершение

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