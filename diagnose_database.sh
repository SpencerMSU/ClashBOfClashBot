#!/bin/bash

# Диагностика проблем с базой данных ClashBot

echo "🔍 Диагностика базы данных..."

cd "$(dirname "$0")"

echo "📁 Текущая папка: $(pwd)"
echo "📁 Содержимое папки:"
ls -la

echo ""
echo "🔍 Поиск clashbot.db:"
find . -name "clashbot.db" -type f 2>/dev/null || echo "❌ clashbot.db не найден"

echo ""
echo "📊 Проверка прав доступа:"
if [ -f "clashbot.db" ]; then
    ls -la clashbot.db
    
    # Проверка возможности чтения
    if [ -r "clashbot.db" ]; then
        echo "✅ Чтение: разрешено"
    else
        echo "❌ Чтение: запрещено"
    fi
    
    # Проверка возможности записи
    if [ -w "clashbot.db" ]; then
        echo "✅ Запись: разрешена"
    else
        echo "❌ Запись: запрещена"
        echo "💡 Исправление: chmod 666 clashbot.db"
    fi
    
    # Проверка блокировок
    if lsof clashbot.db 2>/dev/null; then
        echo "⚠️ База данных используется другим процессом!"
        lsof clashbot.db
    else
        echo "✅ База данных свободна"
    fi
    
    # Проверка целостности БД
    echo ""
    echo "🔧 Проверка целостности:"
    sqlite3 clashbot.db "PRAGMA integrity_check;" 2>/dev/null || {
        echo "❌ Ошибка доступа к SQLite"
        echo "💡 Убедитесь что sqlite3 установлен"
    }
    
else
    echo "❌ clashbot.db не найден в $(pwd)"
    echo ""
    echo "🔧 Создание базы данных..."
    
    # Проверка прав на создание файлов
    touch test_file 2>/dev/null && {
        echo "✅ Права на создание файлов: есть"
        rm test_file
    } || {
        echo "❌ Права на создание файлов: отсутствуют"
        echo "💡 Исправление: chmod 755 $(pwd)"
    }
fi

echo ""
echo "🐍 Проверка Python доступа к БД:"
python3 -c "
import sqlite3
import os

db_path = 'clashbot.db'
print(f'📍 Проверяемый путь: {os.path.abspath(db_path)}')

try:
    # Попытка подключения
    conn = sqlite3.connect(db_path)
    print('✅ SQLite подключение: успешно')
    
    # Проверка записи
    conn.execute('CREATE TABLE IF NOT EXISTS test_table (id INTEGER)')
    conn.execute('INSERT INTO test_table (id) VALUES (1)')
    conn.commit()
    print('✅ Запись в БД: успешно')
    
    # Проверка чтения
    cursor = conn.execute('SELECT COUNT(*) FROM test_table')
    count = cursor.fetchone()[0]
    print(f'✅ Чтение из БД: успешно (записей: {count})')
    
    # Очистка тестовых данных
    conn.execute('DROP TABLE test_table')
    conn.commit()
    conn.close()
    print('✅ Тест БД завершен успешно')
    
except Exception as e:
    print(f'❌ Ошибка Python SQLite: {e}')
" 2>/dev/null || echo "❌ Python или sqlite3 недоступны"

echo ""
echo "🎯 Рекомендации:"
echo "1. База данных должна быть в корневой папке проекта"
echo "2. Запускайте скрипты из корневой папки: cd /root/ClashBOfClashBot"
echo "3. Используйте: python scripts/all_importer.py"