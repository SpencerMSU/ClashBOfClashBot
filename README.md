# ClashBot - Telegram бот для Clash of Clans

[![Go Version](https://img.shields.io/badge/Go-1.21+-00ADD8?style=flat&logo=go)](https://golang.org)
[![Python Version](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Telegram бот для мониторинга кланов и игроков в Clash of Clans с поддержкой премиум-функций.

## 🚀 Статус Проекта

**Проект находится в процессе миграции с Python на Go**

### Текущее состояние:
- ✅ **Python версия** - полностью функциональна (в папке `oldpy/`)
- 🔄 **Go версия** - ~43% завершена (активная разработка)

### Что работает (Go):
- ✅ Модели данных (пользователи, подписки, войны, здания)
- ✅ База данных SQLite (полная поддержка)
- ✅ Clash of Clans API клиент
- ✅ Система конфигурации
- ✅ YooKassa платежная интеграция
- ✅ Мониторинг войн и зданий
- ✅ Система переводов

### В разработке (Go):
- ⏳ Основной бот и обработчики команд
- ⏳ Генератор сообщений
- ⏳ Клавиатуры и навигация
- ⏳ Webhook обработка

## 📋 Функциональность

### Основные возможности:
- 🎯 Просмотр статистики игроков и кланов
- ⚔️ Мониторинг войн и CWL
- 📊 Детальная аналитика атак
- 🏆 Отслеживание достижений
- 💎 Информация о донатах

### Premium функции:
- 👥 Мультипрофильность (до 3 профилей)
- 🏗️ Отслеживание улучшений зданий
- 📈 Расширенная статистика войн
- 🔔 Приоритетные уведомления

## 🛠️ Установка и запуск

### Python версия (oldpy/)

```bash
cd oldpy
pip install -r requirements.txt
python main.py
```

### Go версия (в разработке)

```bash
# Установка зависимостей
go mod download

# Запуск
go run main.go
```

### Конфигурация

Создайте файл `api_tokens.txt` в корне проекта:

```
BOT_TOKEN=your_telegram_bot_token
COC_API_TOKEN=your_coc_api_token
YOOKASSA_SHOP_ID=your_yookassa_shop_id
YOOKASSA_SECRET_KEY=your_yookassa_secret_key
```

Или используйте переменные окружения.

## 📚 Документация

- [ADMINSTR.md](ADMINSTR.md) - Инструкции по запуску и настройке
- [README_GO.md](README_GO.md) - Детали Go реализации
- [ALL_IMPORTER_README.md](ALL_IMPORTER_README.md) - Документация сканера кланов
- [WAR_IMPORTER_README.md](WAR_IMPORTER_README.md) - Документация импортера войн
- [ERROR_TRACKING_README.md](ERROR_TRACKING_README.md) - Отслеживание ошибок API

## 📁 Структура проекта

```
ClashBOfClashBot/
├── oldpy/                  # Python версия (полностью функциональна)
│   ├── bot.py             # Основной бот
│   ├── handlers.py        # Обработчики
│   ├── message_generator.py  # Генератор сообщений
│   ├── database.py        # База данных
│   └── ...
├── internal/              # Go версия (в разработке)
│   ├── api/              # API клиенты
│   ├── database/         # Сервис базы данных
│   ├── models/           # Модели данных
│   ├── services/         # Бизнес-логика
│   └── utils/            # Утилиты
├── config/               # Конфигурация
├── main.go              # Точка входа Go версии
└── *.md                 # Документация
```

## 🔧 Технологии

### Python версия:
- python-telegram-bot
- aiohttp
- sqlite3
- YooKassa API

### Go версия:
- github.com/go-telegram-bot-api/telegram-bot-api/v5
- github.com/mattn/go-sqlite3
- github.com/go-resty/resty/v2
- YooKassa API v3

## 📊 Статистика миграции

| Компонент | Python строк | Go строк | Статус |
|-----------|--------------|----------|--------|
| Модели | ~220 | ~260 | ✅ 100% |
| База данных | ~1570 | ~1380 | ✅ 100% |
| API клиент | ~700 | ~450 | ✅ 100% |
| Сервисы | ~3000 | ~1950 | ✅ 100% |
| Утилиты | ~2200 | ~950 | ✅ 100% |
| Бот/Обработчики | ~8509 | ~0 | ⏳ 0% |
| **Итого** | **~14976** | **~4686** | **~43%** |

## 🤝 Вклад в проект

Проект в активной разработке. Приветствуется помощь в миграции на Go!

## 📝 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 📧 Контакты

Для вопросов и предложений создайте Issue в репозитории.
