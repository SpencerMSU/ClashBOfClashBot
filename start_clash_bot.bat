@echo off
echo 🔍 Проверка запущенных ботов...

echo 🛑 Остановка процессов main.py (python.exe)...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv /nh ^| findstr "main.py"') do (
    echo    -> Остановка процесса Python: %%i
    taskkill /f /pid %%i >nul 2>&1
)

echo 🛑 Остановка процессов main.py (python3.exe)...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python3.exe" /fo csv /nh ^| findstr "main.py"') do (
    echo    -> Остановка процесса Python3: %%i
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

echo 🎯 Запуск main.py...

REM Запуск основного бота
python main.py

pause
