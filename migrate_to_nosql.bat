@echo off
echo 🔄 ПЕРЕХОД НА NOSQL DATABASE
echo ==============================

cd /d "%~dp0"

echo 📍 Текущая папка: %CD%

REM Остановка процессов
echo.
echo 🛑 Остановка всех процессов...
taskkill /f /im python.exe /t >nul 2>&1
taskkill /f /im python3.exe /t >nul 2>&1

REM Очистка SQLite
echo.
echo 🧹 Очистка SQLite файлов...
if exist "clashbot.db-wal" del /f "clashbot.db-wal"
if exist "clashbot.db-shm" del /f "clashbot.db-shm"

REM Backup старой БД
if exist "clashbot.db" (
    set backup_name=sqlite_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db
    copy "clashbot.db" "%backup_name%" >nul
    echo 💾 SQLite backup создан: %backup_name%
)

REM Создание NoSQL папки
echo.
echo 📁 Создание NoSQL структуры...
if not exist "nosql_db" mkdir "nosql_db"
echo ✅ Папка nosql_db создана

REM Активация виртуального окружения
if exist "venv\Scripts\activate.bat" (
    echo 📦 Активация виртуального окружения...
    call venv\Scripts\activate.bat
)

REM Тестирование NoSQL
echo.
echo 🧪 Тестирование NoSQL системы...

python -c "
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

if %errorlevel% equ 0 (
    echo.
    echo 🎯 ПЕРЕХОД НА NOSQL ЗАВЕРШЕН!
    echo ================================
    echo ✅ NoSQL база данных готова
    echo ✅ Никаких блокировок SQLite
    echo ✅ Никаких thread limit проблем
    echo ✅ Простота и надежность
    echo.
    echo 📊 Структура NoSQL:
    dir nosql_db 2>nul || echo    (будет создана при первом запуске)
    echo.
    echo 🚀 Теперь можно запустить Ultra Scanner:
    echo    python scripts\all_importer.py
    echo.
    echo 💡 Преимущества NoSQL:
    echo    - Нет блокировок базы данных
    echo    - Нет ограничений на потоки
    echo    - Простое резервное копирование
    echo    - Легко читаемые JSON файлы
) else (
    echo.
    echo ❌ ОШИБКА ПЕРЕХОДА НА NOSQL
    echo 💡 Проверьте зависимости и запустите снова
)

pause