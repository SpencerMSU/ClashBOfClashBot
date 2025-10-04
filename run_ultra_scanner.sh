#!/bin/bash

# Скрипт для запуска Ultra Clan Scanner

echo "🚀 Запуск Ultra Clan Scanner..."

# Переход в корневую папку проекта
cd "$(dirname "$0")"

# Проверка виртуального окружения
if [ -d "venv" ]; then
    echo "📦 Активация виртуального окружения..."
    source venv/bin/activate
    echo "🐍 Python: $(which python)"
else
    echo "⚠️ Виртуальное окружение не найдено"
fi

# Проверка зависимостей
echo "🔍 Проверка зависимостей..."
python -c "import aiohttp, asyncio; print('✅ Зависимости OK')" 2>/dev/null || {
    echo "❌ Отсутствуют зависимости. Установка..."
    pip install aiohttp asyncio
}

# Запуск Ultra Scanner
echo "🌟 Запуск Ultra Clan Scanner..."
echo "   - Многопоточность: 50 потоков"
echo "   - Скорость: 100 запросов/сек"
echo "   - Покрытие: Все мировые регионы"
echo ""

python scripts/all_importer.py

echo ""
echo "✅ Ultra Clan Scanner завершен!"