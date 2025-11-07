"""Конфигурация бота - аналог Java BotConfig"""
import os


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
        raw_database_url = api_tokens.get('DATABASE_URL', '') or os.getenv('DATABASE_URL', '')
        raw_database_path = api_tokens.get('DATABASE_PATH', '') or os.getenv('DATABASE_PATH', '')

        # Дополнительные параметры подключения для PostgreSQL
        self.DATABASE_HOST: str = (
            api_tokens.get('DATABASE_HOST', '') or os.getenv('DATABASE_HOST', '') or 'localhost'
        )
        self.DATABASE_PORT: str = (
            api_tokens.get('DATABASE_PORT', '') or os.getenv('DATABASE_PORT', '') or '5432'
        )
        self.DATABASE_USER: str = (
            api_tokens.get('DATABASE_USER', '') or os.getenv('DATABASE_USER', '') or 'postgres'
        )
        self.DATABASE_PASSWORD: str = api_tokens.get('DATABASE_PASSWORD', '') or os.getenv(
            'DATABASE_PASSWORD', ''
        )
        raw_database_name = api_tokens.get('DATABASE_NAME', '') or os.getenv('DATABASE_NAME', '')

        self.DATABASE_URL: str = self._resolve_database_url(
            database_url=raw_database_url,
            database_path=raw_database_path,
            database_name=raw_database_name,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            user=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
        )

        # Настройки клана
        self.OUR_CLAN_TAG: str = os.getenv('OUR_CLAN_TAG', '#2PQU0PLJ2')

        # Настройки API
        self.COC_API_BASE_URL: str = 'https://api.clashofclans.com/v1'

        # Настройки архивации
        self.ARCHIVE_CHECK_INTERVAL: int = int(os.getenv('ARCHIVE_CHECK_INTERVAL', '900'))  # 15 минут
        self.DONATION_SNAPSHOT_INTERVAL: int = int(os.getenv('DONATION_SNAPSHOT_INTERVAL', '21600'))  # 6 часов

        # Валидация обязательных параметров
        self._validate_config()

    @staticmethod
    def _resolve_database_url(
        database_url: str,
        database_path: str,
        database_name: str,
        host: str,
        port: str,
        user: str,
        password: str,
    ) -> str:
        """Определение итоговой строки подключения к базе данных."""
        if database_url:
            return database_url

        if database_path and '://' in database_path:
            return database_path

        db_name = database_name or database_path or ''
        if db_name.endswith('.db'):
            db_name = db_name[:-3]
        db_name = db_name or 'clashbot'

        host = host or 'localhost'
        port = port or '5432'
        user = user or ''
        password = password or ''

        auth_part = ''
        if user:
            auth_part = user
            if password:
                auth_part += f":{password}"
            auth_part += '@'

        port_part = f":{port}" if port else ''
        return f"postgresql://{auth_part}{host}{port_part}/{db_name}"

    def _validate_config(self):
        """Проверка обязательных параметров конфигурации"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменные окружения")
        if not self.COC_API_TOKEN:
            raise ValueError("COC_API_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменные окружения")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL не установлен. Укажите строку подключения к PostgreSQL в api_tokens.txt или переменных окружения")


# Глобальный экземпляр конфигурации
config = BotConfig()
