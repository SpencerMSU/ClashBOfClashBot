#!/bin/bash

# Скрипт для остановки всех запущенных ботов

echo "🔍 Поиск запущенных процессов Python..."

# Ищем процессы с main.py
PROCESSES=$(ps aux | grep "python.*main.py" | grep -v grep)

if [ -z "$PROCESSES" ]; then
    echo "✅ Активных ботов не найдено"
else
    echo "🚨 Найдены запущенные боты:"
    echo "$PROCESSES"
    echo ""
    
    # Получаем PID процессов
    PIDS=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}')
    
    for PID in $PIDS; do
        echo "🛑 Остановка процесса $PID..."
        kill -TERM "$PID" 2>/dev/null
        
        # Ждем 3 секунды
        sleep 3
        
        # Проверяем, завершился ли процесс
        if kill -0 "$PID" 2>/dev/null; then
            echo "⚠️ Процесс $PID не завершился, принудительная остановка..."
            kill -KILL "$PID" 2>/dev/null
        else
            echo "✅ Процесс $PID успешно остановлен"
        fi
    done
fi

echo ""
echo "🔍 Проверка портов Telegram API..."

# Проверяем соединения к api.telegram.org
TELEGRAM_CONNECTIONS=$(netstat -an 2>/dev/null | grep "api.telegram.org" || ss -an 2>/dev/null | grep "149.154" || true)

if [ -n "$TELEGRAM_CONNECTIONS" ]; then
    echo "⚠️ Обнаружены активные соединения к Telegram:"
    echo "$TELEGRAM_CONNECTIONS"
else
    echo "✅ Нет активных соединений к Telegram"
fi

echo ""
echo "✅ Теперь можно безопасно запустить бота!"
echo "Выполните: ./start_bot_linux.sh"