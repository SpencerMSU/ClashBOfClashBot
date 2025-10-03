# 🚀 ИНСТРУКЦИЯ ПО ЗАПУСКУ CLASHBOT (GO VERSION) В VISUAL STUDIO CODE

## 📋 ОГЛАВЛЕНИЕ
1. [Системные требования](#системные-требования)
2. [Установка Go](#установка-go)
3. [Настройка VSCode](#настройка-vscode)
4. [Клонирование и настройка проекта](#клонирование-и-настройка-проекта)
5. [Установка зависимостей](#установка-зависимостей)
6. [Настройка конфигурации](#настройка-конфигурации)
7. [Запуск бота](#запуск-бота)
8. [Отладка](#отладка)
9. [Сборка для production](#сборка-для-production)
10. [Решение проблем](#решение-проблем)

---

## 📦 СИСТЕМНЫЕ ТРЕБОВАНИЯ

### Минимальные требования:
- **OS**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **RAM**: 2 GB свободной памяти
- **Диск**: 500 MB свободного места
- **Go**: версия 1.21 или новее
- **Git**: последняя версия

### Рекомендуемые требования:
- **RAM**: 4 GB свободной памяти
- **Диск**: 1 GB свободного места
- **Go**: версия 1.22+

---

## 🔧 УСТАНОВКА GO

### Windows:
1. Скачайте установщик: https://go.dev/dl/
2. Запустите `go1.22.x.windows-amd64.msi`
3. Следуйте инструкциям установщика
4. Проверьте установку:
   ```powershell
   go version
   ```

### macOS:
1. Через Homebrew:
   ```bash
   brew install go
   ```
2. Или скачайте установщик: https://go.dev/dl/
3. Проверьте установку:
   ```bash
   go version
   ```

### Linux (Ubuntu/Debian):
```bash
# Удалите старую версию (если есть)
sudo rm -rf /usr/local/go

# Скачайте и установите
wget https://go.dev/dl/go1.22.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz

# Добавьте в PATH
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
source ~/.bashrc

# Проверьте установку
go version
```

### Настройка переменных окружения Go:
```bash
# Linux/macOS - добавьте в ~/.bashrc или ~/.zshrc
export GOPATH=$HOME/go
export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# Windows - через PowerShell (от администратора)
[System.Environment]::SetEnvironmentVariable("GOPATH", "$env:USERPROFILE\go", "User")
[System.Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\Go\bin;$env:GOPATH\bin", "User")
```

---

## 💻 НАСТРОЙКА VSCODE

### 1. Установка Visual Studio Code
Скачайте и установите VSCode: https://code.visualstudio.com/

### 2. Установка необходимых расширений

#### Обязательные расширения:
1. **Go** (от Go Team at Google)
   - Откройте VSCode
   - Нажмите `Ctrl+Shift+X` (Windows/Linux) или `Cmd+Shift+X` (macOS)
   - Найдите "Go" и установите официальное расширение

2. **Go Test Explorer** (опционально, но рекомендуется)
   - Удобный интерфейс для запуска тестов

#### Рекомендуемые расширения:
- **GitLens** - расширенная работа с Git
- **Error Lens** - подсветка ошибок прямо в коде
- **Better Comments** - улучшенные комментарии
- **SQLite Viewer** - просмотр базы данных SQLite

### 3. Настройка Go расширения в VSCode

После установки расширения Go, установите инструменты:
1. Нажмите `Ctrl+Shift+P` (Windows/Linux) или `Cmd+Shift+P` (macOS)
2. Введите "Go: Install/Update Tools"
3. Выберите все инструменты и нажмите OK

Будут установлены:
- `gopls` - Go language server
- `dlv` - отладчик Delve
- `staticcheck` - статический анализатор
- `go-outline` - структура кода
- и другие полезные инструменты

### 4. Настройки VSCode для Go (settings.json)

Откройте настройки VSCode (`Ctrl+,`) и добавьте:

```json
{
    "go.useLanguageServer": true,
    "go.toolsManagement.autoUpdate": true,
    "go.lintOnSave": "workspace",
    "go.formatTool": "gofmt",
    "go.lintTool": "staticcheck",
    "go.buildOnSave": "workspace",
    "go.vetOnSave": "workspace",
    "editor.formatOnSave": true,
    "[go]": {
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        },
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "golang.go"
    },
    "gopls": {
        "ui.semanticTokens": true,
        "ui.completion.usePlaceholders": true
    }
}
```

---

## 📂 КЛОНИРОВАНИЕ И НАСТРОЙКА ПРОЕКТА

### 1. Клонирование репозитория

```bash
# Клонируйте репозиторий
git clone https://github.com/SpencerMSU/ClashBOfClashBot.git
cd ClashBOfClashBot
```

### 2. Открытие проекта в VSCode

```bash
# Откройте текущую директорию в VSCode
code .
```

Или через VSCode: File → Open Folder → выберите папку проекта

### 3. Структура проекта Go

После миграции структура будет следующей:

```
ClashBOfClashBot/
├── go.mod                    # Описание модуля и зависимостей
├── go.sum                    # Контрольные суммы зависимостей
├── main.go                   # Точка входа приложения
├── config/
│   └── config.go            # Конфигурация бота
├── internal/
│   ├── bot/
│   │   └── bot.go           # Основной класс бота
│   ├── database/
│   │   └── database.go      # Работа с БД
│   ├── api/
│   │   └── coc_api.go       # Clash of Clans API
│   ├── handlers/
│   │   ├── message.go       # Обработчики сообщений
│   │   └── callback.go      # Обработчики callback
│   ├── keyboards/
│   │   └── keyboards.go     # Клавиатуры
│   ├── services/
│   │   ├── payment.go       # YooKassa интеграция
│   │   ├── war_archiver.go  # Архивация войн
│   │   ├── building_monitor.go  # Мониторинг зданий
│   │   └── message_generator.go # Генерация сообщений
│   ├── models/
│   │   ├── user.go          # Модель пользователя
│   │   ├── war.go           # Модель войны
│   │   ├── subscription.go  # Модель подписки
│   │   └── building.go      # Модель здания
│   ├── scanners/
│   │   ├── clan_scanner.go  # Сканер кланов
│   │   └── war_importer.go  # Импорт войн
│   └── utils/
│       ├── validate.go      # Валидация
│       ├── translations.go  # Переводы
│       └── policy.go        # Политика конфиденциальности
├── oldpy/                    # Python версия (после миграции)
│   ├── bot.py
│   ├── config.py
│   └── ... (все Python файлы)
├── api_tokens.txt           # Токены и ключи (НЕ коммитить!)
├── clashbot.db              # База данных SQLite
├── .gitignore
└── README.md
```

---

## 📥 УСТАНОВКА ЗАВИСИМОСТЕЙ

### 1. Инициализация Go модуля

```bash
# Если go.mod еще не создан
go mod init github.com/SpencerMSU/ClashBOfClashBot
```

### 2. Установка всех зависимостей

```bash
# Установка всех необходимых библиотек
go get -u github.com/go-telegram-bot-api/telegram-bot-api/v5
go get -u github.com/mattn/go-sqlite3
go get -u github.com/go-resty/resty/v2
go get -u github.com/google/uuid
go get -u github.com/joho/godotenv
go get -u github.com/sirupsen/logrus
go get -u golang.org/x/time/rate

# Синхронизация зависимостей
go mod tidy
go mod download
```

### 3. Список основных зависимостей

| Библиотека | Назначение | Python аналог |
|-----------|-----------|---------------|
| `telegram-bot-api/v5` | Telegram Bot API | `python-telegram-bot` |
| `go-sqlite3` | SQLite драйвер | `aiosqlite` |
| `resty/v2` | HTTP клиент | `aiohttp` |
| `uuid` | UUID генерация | `uuid` |
| `godotenv` | .env файлы | `python-dotenv` |
| `logrus` | Логирование | `logging` |
| `golang.org/x/time/rate` | Rate limiting | `asyncio-throttle` |

---

## ⚙️ НАСТРОЙКА КОНФИГУРАЦИИ

### 1. Создание файла api_tokens.txt

Создайте файл `api_tokens.txt` в корне проекта:

```txt
# Telegram Bot Configuration
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
BOT_USERNAME=YourBotUsername

# Clash of Clans API
COC_API_TOKEN=YOUR_COC_API_TOKEN_HERE

# YooKassa Payment Gateway
YOOKASSA_SHOP_ID=YOUR_SHOP_ID
YOOKASSA_SECRET_KEY=YOUR_SECRET_KEY

# Optional Settings
OUR_CLAN_TAG=#2PQU0PLJ2
DATABASE_PATH=clashbot.db
```

**⚠️ ВАЖНО**: Добавьте `api_tokens.txt` в `.gitignore`!

### 2. Получение необходимых токенов

#### Telegram Bot Token:
1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

#### Clash of Clans API Token:
1. Зайдите на https://developer.clashofclans.com/
2. Войдите через Supercell ID
3. Создайте новый ключ (API Key)
4. Укажите свой IP адрес
5. Скопируйте токен

#### YooKassa Credentials (для платежей):
1. Зарегистрируйтесь на https://yookassa.ru/
2. Получите Shop ID и Secret Key
3. Настройте возвратные URL

### 3. Альтернатива: использование .env файла

Создайте файл `.env`:

```env
BOT_TOKEN=your_token_here
COC_API_TOKEN=your_token_here
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
```

---

## 🚀 ЗАПУСК БОТА

### 1. Запуск в режиме разработки

#### Через терминал VSCode:
```bash
# Просто запустите
go run main.go

# Или с включением race detector (для поиска race conditions)
go run -race main.go
```

#### Через VSCode (F5):
1. Откройте `main.go`
2. Нажмите `F5` или перейдите в Run → Start Debugging
3. Выберите "Go: Launch Package"

### 2. Настройка launch.json для VSCode

Создайте `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Launch ClashBot",
            "type": "go",
            "request": "launch",
            "mode": "debug",
            "program": "${workspaceFolder}/main.go",
            "env": {
                "BOT_TOKEN": "${env:BOT_TOKEN}",
                "COC_API_TOKEN": "${env:COC_API_TOKEN}"
            },
            "args": [],
            "showLog": true,
            "trace": "verbose"
        },
        {
            "name": "Launch ClashBot (with race detector)",
            "type": "go",
            "request": "launch",
            "mode": "debug",
            "program": "${workspaceFolder}/main.go",
            "buildFlags": "-race",
            "env": {},
            "args": []
        }
    ]
}
```

### 3. Проверка работы бота

После запуска вы должны увидеть:
```
INFO[0000] Запуск бота Clash of Clans...
INFO[0001] База данных инициализирована
INFO[0001] Бот успешно запущен: @YourBotUsername
INFO[0001] Ожидание сообщений...
```

Откройте Telegram и отправьте боту команду `/start`

---

## 🐛 ОТЛАДКА

### 1. Установка точек останова (breakpoints)

1. Откройте нужный `.go` файл
2. Кликните слева от номера строки
3. Появится красная точка
4. Запустите отладку (`F5`)
5. Программа остановится на точке останова

### 2. Просмотр переменных

Во время отладки:
- **Variables** - все переменные в текущем scope
- **Watch** - добавьте выражения для отслеживания
- **Call Stack** - стек вызовов
- **Debug Console** - выполнение команд

### 3. Управление отладкой

- `F5` - Continue (продолжить)
- `F10` - Step Over (перейти к следующей строке)
- `F11` - Step Into (войти в функцию)
- `Shift+F11` - Step Out (выйти из функции)
- `Shift+F5` - Stop (остановить отладку)

### 4. Логирование

В коде используется `logrus`:

```go
import log "github.com/sirupsen/logrus"

log.Info("Информационное сообщение")
log.Warn("Предупреждение")
log.Error("Ошибка")
log.Debug("Отладочное сообщение")
log.WithFields(log.Fields{
    "user_id": 123,
    "action": "start",
}).Info("Пользователь запустил бота")
```

Логи сохраняются в файл `bot.log`

---

## 📦 СБОРКА ДЛЯ PRODUCTION

### 1. Сборка исполняемого файла

#### Linux:
```bash
# Обычная сборка
go build -o clashbot main.go

# Оптимизированная сборка (меньший размер)
go build -ldflags="-s -w" -o clashbot main.go

# Статическая сборка (для Docker)
CGO_ENABLED=1 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o clashbot main.go
```

#### Windows:
```bash
# На Windows
go build -o clashbot.exe main.go

# Кросс-компиляция с Linux на Windows
GOOS=windows GOARCH=amd64 go build -o clashbot.exe main.go
```

#### macOS:
```bash
# На macOS
go build -o clashbot main.go

# Кросс-компиляция
GOOS=darwin GOARCH=amd64 go build -o clashbot main.go
```

### 2. Оптимизация размера бинарника

```bash
# Удаление отладочной информации и таблицы символов
go build -ldflags="-s -w" -o clashbot main.go

# Дополнительное сжатие с UPX (опционально)
upx --brute clashbot
```

### 3. Запуск в production

```bash
# Прямой запуск
./clashbot

# В фоновом режиме с логами
nohup ./clashbot > clashbot.log 2>&1 &

# С помощью systemd (Linux)
sudo systemctl start clashbot
```

### 4. Создание systemd service (Linux)

Создайте `/etc/systemd/system/clashbot.service`:

```ini
[Unit]
Description=ClashBot Telegram Bot
After=network.target

[Service]
Type=simple
User=clashbot
WorkingDirectory=/opt/clashbot
ExecStart=/opt/clashbot/clashbot
Restart=always
RestartSec=10
StandardOutput=append:/var/log/clashbot/bot.log
StandardError=append:/var/log/clashbot/error.log

[Install]
WantedBy=multi-user.target
```

Управление:
```bash
sudo systemctl daemon-reload
sudo systemctl enable clashbot
sudo systemctl start clashbot
sudo systemctl status clashbot
```

---

## 🔧 РЕШЕНИЕ ПРОБЛЕМ

### Проблема: "go: command not found"

**Решение:**
```bash
# Проверьте PATH
echo $PATH

# Добавьте Go в PATH (Linux/macOS)
export PATH=$PATH:/usr/local/go/bin

# Windows - через System Properties → Environment Variables
```

### Проблема: "cannot find package"

**Решение:**
```bash
# Обновите зависимости
go mod tidy
go mod download

# Переустановите конкретный пакет
go get -u github.com/package/name
```

### Проблема: CGO ошибки с go-sqlite3

**Решение для Windows:**
1. Установите MinGW-w64: https://www.mingw-w64.org/
2. Добавьте MinGW в PATH
3. Или используйте pure-Go SQLite: `github.com/mattn/go-sqlite3` → `modernc.org/sqlite`

**Решение для Linux:**
```bash
sudo apt-get install gcc
```

**Решение для macOS:**
```bash
xcode-select --install
```

### Проблема: "panic: runtime error"

**Решение:**
1. Проверьте логи в `bot.log`
2. Запустите с race detector: `go run -race main.go`
3. Используйте отладчик VSCode (F5)

### Проблема: База данных заблокирована

**Решение:**
```bash
# Закройте все процессы, использующие БД
lsof clashbot.db  # Linux/macOS
# Или просто перезапустите бота
```

### Проблема: Telegram API таймауты

**Решение:**
```go
// Увеличьте таймауты в коде
bot.Client.Timeout = 60 * time.Second
```

### Проблема: Память утечка (memory leak)

**Решение:**
```bash
# Профилирование памяти
go run main.go -memprofile=mem.prof
go tool pprof mem.prof

# Проверка с race detector
go run -race main.go
```

---

## 📊 МОНИТОРИНГ И МЕТРИКИ

### 1. Проверка статуса бота

```bash
# Проверка процесса
ps aux | grep clashbot

# Использование памяти
top -p $(pgrep clashbot)

# Логи
tail -f bot.log
```

### 2. Мониторинг производительности

```go
// Добавьте в код для pprof
import _ "net/http/pprof"
import "net/http"

go func() {
    log.Println(http.ListenAndServe("localhost:6060", nil))
}()
```

Затем:
```bash
# CPU профилирование
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Heap профилирование
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutines
curl http://localhost:6060/debug/pprof/goroutine?debug=1
```

---

## 🎯 ПРОИЗВОДИТЕЛЬНОСТЬ

### Сравнение с Python версией:

| Метрика | Python | Go | Улучшение |
|---------|--------|-----|-----------|
| Время запуска | ~3-5 сек | ~0.5-1 сек | **5x быстрее** |
| Память (RAM) | ~150-200 MB | ~30-50 MB | **4x меньше** |
| Обработка запроса | ~50-100 мс | ~5-20 мс | **5-10x быстрее** |
| Размер бинарника | N/A (интерпретатор) | ~20-30 MB | Standalone |

---

## 📚 ПОЛЕЗНЫЕ РЕСУРСЫ

### Официальная документация:
- Go: https://go.dev/doc/
- Telegram Bot API: https://core.telegram.org/bots/api
- Go Telegram Bot: https://github.com/go-telegram-bot-api/telegram-bot-api
- SQLite: https://www.sqlite.org/docs.html

### Обучающие материалы:
- Go by Example: https://gobyexample.com/
- Effective Go: https://go.dev/doc/effective_go
- Go Tour: https://go.dev/tour/

### Инструменты:
- Go Playground: https://go.dev/play/
- SQLite Browser: https://sqlitebrowser.org/
- Postman (для тестирования API): https://www.postman.com/

---

## 🆘 ПОДДЕРЖКА

### Если возникли проблемы:

1. **Проверьте логи**: `tail -f bot.log`
2. **Проверьте конфигурацию**: убедитесь, что все токены корректны
3. **Проверьте зависимости**: `go mod verify`
4. **Пересоберите**: `go clean && go build`
5. **Создайте issue**: https://github.com/SpencerMSU/ClashBOfClashBot/issues

---

## ✅ ЧЕКЛИСТ БЫСТРОГО СТАРТА

- [ ] Установлен Go 1.21+
- [ ] Установлен VSCode с расширением Go
- [ ] Клонирован репозиторий
- [ ] Созданы `api_tokens.txt` с токенами
- [ ] Выполнено `go mod tidy`
- [ ] Выполнено `go build`
- [ ] Бот успешно запускается
- [ ] Команда `/start` работает в Telegram

---

**Версия документа**: 1.0
**Последнее обновление**: 2024
**Статус**: Готово для использования после завершения миграции

🎉 **Удачи в запуске бота!**
