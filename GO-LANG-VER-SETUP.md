# ClashBot Go Version - Подробное руководство по настройке

## 🚀 Быстрый старт

### Шаг 1: Проверка зависимостей

```bash
# Проверка версии Go (требуется 1.21+)
go version

# Проверка Python (требуется для YooKassa API)
python3 --version

# Проверка наличия pip
pip3 --version
```

### Шаг 2: Создание файла конфигурации

Создайте файл `api_tokens.txt` в корневой директории:

```bash
# Создание файла токенов
touch api_tokens.txt
```

Заполните файл следующим содержимым:

```
# Telegram Bot Token (получить у @BotFather)
BOT_TOKEN=ваш_telegram_bot_token_здесь

# Clash of Clans API Token (получить на https://developer.clashofclans.com)
COC_API_TOKEN=ваш_clash_of_clans_api_token_здесь

# Bot Username (имя пользователя бота без @)
BOT_USERNAME=имя_вашего_бота

# YooKassa реквизиты (опционально, есть тестовые значения)
YOOKASSA_SHOP_ID=ваш_shop_id_yookassa
YOOKASSA_SECRET_KEY=ваш_secret_key_yookassa
```

### Шаг 3: Установка зависимостей

```bash
# Go зависимости
go mod download

# Python зависимости для платежей
pip3 install aiohttp
```

### Шаг 4: Запуск бота

```bash
# Сборка и запуск
go run main.go

# Или сборка в исполняемый файл
go build -o clashbot-go .
./clashbot-go
```

## 🔧 Детальная настройка

### Получение токенов

#### 1. Telegram Bot Token
1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `api_tokens.txt`

#### 2. Clash of Clans API Token
1. Перейдите на https://developer.clashofclans.com
2. Войдите используя Supercell ID
3. Создайте ключ API
4. Укажите IP адрес сервера где будет работать бот
5. Скопируйте токен в `api_tokens.txt`

### Структура проекта

```
ClashBOfClashBot/
├── main.go                     # 🎯 Главный файл запуска
├── api_tokens.txt             # 🔑 Файл с токенами
├── payment_bridge.py          # 🐍 Python мост для платежей
├── go.mod                     # 📦 Go модули
├── go.sum                     # 🔒 Хеши модулей
├── internal/                  # 🏗️ Внутренние компоненты
│   ├── bot/                   # 🤖 Основной класс бота
│   │   └── bot.go
│   ├── config/                # ⚙️ Конфигурация
│   │   └── config.go
│   ├── database/              # 💾 База данных
│   │   └── service.go
│   ├── api/                   # 🌐 API клиенты
│   │   └── coc_client.go
│   ├── handlers/              # 📨 Обработчики сообщений
│   │   └── handlers.go
│   ├── payment/               # 💳 Сервис платежей
│   │   └── service.go
│   └── models/                # 📊 Модели данных
│       ├── user.go
│       ├── war.go
│       └── building.go
└── README-GO.md               # 📖 Документация
```

## 🐛 Диагностика проблем

### Проблема: "BOT_TOKEN не установлен"

**Решение:**
1. Убедитесь что файл `api_tokens.txt` существует
2. Проверьте формат файла - строки вида `KEY=VALUE`
3. Убедитесь что токен указан без пробелов

```bash
# Проверка содержимого файла
cat api_tokens.txt

# Проверка переменных окружения (альтернатива)
export BOT_TOKEN=ваш_токен
export COC_API_TOKEN=ваш_coc_токен
```

### Проблема: "COC_API_TOKEN не установлен"

**Решение:**
1. Получите токен на https://developer.clashofclans.com
2. Добавьте IP сервера в настройки ключа
3. Проверьте что токен правильно указан в файле

### Проблема: "Ошибка подключения к базе данных"

**Решение:**
1. Убедитесь что SQLite поддерживается системой
2. Проверьте права на запись в директории
3. Убедитесь что у пользователя есть права создавать файлы

```bash
# Проверка SQLite
sqlite3 --version

# Создание тестовой базы
sqlite3 test.db "CREATE TABLE test (id INTEGER);"
rm test.db
```

### Проблема: "Ошибка создания Telegram Bot API"

**Решение:**
1. Проверьте правильность токена бота
2. Убедитесь что бот не заблокирован
3. Проверьте интернет-соединение

```bash
# Тест API токена
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

## 📋 Журнал инициализации

При запуске бот выводит подробную информацию о процессе инициализации:

```
🚀 Запуск бота Clash of Clans...
📋 Инициализация компонентов:
  ⏳ Загрузка конфигурации...
  ✅ Конфигурация загружена
  ⏳ Валидация конфигурации...
  ✅ Конфигурация валидна
  ⏳ Инициализация бота...
📋 Детальная инициализация компонентов бота:
    ⏳ Валидация конфигурации...
    ✅ Конфигурация валидна
    ⏳ Подключение к Telegram Bot API...
    ✅ Авторизован как @your_bot_name
    ⏳ Подключение к базе данных (clashbot.db)...
    ✅ База данных подключена
    ⏳ Инициализация Clash of Clans API клиента...
    ✅ COC API клиент создан
    ⏳ Инициализация сервиса платежей (YooKassa)...
    ✅ Сервис платежей инициализирован
    ⏳ Создание обработчиков сообщений...
    ✅ Обработчики сообщений созданы
🎉 Все компоненты бота успешно инициализированы!
  ✅ Бот инициализирован
🎯 Запуск основного цикла бота...
🎯 Запуск бота...
⚙️ Настройка получения обновлений...
📡 Подключение к серверам Telegram...
✅ Бот запущен и готов к работе!
👂 Ожидание сообщений...
```

## 🎛️ Конфигурация

### Через файл api_tokens.txt (рекомендуется)

```
BOT_TOKEN=ваш_токен
COC_API_TOKEN=ваш_coc_токен
BOT_USERNAME=ваш_бот
YOOKASSA_SHOP_ID=ваш_shop_id
YOOKASSA_SECRET_KEY=ваш_secret_key
```

### Через переменные окружения

```bash
export BOT_TOKEN=ваш_токен
export COC_API_TOKEN=ваш_coc_токен
export BOT_USERNAME=ваш_бот
export DATABASE_PATH=путь_к_базе
export OUR_CLAN_TAG=#ваш_тег_клана
```

### Настройки по умолчанию

| Параметр | Значение по умолчанию | Описание |
|----------|----------------------|----------|
| `DATABASE_PATH` | `clashbot.db` | Путь к файлу базы данных |
| `OUR_CLAN_TAG` | `#2PQU0PLJ2` | Тег основного клана |
| `COC_API_BASE_URL` | `https://api.clashofclans.com/v1` | URL API Clash of Clans |
| `ARCHIVE_CHECK_INTERVAL` | `900` | Интервал проверки архиватора (сек) |
| `DONATION_SNAPSHOT_INTERVAL` | `21600` | Интервал снимков донатов (сек) |

## 🧪 Тестирование

### Проверка компонентов

```bash
# Тест компиляции
go build -o /tmp/clashbot-test .

# Тест зависимостей
go mod verify

# Тест с заглушками (без реальных токенов)
go test ./...
```

### Проверка работы бота

1. Запустите бота с правильными токенами
2. Найдите своего бота в Telegram
3. Отправьте команду `/start`
4. Проверьте что бот отвечает

## 🚀 Деплой

### Системная служба Linux

Создайте файл `/etc/systemd/system/clashbot.service`:

```ini
[Unit]
Description=ClashBot Go
After=network.target

[Service]
Type=simple
User=clashbot
WorkingDirectory=/opt/clashbot
ExecStart=/opt/clashbot/clashbot-go
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Активация:

```bash
sudo systemctl enable clashbot
sudo systemctl start clashbot
sudo systemctl status clashbot
```

### Docker

```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o clashbot-go .

FROM python:3.11-alpine
RUN pip install aiohttp
WORKDIR /app
COPY --from=builder /app/clashbot-go .
COPY payment_bridge.py .
COPY api_tokens.txt .
CMD ["./clashbot-go"]
```

## 📞 Поддержка

### Частые ошибки

1. **"command not found: go"** - Установите Go
2. **"no such file: api_tokens.txt"** - Создайте файл с токенами
3. **"permission denied"** - Проверьте права на файлы
4. **"cannot bind port"** - Порт уже занят
5. **"invalid token"** - Проверьте токен Telegram

### Логи и отладка

```bash
# Запуск с дополнительными логами
go run main.go 2>&1 | tee clashbot.log

# Проверка активных процессов
ps aux | grep clashbot

# Мониторинг использования ресурсов
top -p $(pgrep clashbot)
```

### Бэкап

```bash
# Создание резервной копии базы данных
cp clashbot.db clashbot_backup_$(date +%Y%m%d).db

# Автоматический бэкап (добавить в cron)
0 2 * * * /usr/bin/cp /opt/clashbot/clashbot.db /opt/backups/clashbot_$(date +\%Y\%m\%d).db
```

## 🎯 Команды бота

### Основные команды

- `/start` - Приветствие и инструкции
- `/help` - Список всех команд
- `/link <тег>` - Привязка аккаунта игрока
- `/profile` - Просмотр своего профиля
- `/clan` - Информация о клане
- `/search <тег>` - Поиск игрока или клана
- `/subscription` - Управление подпиской

### Примеры использования

```
/link #ABC123DEF
/search #PlayerTag
/search #ClanTag
```

---

🎮 **Готово!** Ваш ClashBot должен работать правильно. При возникновении проблем проверьте логи инициализации.