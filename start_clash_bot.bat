@echo off
echo 🔍 Проверка запущенных ботов...

REM Остановка процессов Python с main.py
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv /nh ^| findstr "main.py"') do (
    echo 🛑 Остановка процесса Python: %%i
    taskkill /f /pid %%i >nul 2>&1
)

for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python3.exe" /fo csv /nh ^| findstr "main.py"') do (
    echo 🛑 Остановка процесса Python3: %%i
    taskkill /f /pid %%i >nul 2>&1
)

echo.
echo 🚀 Запуск ClashBot...

cd /d "%~dp0"

REM Проверка и активация виртуального окружения
if exist "venv\Scripts\activate.bat" (
    echo 📦 Активация виртуального окружения...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Виртуальное окружение не найдено, используем системный Python
)

REM Установка переменных окружения
set ENABLE_GLOBAL_CLAN_SCANNING=false
set SCAN_ONLY_OUR_CLAN=true

echo ⚙️ Настройки сканера:
echo    - Глобальное сканирование: ОТКЛЮЧЕНО
echo    - Сканирование только нашего клана: ВКЛЮЧЕНО
echo.

echo 🎯 Запуск main.py...

REM Запуск основного бота
python main.py

pause