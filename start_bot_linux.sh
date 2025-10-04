#!/bin/bash

# Скрипт для запуска ClashBot на Linux с автоматической активацией venv

# Определяем директорию проекта
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo "🚀 Запуск ClashBot на Linux..."
echo "======================================"
echo "📁 Директория проекта: $PROJECT_DIR"

# Проверяем существование виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Виртуальное окружение не найдено в $VENV_DIR"
    echo "🔧 Создаем новое виртуальное окружение..."
    
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        echo "✅ Виртуальное окружение создано"
    else
        echo "❌ Ошибка создания виртуального окружения"
        exit 1
    fi
fi

# Активируем виртуальное окружение
echo "🔄 Активация виртуального окружения..."
source "$VENV_DIR/bin/activate"

if [ $? -eq 0 ]; then
    echo "✅ Виртуальное окружение активировано"
    echo "🐍 Python: $(which python)"
    echo "📦 Pip: $(which pip)"
else
    echo "❌ Ошибка активации виртуального окружения"
    exit 1
fi

# Проверяем установленные пакеты
echo "📋 Проверка зависимостей..."
if ! python -c "import telegram" 2>/dev/null; then
    echo "⚠️ Пакеты не установлены, устанавливаем зависимости..."
    
    if [ -f "data/requirements.txt" ]; then
        pip install -r data/requirements.txt
    elif [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "❌ Файл requirements.txt не найден"
        echo "🔧 Установка основных пакетов..."
        pip install python-telegram-bot aiosqlite aiohttp python-dateutil asyncio-throttle
    fi
fi

# Запускаем бота
echo "🚀 Запуск бота..."
echo "======================================"

python main.py

echo ""
echo "🛑 Бот остановлен"
echo "📝 Для выхода из виртуального окружения выполните: deactivate"