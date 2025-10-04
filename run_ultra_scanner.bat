@echo off
echo 🚀 Запуск Ultra Clan Scanner...

cd /d "%~dp0"

REM Проверка виртуального окружения
if exist "venv\Scripts\activate.bat" (
    echo 📦 Активация виртуального окружения...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Виртуальное окружение не найдено
)

REM Проверка зависимостей
echo 🔍 Проверка зависимостей...
python -c "import aiohttp, asyncio; print('✅ Зависимости OK')" 2>nul || (
    echo ❌ Отсутствуют зависимости. Установка...
    pip install aiohttp asyncio
)

REM Запуск Ultra Scanner
echo 🌟 Запуск Ultra Clan Scanner...
echo    - Многопоточность: 50 потоков
echo    - Скорость: 100 запросов/сек
echo    - Покрытие: Все мировые регионы
echo.

python scripts\all_importer.py

echo.
echo ✅ Ultra Clan Scanner завершен!
pause