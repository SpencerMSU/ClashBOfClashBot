#!/bin/bash

# Проверка и остановка конфликтующих ботов
echo "🔍 Проверка запущенных ботов..."

# Остановка всех существующих ботов
./stop_all_bots.sh

echo ""
echo "🚀 Запуск ClashBot..."

# Переход в директорию проекта
cd "$(dirname "$0")"

# Активация виртуального окружения если существует
if [ -d "venv" ]; then
    echo "📦 Активация виртуального окружения..."
    source venv/bin/activate
    
    # Проверка Python
    echo "🐍 Версия Python: $(python --version)"
    echo "📍 Путь к Python: $(which python)"
else
    echo "⚠️ Виртуальное окружение не найдено, используем системный Python"
fi

# Установка переменных окружения для конфигурации
export ENABLE_GLOBAL_CLAN_SCANNING=false
export SCAN_ONLY_OUR_CLAN=true

echo "⚙️ Настройки сканера:"
echo "   - Глобальное сканирование: ОТКЛЮЧЕНО"
echo "   - Сканирование только нашего клана: ВКЛЮЧЕНО"

echo ""
echo "🎯 Запуск main.py..."

# Запуск основного бота
python main.py