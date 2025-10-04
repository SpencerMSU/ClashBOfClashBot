@echo off
echo 🛑 Принудительная остановка всех процессов ClashBot...

cd /d "%~dp0"

echo 🔍 Поиск процессов Python...

REM Остановка процессов Python с main.py
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv /nh 2^>nul ^| findstr "main.py"') do (
    echo 🛑 Остановка процесса Python main.py: %%i
    taskkill /f /pid %%i >nul 2>&1
)

REM Остановка процессов Python с all_importer.py
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv /nh 2^>nul ^| findstr "all_importer.py"') do (
    echo 🛑 Остановка процесса Python all_importer.py: %%i
    taskkill /f /pid %%i >nul 2>&1
)

REM Остановка всех python3.exe
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python3.exe" /fo csv /nh 2^>nul') do (
    echo 🛑 Остановка процесса Python3: %%i
    taskkill /f /pid %%i >nul 2>&1
)

echo.
echo 🔓 Освобождение блокировок базы данных...

REM Удаление временных файлов SQLite
if exist "clashbot.db-wal" (
    echo 🧹 Удаление clashbot.db-wal
    del /f "clashbot.db-wal" >nul 2>&1
)

if exist "clashbot.db-shm" (
    echo 🧹 Удаление clashbot.db-shm
    del /f "clashbot.db-shm" >nul 2>&1
)

echo.
echo ✅ Все процессы остановлены, блокировки сняты
echo 🎯 Теперь можно безопасно запустить бот

pause