#!/bin/bash

# Скрипт инициализации MongoDB для ClashBot

echo "🔍 ПОЛНАЯ ПРОВЕРКА И ИНИЦИАЛИЗАЦИЯ MongoDB"
echo "========================================="

cd "$(dirname "$0")"

echo "📍 Текущая папка: $(pwd)"

# Активация виртуального окружения
if [ -d "venv" ]; then
    echo "📦 Активация виртуального окружения..."
    # shellcheck disable=SC1091
    source venv/bin/activate
fi

echo ""
echo "🐍 Проверка MongoDB через Python..."

python3 - <<'PY'
import asyncio
import sys

sys.path.insert(0, '.')

try:
    from src.services.database import DatabaseService
except RuntimeError as exc:
    print(f"❌ {exc}")
    sys.exit(1)

async def init_database():
    db_service = DatabaseService()

    print('🗄️ MongoDB URI:', getattr(db_service, 'mongo_uri', '<unknown>'))
    print('🗄️ Используемая БД:', getattr(db_service, 'db_name', 'clashbot'))

    print('🔧 Проверка подключения...')
    await db_service.ping()
    print('✅ Подключение успешно')

    print('🛠️ Настройка коллекций и индексов...')
    await db_service.init_db()
    print('✅ Индексы готовы к работе')

    collections = await db_service.db.list_collection_names()
    if collections:
        print('\n📚 Текущие коллекции:')
        for name in sorted(collections):
            count = await db_service.db[name].estimated_document_count()
            print(f"   • {name}: {count} документ(ов)")
    else:
        print('\n⚠️ Коллекции отсутствуют — будут созданы автоматически при работе бота')

    db_service.client.close()
    return True

asyncio.run(init_database())
PY

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 MongoDB подготовлена к работе!"
else
    echo ""
    echo "❌ Ошибка при инициализации MongoDB"
    exit 1
fi
