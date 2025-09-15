"""
Точка входа в приложение - аналог Java Main
"""
import asyncio
import logging
import os
import sys

from bot import ClashBot
from config import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция приложения"""
    try:
        logger.info("Запуск бота Clash of Clans...")
        
        # Проверяем переменные окружения
        if not config.BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменную окружения BOT_TOKEN.")
            return
        
        if not config.COC_API_TOKEN:
            logger.error("COC_API_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменную окружения COC_API_TOKEN.")
            return
        
        # Создание и запуск бота
        bot = ClashBot()
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Запуск бота
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Программа завершена пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        sys.exit(1)