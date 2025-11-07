@echo off
echo 🛑 Принудительная остановка всех процессов ClashBot...

cd /d "%~dp0"

echo 🔍 Поиск процессов Python...

REM Остановка процессов Python с main.py
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv /nh 2^>nul ^| findstr "main.py"') do (
    echo 🛑 Остановка процесса Python main.py: %%i
    taskkill /f /pid %%i >nul 2>&1
)

REM Остановка всех python3.exe, запущенных с main.py
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python3.exe" /fo csv /nh 2^>nul ^| findstr "main.py"') do (
    echo 🛑 Остановка процесса Python3 main.py: %%i
    taskkill /f /pid %%i >nul 2>&1
)

echo.
echo 🔓 Проверка подключения к PostgreSQL...
python - <<"PY"
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.services.database import DatabaseService
except RuntimeError as exc:
    print(f"❌ {exc}")
    sys.exit(1)

async def main():
    db_service = DatabaseService()
    print('🗄️ Строка подключения:', getattr(db_service, 'database_url', '<unknown>'))
    try:
        await db_service.ping()
        print('✅ Подключение к PostgreSQL активно')
    except Exception as exc:
        print('❌ Ошибка подключения к PostgreSQL:', exc)
    finally:
        await db_service.close()

asyncio.run(main())
PY

echo.
echo ✅ Все процессы остановлены, блокировки сняты
echo 🎯 Теперь можно безопасно запустить бот

pause
