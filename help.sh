#!/bin/bash

# ClashBot Go - Скрипт помощи

echo "🤖 ClashBot Go - Помощник запуска"
echo "=================================="
echo ""

echo "📋 Доступные команды:"
echo ""

echo "🔍 1. ДИАГНОСТИКА УСТАНОВКИ:"
echo "   go run validate_setup.go"
echo "   ↳ Проверяет все компоненты и конфигурацию"
echo ""

echo "🚀 2. ЗАПУСК БОТА:"
echo "   go run main.go"
echo "   ↳ Запускает бота с полным логированием"
echo ""

echo "⚙️ 3. СБОРКА БОТА:"
echo "   go build -o clashbot-go ."
echo "   ./clashbot-go"
echo "   ↳ Создает исполняемый файл и запускает"
echo ""

echo "🧹 4. ОЧИСТКА:"
echo "   go clean"
echo "   rm -f clashbot.db"
echo "   ↳ Удаляет временные файлы"
echo ""

echo "📖 5. ПРОСМОТР ДОКУМЕНТАЦИИ:"
echo "   cat GO-LANG-VER-SETUP.md"
echo "   ↳ Полное руководство по настройке"
echo ""

echo "⚠️  ТРЕБУЕТСЯ НАСТРОЙКА:"
echo ""

if [ ! -f "api_tokens.txt" ]; then
    echo "❌ Файл api_tokens.txt не найден!"
    echo "   1. Скопируйте: cp api_tokens.txt.example api_tokens.txt"
    echo "   2. Отредактируйте api_tokens.txt и добавьте реальные токены"
    echo "   3. Получите BOT_TOKEN у @BotFather в Telegram"
    echo "   4. Получите COC_API_TOKEN на https://developer.clashofclans.com"
else
    echo "✅ Файл api_tokens.txt найден"
    echo "   Убедитесь что в нем указаны реальные токены"
fi

echo ""
echo "🎯 БЫСТРЫЙ СТАРТ:"
echo "   1. cp api_tokens.txt.example api_tokens.txt"
echo "   2. nano api_tokens.txt  (добавьте реальные токены)"
echo "   3. go run validate_setup.go  (проверка)"
echo "   4. go run main.go  (запуск)"
echo ""

echo "📞 При проблемах см. GO-LANG-VER-SETUP.md"