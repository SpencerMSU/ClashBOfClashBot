#!/bin/bash

# Скрипт проверки и обновления зависимостей для Ultra Scanner

echo "🔍 Проверка зависимостей Ultra Scanner..."

cd "$(dirname "$0")"

# Активация виртуального окружения
if [ -d "venv" ]; then
    echo "📦 Активация виртуального окружения..."
    source venv/bin/activate
else
    echo "⚠️ Виртуальное окружение не найдено, используем системный Python"
fi

echo "🐍 Python версия: $(python --version)"

# Проверка и установка/обновление aiohttp
echo ""
echo "🌐 Проверка aiohttp..."
python -c "
import aiohttp
print(f'✅ aiohttp версия: {aiohttp.__version__}')

# Проверка поддержки современного API
try:
    import aiohttp
    connector = aiohttp.TCPConnector(limit=10)
    print('✅ TCPConnector работает корректно')
    connector.close()
except Exception as e:
    print(f'❌ Проблема с TCPConnector: {e}')
" 2>/dev/null || {
    echo "❌ aiohttp не установлен или устарел"
    echo "📥 Установка/обновление aiohttp..."
    pip install --upgrade aiohttp
}

# Проверка других зависимостей
echo ""
echo "📋 Проверка остальных зависимостей..."

DEPS=("asyncio" "motor" "pymongo")
for dep in "${DEPS[@]}"; do
    python -c "import $dep; print(f'✅ $dep: OK')" 2>/dev/null || {
        echo "❌ $dep не найден, устанавливаем..."
        pip install $dep
    }
done

echo ""
echo "🧪 Тестирование Ultra Scanner API..."
python -c "
try:
    import aiohttp
    import asyncio
    
    async def test():
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=60,
            enable_cleanup_closed=True,
            force_close=False
        )
        
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
        await session.close()
        print('✅ Ultra Scanner API тест пройден!')
    
    asyncio.run(test())
    
except Exception as e:
    print(f'❌ Ошибка в тесте: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Все зависимости готовы!"
    echo "🚀 Можно запускать Ultra Scanner: python scripts/all_importer.py"
else
    echo ""
    echo "❌ Есть проблемы с зависимостями"
    exit 1
fi