#!/bin/bash

# Скрипт принудительной остановки всех процессов ClashBot

echo "🛑 Принудительная остановка всех процессов ClashBot..."

cd "$(dirname "$0")"

# Остановка Python процессов с ClashBot
echo "🔍 Поиск процессов Python..."
PYTHON_PROCESSES=$(ps aux | grep -E "(main\.py|all_importer\.py)" | grep -v grep)

if [ -n "$PYTHON_PROCESSES" ]; then
    echo "📋 Найденные процессы:"
    echo "$PYTHON_PROCESSES"
    echo ""
    
    # Получаем PID процессов
    PIDS=$(ps aux | grep -E "(main\.py|all_importer\.py)" | grep -v grep | awk '{print $2}')
    
    for PID in $PIDS; do
        echo "🛑 Остановка процесса $PID..."
        kill -TERM "$PID" 2>/dev/null
        
        # Ждем 3 секунды
        sleep 3
        
        # Проверяем, завершился ли процесс
        if kill -0 "$PID" 2>/dev/null; then
            echo "⚠️ Процесс $PID не завершился, принудительная остановка..."
            kill -KILL "$PID" 2>/dev/null
            sleep 1
            
            if kill -0 "$PID" 2>/dev/null; then
                echo "❌ Не удалось остановить процесс $PID"
            else
                echo "✅ Процесс $PID принудительно остановлен"
            fi
        else
            echo "✅ Процесс $PID корректно завершился"
        fi
    done
else
    echo "✅ Процессы Python не найдены"
fi

# Освобождение блокировок базы данных
echo ""
echo "🔓 Освобождение блокировок базы данных..."

if [ -f "clashbot.db" ]; then
    # Проверка блокировок
    if command -v lsof >/dev/null 2>&1; then
        DB_LOCKS=$(lsof clashbot.db 2>/dev/null)
        if [ -n "$DB_LOCKS" ]; then
            echo "⚠️ База данных все еще заблокирована:"
            echo "$DB_LOCKS"
            
            # Попытка принудительно освободить
            DB_PIDS=$(lsof -t clashbot.db 2>/dev/null)
            for PID in $DB_PIDS; do
                echo "🛑 Принудительное освобождение БД от процесса $PID..."
                kill -KILL "$PID" 2>/dev/null
            done
        else
            echo "✅ База данных свободна от блокировок"
        fi
    fi
    
    # Проверка файлов WAL и SHM (SQLite)
    if [ -f "clashbot.db-wal" ] || [ -f "clashbot.db-shm" ]; then
        echo "🧹 Очистка временных файлов SQLite..."
        rm -f clashbot.db-wal clashbot.db-shm 2>/dev/null
        echo "✅ Временные файлы очищены"
    fi
    
    # Тест доступа к БД
    echo "🧪 Проверка доступа к базе данных..."
    sqlite3 clashbot.db "SELECT COUNT(*) FROM sqlite_master;" >/dev/null 2>&1 && {
        echo "✅ База данных доступна"
    } || {
        echo "❌ База данных недоступна или повреждена"
    }
else
    echo "⚠️ clashbot.db не найден"
fi

echo ""
echo "✅ Все процессы остановлены, блокировки сняты"
echo "🎯 Теперь можно безопасно запустить бот: python scripts/all_importer.py"