#!/bin/bash

# Скрипт полной проверки и инициализации базы данных

echo "🔍 ПОЛНАЯ ПРОВЕРКА И ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ"
echo "=================================================="

cd "$(dirname "$0")"

# Активация виртуального окружения
if [ -d "venv" ]; then
    echo "📦 Активация виртуального окружения..."
    source venv/bin/activate
fi

echo "📍 Текущая папка: $(pwd)"

# Проверка и создание БД через Python
echo ""
echo "🐍 Инициализация БД через Python..."

python3 -c "
import asyncio
import sys
import os

# Добавление пути к проекту
sys.path.insert(0, '.')

try:
    from src.services.database import DatabaseService
    from config.config import config
    
    async def init_database():
        print('🗄️ Создание DatabaseService...')
        db_service = DatabaseService()
        
        print(f'📂 Путь к БД: {os.path.abspath(db_service.db_path)}')
        
        # Проверка папки
        db_dir = os.path.dirname(os.path.abspath(db_service.db_path))
        if not os.path.exists(db_dir):
            print(f'❌ Папка не существует: {db_dir}')
            return False
            
        if not os.access(db_dir, os.W_OK):
            print(f'❌ Нет прав на запись в папку: {db_dir}')
            return False
            
        print('✅ Папка доступна для записи')
        
        # Инициализация БД
        print('🔧 Инициализация базы данных...')
        await db_service.init_db()
        
        print('✅ База данных успешно инициализирована!')
        return True
    
    # Запуск инициализации
    result = asyncio.run(init_database())
    
    if result:
        print('🎉 Инициализация завершена успешно!')
    else:
        print('❌ Ошибка при инициализации')
        sys.exit(1)
        
except Exception as e:
    print(f'💥 Критическая ошибка: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🧪 Проверка структуры БД..."
    
    # Проверка таблиц
    sqlite3 clashbot.db "
    .mode column
    .headers on
    
    SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;
    " 2>/dev/null || {
        echo "❌ Ошибка доступа к SQLite"
        exit 1
    }
    
    echo ""
    echo "📊 Статистика таблиц:"
    
    # Подсчет записей в основных таблицах
    for table in users wars attacks linked_clans subscriptions buildings; do
        count=$(sqlite3 clashbot.db "SELECT COUNT(*) FROM $table" 2>/dev/null || echo "0")
        echo "   📋 $table: $count записей"
    done
    
    echo ""
    echo "🎉 БАЗА ДАННЫХ ГОТОВА К РАБОТЕ!"
    echo "✅ Все таблицы созданы"
    echo "✅ Индексы установлены"
    echo "✅ Права доступа корректны"
    echo ""
    echo "🚀 Теперь можно запустить Ultra Scanner:"
    echo "   python scripts/all_importer.py"
    
else
    echo ""
    echo "❌ ОШИБКА ИНИЦИАЛИЗАЦИИ БД"
    echo "💡 Проверьте права доступа и запустите снова"
    exit 1
fi