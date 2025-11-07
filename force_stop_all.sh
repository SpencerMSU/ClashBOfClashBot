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

# Проверка состояния MongoDB
echo ""
echo "🔓 Проверка состояния MongoDB..."

python3 - <<'PY'
import asyncio
import sys

sys.path.insert(0, '.')

try:
    from src.services.database import DatabaseService
except RuntimeError as exc:
    print(f"❌ {exc}")
    sys.exit(1)

async def main():
    db_service = DatabaseService()
    print('🗄️ MongoDB URI:', getattr(db_service, 'mongo_uri', '<unknown>'))
    print('🗄️ База данных:', getattr(db_service, 'db_name', '<unknown>'))

    try:
        await db_service.ping()
        print('✅ Подключение к MongoDB активно')
    except Exception as exc:
        print('❌ Ошибка подключения к MongoDB:', exc)
    finally:
        db_service.client.close()

asyncio.run(main())
PY

echo ""
echo "✅ Все процессы остановлены, блокировки сняты"
echo "🎯 Теперь можно безопасно запустить бот: python scripts/all_importer.py"