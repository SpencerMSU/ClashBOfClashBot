"""
Конфигурация для NoSQL базы данных
"""
import os
from config.config import config as original_config

# Патч для использования NoSQL вместо SQLite
original_config.USE_NOSQL = True
original_config.NOSQL_DIR = os.getenv('NOSQL_DIR', 'nosql_db')

# Экспорт обновленной конфигурации
config = original_config