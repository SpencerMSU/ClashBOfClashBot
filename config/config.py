"""
Конфигурация бота - аналог Java BotConfig
"""
import os
from typing import Optional


def _read_api_tokens(filename: str = 'api_tokens.txt') -> dict:
    """Чтение API токенов из текстового файла"""
    tokens = {}
    
    try:
        # Сначала ищем файл в текущей директории
        if os.path.exists(filename):
            filepath = filename
        else:
            # Если не найден, ищем в корневой директории проекта (на уровень выше config)
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(script_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Пропускаем комментарии и пустые строки
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            tokens[key.strip()] = value.strip()
        
    except Exception as e:
        print(f"Ошибка при чтении файла токенов {filename}: {e}")
    
    return tokens


class BotConfig:
    """Конфигурация бота"""
    
    def __init__(self):
        # Читаем токены из файла
        api_tokens = _read_api_tokens()
        
        # Основные токены и настройки (сначала пробуем файл, потом переменные окружения)
        self.BOT_TOKEN: str = api_tokens.get('BOT_TOKEN', '') or os.getenv('BOT_TOKEN', '')
        self.BOT_USERNAME: str = api_tokens.get('BOT_USERNAME', '') or os.getenv('BOT_USERNAME', '')
        self.COC_API_TOKEN: str = api_tokens.get('COC_API_TOKEN', '') or os.getenv('COC_API_TOKEN', '')
        
        # YooKassa платежные реквизиты
        self.YOOKASSA_SHOP_ID: str = api_tokens.get('YOOKASSA_SHOP_ID', '') or os.getenv('YOOKASSA_SHOP_ID', '')
        self.YOOKASSA_SECRET_KEY: str = api_tokens.get('YOOKASSA_SECRET_KEY', '') or os.getenv('YOOKASSA_SECRET_KEY', '')
        
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
            raise ValueError("BOT_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменные окружения")
        if not self.COC_API_TOKEN:
            raise ValueError("COC_API_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменные окружения")


# Глобальный экземпляр конфигурации
config = BotConfig()