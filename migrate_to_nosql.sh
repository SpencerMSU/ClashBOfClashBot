#!/bin/bash

# Скрипт перехода с SQLite на NoSQL

echo "🔄 ПЕРЕХОД НА NOSQL DATABASE"
echo "=============================="

cd "$(dirname "$0")"

# Активация виртуального окружения
if [ -d "venv" ]; then
    echo "📦 Активация виртуального окружения..."
    source venv/bin/activate
fi

echo "📍 Текущая папка: $(pwd)"

# Остановка всех процессов
echo ""
echo "🛑 Остановка всех процессов..."
pkill -f "python.*main.py" 2>/dev/null || echo "main.py не запущен"
pkill -f "python.*all_importer.py" 2>/dev/null || echo "all_importer.py не запущен"

# Очистка SQLite блокировок
echo ""
echo "🧹 Очистка SQLite файлов..."
rm -f clashbot.db-wal clashbot.db-shm

# Backup старой БД если существует
if [ -f "clashbot.db" ]; then
    backup_name="sqlite_backup_$(date +%Y%m%d_%H%M%S).db"
    cp clashbot.db "$backup_name"
    echo "💾 SQLite backup создан: $backup_name"
fi

# Создание NoSQL папки
echo ""
echo "📁 Создание NoSQL структуры..."
mkdir -p nosql_db
echo "✅ Папка nosql_db создана"

# Тестирование NoSQL
echo ""
echo "🧪 Тестирование NoSQL системы..."

python3 -c "
import asyncio
import sys
import os

# Добавление пути к проекту
sys.path.insert(0, '.')

try:
    from src.services.nosql_database import NoSQLDatabaseService
    
    async def test_nosql():
        print('🗄️ Инициализация NoSQL...')
        db = NoSQLDatabaseService()
        
        await db.init_db()
        print('✅ NoSQL инициализирована!')
        
        # Тест записи
        class TestWar:
            def __init__(self):
                self.end_time = '2024-10-04T19:30:00Z'
                self.opponent_name = 'Test Clan'
                self.team_size = 15
                self.clan_stars = 42
                self.opponent_stars = 35
                self.clan_destruction = 85.5
                self.opponent_destruction = 75.2
                self.clan_attacks_used = 28
                self.result = 'win'
                self.is_cwl_war = False
                self.total_violations = 2
                self.attacks_by_member = {}
        
        test_war = TestWar()
        result = await db.save_war(test_war)
        
        if result:
            print('✅ Тест записи: УСПЕШНО')
        else:
            print('❌ Тест записи: ОШИБКА')
            return False
        
        # Тест чтения
        exists = await db.war_exists(test_war.end_time)
        if exists:
            print('✅ Тест чтения: УСПЕШНО')
        else:
            print('❌ Тест чтения: ОШИБКА')
            return False
        
        # Статистика
        count = await db.get_wars_count()
        print(f'📊 Количество войн в NoSQL: {count}')
        
        return True
    
    # Запуск теста
    result = asyncio.run(test_nosql())
    
    if result:
        print('🎉 NoSQL система работает идеально!')
        print('🚀 Готово к запуску Ultra Scanner!')
    else:
        print('❌ Ошибка в NoSQL системе')
        sys.exit(1)
        
except Exception as e:
    print(f'💥 Критическая ошибка: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎯 ПЕРЕХОД НА NOSQL ЗАВЕРШЕН!"
    echo "================================"
    echo "✅ NoSQL база данных готова"
    echo "✅ Никаких блокировок SQLite"
    echo "✅ Никаких thread limit проблем"
    echo "✅ Простота и надежность"
    echo ""
    echo "📊 Структура NoSQL:"
    ls -la nosql_db/ 2>/dev/null || echo "   (будет создана при первом запуске)"
    echo ""
    echo "🚀 Теперь можно запустить Ultra Scanner:"
    echo "   python scripts/all_importer.py"
    echo ""
    echo "💡 Преимущества NoSQL:"
    echo "   - Нет блокировок базы данных"
    echo "   - Нет ограничений на потоки"
    echo "   - Простое резервное копирование"
    echo "   - Легко читаемые JSON файлы"
    
else
    echo ""
    echo "❌ ОШИБКА ПЕРЕХОДА НА NOSQL"
    echo "💡 Проверьте зависимости и запустите снова"
    exit 1
fi