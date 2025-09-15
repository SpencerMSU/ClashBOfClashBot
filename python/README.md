# Python Handlers для Clash of Clans Bot

Этот модуль содержит Python-версию обработчиков сообщений и callback-запросов для бота Clash of Clans, портированную с Java версии.

## Структура

```
python/
├── __init__.py                 # Главный модуль пакета
├── bot/
│   ├── __init__.py            # Экспорты модуля bot
│   ├── handlers.py            # Главный файл обработчиков
│   ├── user_state.py          # Состояния пользователей
│   ├── war_sort.py            # Типы сортировки войн
│   ├── keyboards.py           # Константы клавиатур
│   └── handlers/
│       ├── __init__.py        # Настройка обработчиков
│       ├── message_handler.py # Обработчик сообщений
│       └── callback_handler.py# Обработчик callback-запросов
├── example_usage.py           # Пример использования
└── README.md                  # Этот файл
```

## Основные компоненты

### 1. MessageHandler
Асинхронный обработчик текстовых сообщений и команд:
- Обработка команд меню (профиль, клан, уведомления)
- Управление состояниями пользователей
- Валидация и обработка тегов игроков/кланов
- Интеграция с базой данных и API

### 2. CallbackHandler
Асинхронный обработчик inline-кнопок:
- Обработка пагинации списков
- Взаимодействие с информацией о войнах
- Управление настройками уведомлений
- Навигация по меню

### 3. Вспомогательные модули
- **UserState**: Перечисление состояний пользователя
- **WarSort**: Типы сортировки истории войн
- **Keyboards**: Константы текстов кнопок и callback-данных

## Использование

### Быстрый старт

```python
from python.bot import setup_handlers
from telegram.ext import Application

# Создание приложения
app = Application.builder().token("YOUR_BOT_TOKEN").build()

# Настройка обработчиков
handlers = setup_handlers(app, bot_instance, message_generator)

# Запуск бота
app.run_polling()
```

### Детальная настройка

```python
from python.bot.handlers import MessageHandler, CallbackHandler
from telegram.ext import MessageHandler as TGMessageHandler, CallbackQueryHandler
from telegram.ext import filters

# Создание обработчиков
message_handler = MessageHandler(bot_instance, message_generator)
callback_handler = CallbackHandler(bot_instance, message_generator)

# Регистрация в приложении
app.add_handler(TGMessageHandler(filters.TEXT, message_handler.handle))
app.add_handler(CallbackQueryHandler(callback_handler.handle))
```

## Функциональность

### Обработка сообщений
- **Команды меню**: /start, кнопки профиля, клана
- **Состояния ввода**: Ожидание тегов для поиска/привязки
- **Валидация тегов**: Автоматическая нормализация тегов

### Обработка callback-запросов
- **Пагинация**: Навигация по спискам участников и войн
- **Детали войн**: Просмотр информации о конкретных войнах
- **Профили**: Отображение информации об игроках
- **Уведомления**: Управление подписками

### Интеграция

Обработчики предназначены для работы с:
- **python-telegram-bot** (версия 20+)
- **База данных** (через DatabaseService)
- **Clash of Clans API** (через CocApiClient)
- **Генератор сообщений** (MessageGenerator)

## Зависимости

```python
# Основные зависимости
python-telegram-bot >= 20.0
asyncio  # встроенный
logging  # встроенный
typing   # встроенный
re       # встроенный
enum     # встроенный
```

## Миграция с Java

Основные отличия от Java версии:
1. **Асинхронность**: Все методы используют async/await
2. **Управление состоянием**: Используется context.user_data вместо ConcurrentHashMap
3. **Обработка ошибок**: Встроенное логирование и обработка исключений
4. **Типизация**: Поддержка type hints для лучшей разработки

## Примеры использования

### Обработка команды /start
```python
# Автоматически обрабатывается MessageHandler
# Отправляет главное меню пользователю
```

### Поиск игрока по тегу
```python
# 1. Пользователь нажимает "Найти профиль по тегу"
# 2. Устанавливается состояние AWAITING_PLAYER_TAG_TO_SEARCH
# 3. Пользователь вводит тег
# 4. Тег обрабатывается и отображается информация
```

### Просмотр списка участников клана
```python
# 1. Пользователь в меню клана нажимает "Список участников"
# 2. Отображается первая страница с пагинацией
# 3. Callback-запросы обрабатывают навигацию
```

## Логирование

Все обработчики используют стандартное Python логирование:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

Логируются:
- Входящие сообщения и callback-запросы
- Ошибки обработки
- Важные действия пользователей

## Обработка ошибок

- Все исключения перехватываются и логируются
- Пользователям отправляются понятные сообщения об ошибках
- Состояния пользователей очищаются при ошибках
- Callback-запросы всегда подтверждаются

## Расширение

Для добавления новых команд:
1. Добавьте константу в `Keyboards`
2. Добавьте обработку в `MessageHandler._handle_menu_commands`
3. При необходимости добавьте новый callback в `CallbackHandler`

Для новых callback-запросов:
1. Добавьте константу в `Keyboards`
2. Добавьте обработку в `CallbackHandler._process_callback`
3. Реализуйте соответствующий метод в MessageGenerator