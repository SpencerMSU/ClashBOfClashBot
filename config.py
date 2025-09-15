"""
Конфигурация бота - аналог Java BotConfig
"""
import os
from typing import Optional


class BotConfig:
    """Конфигурация бота"""
    
    def __init__(self):
        # Основные токены и настройки
        self.BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
        self.BOT_USERNAME: str = os.getenv('BOT_USERNAME', '')
        self.COC_API_TOKEN: str = os.getenv('COC_API_TOKEN', '')
        
        # Настройки базы данных
        self.DATABASE_PATH: str = os.getenv('DATABASE_PATH', 'clashbot.db')
        
        # Настройки клана
        self.OUR_CLAN_TAG: str = os.getenv('OUR_CLAN_TAG', '#2PQU0PLJ2')
        
        # Настройки API
        self.COC_API_BASE_URL: str = 'https://api.clashofclans.com/v1'
        
        # Настройки архивации
        self.ARCHIVE_CHECK_INTERVAL: int = int(os.getenv('ARCHIVE_CHECK_INTERVAL', '900'))  # 15 минут
        self.DONATION_SNAPSHOT_INTERVAL: int = int(os.getenv('DONATION_SNAPSHOT_INTERVAL', '21600'))  # 6 часов
        
        # Валидация обязательных параметров
        self._validate_config()
    
    def _validate_config(self):
        """Проверка обязательных параметров конфигурации"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен в переменных окружения")
        if not self.COC_API_TOKEN:
            raise ValueError("COC_API_TOKEN не установлен в переменных окружения")


# Глобальный экземпляр конфигурации
config = BotConfig()