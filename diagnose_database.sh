#!/bin/bash

# Диагностика MongoDB для ClashBot

echo "🔍 Диагностика MongoDB..."

cd "$(dirname "$0")"

echo "📁 Текущая папка: $(pwd)"

echo ""
echo "🌐 Проверка переменных окружения:"
echo "   MONGODB_URI=${MONGODB_URI:-'не задан'}"
echo "   MONGODB_DB_NAME=${MONGODB_DB_NAME:-'не задан'}"

echo ""
echo "🐍 Проверка подключения через Python..."

python3 - <<'PY'
import asyncio
import os
import sys

sys.path.insert(0, '.')

try:
    from src.services.database import DatabaseService
except RuntimeError as exc:
    print(f"❌ {exc}")
    sys.exit(1)

async def diagnose():
    db_service = DatabaseService()
    print('🗄️ MongoDB URI:', getattr(db_service, 'mongo_uri', '<unknown>'))
    print('🗄️ База данных:', getattr(db_service, 'db_name', '<unknown>'))

    try:
        await db_service.ping()
        print('✅ Подключение к MongoDB успешно')
    except Exception as exc:
        print('❌ Ошибка подключения:', exc)
        raise

    collections = await db_service.db.list_collection_names()
    if not collections:
        print('⚠️ В базе данных пока нет коллекций')
    else:
        print('\n📚 Статистика коллекций:')
        for name in sorted(collections):
            count = await db_service.db[name].estimated_document_count()
            print(f"   • {name}: {count} документ(ов)")

    db_service.client.close()

asyncio.run(diagnose())
PY

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Диагностика завершена"
else
    echo ""
    echo "❌ Диагностика завершилась с ошибкой"
    exit 1
fi
