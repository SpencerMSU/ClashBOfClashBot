#!/bin/bash

# Диагностический скрипт для проверки Python окружения

echo "🔍 ДИАГНОСТИКА PYTHON ОКРУЖЕНИЯ"
echo "=================================="

echo "📍 Текущая директория: $(pwd)"
echo ""

echo "🐍 ИНФОРМАЦИЯ О PYTHON:"
echo "----------------------"
echo "Системный Python3: $(which python3)"
python3 --version
echo ""

if command -v python &> /dev/null; then
    echo "Команда python: $(which python)"
    python --version
else
    echo "Команда python: НЕ НАЙДЕНА"
fi
echo ""

echo "📦 ВИРТУАЛЬНОЕ ОКРУЖЕНИЕ:"
echo "------------------------"

# Проверяем различные возможные расположения venv
VENV_PATHS=(
    ".venv"
    "../.venv"
    "venv"
    "../venv"
    "env"
    "../env"
)

VENV_FOUND=false
for venv_path in "${VENV_PATHS[@]}"; do
    if [ -d "$venv_path" ]; then
        echo "✅ Найдено виртуальное окружение: $venv_path"
        
        if [ -f "$venv_path/bin/activate" ]; then
            echo "✅ Скрипт активации: $venv_path/bin/activate"
            
            # Проверяем Python в venv
            if [ -f "$venv_path/bin/python" ]; then
                echo "✅ Python в venv: $venv_path/bin/python"
                echo "   Версия: $($venv_path/bin/python --version)"
            fi
            
            # Проверяем pip в venv
            if [ -f "$venv_path/bin/pip" ]; then
                echo "✅ Pip в venv: $venv_path/bin/pip"
            fi
        else
            echo "❌ Скрипт активации не найден"
        fi
        
        VENV_FOUND=true
        echo ""
    fi
done

if [ "$VENV_FOUND" = false ]; then
    echo "❌ Виртуальное окружение не найдено"
    echo ""
fi

echo "📋 ПРОВЕРКА ЗАВИСИМОСТЕЙ:"
echo "------------------------"

# Проверяем в системном Python
echo "В системном Python3:"
for package in telegram aiosqlite aiohttp; do
    if python3 -c "import $package" 2>/dev/null; then
        echo "  ✅ $package"
    else
        echo "  ❌ $package"
    fi
done
echo ""

# Если есть активное venv, проверяем в нем
if [ -n "$VIRTUAL_ENV" ]; then
    echo "В активном виртуальном окружении ($VIRTUAL_ENV):"
    for package in telegram aiosqlite aiohttp; do
        if python -c "import $package" 2>/dev/null; then
            echo "  ✅ $package"
        else
            echo "  ❌ $package"
        fi
    done
fi

echo ""
echo "🔧 РЕКОМЕНДАЦИИ:"
echo "---------------"

if [ "$VENV_FOUND" = true ]; then
    echo "1. Активируйте виртуальное окружение:"
    echo "   source .venv/bin/activate"
    echo ""
    echo "2. Установите зависимости (если нужно):"
    echo "   pip install -r data/requirements.txt"
    echo ""
    echo "3. Запустите бота:"
    echo "   python main.py"
else
    echo "1. Создайте виртуальное окружение:"
    echo "   python3 -m venv .venv"
    echo ""
    echo "2. Активируйте его:"
    echo "   source .venv/bin/activate"
    echo ""
    echo "3. Установите зависимости:"
    echo "   pip install -r data/requirements.txt"
    echo ""
    echo "4. Запустите бота:"
    echo "   python main.py"
fi

echo ""
echo "🚀 Или используйте автоматический скрипт:"
echo "   chmod +x start_bot_linux.sh"
echo "   ./start_bot_linux.sh"