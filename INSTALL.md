# 🚀 Установка ClashBot на Ubuntu 24.04

## 📋 Содержание

1. [Введение](#введение)
2. [Требования к системе](#требования-к-системе)
3. [Установка зависимостей](#установка-зависимостей)
4. [Настройка бота](#настройка-бота)
5. [Запуск бота](#запуск-бота)
6. [Автозапуск через systemd](#автозапуск-через-systemd)
7. [Проверка работы](#проверка-работы)
8. [Обновление бота](#обновление-бота)
9. [Устранение неполадок](#устранение-неполадок)

---

## 🎮 Введение

**ClashBot** - это Telegram бот для мониторинга и анализа кланов и игроков в игре Clash of Clans. 

### Основные возможности:
- 🎯 **Профиль игрока** - просмотр детальной статистики вашего аккаунта
- 🏰 **Информация о клане** - статистика клана, список участников
- ⚔️ **Архив войн** - автоматическое сохранение истории клановых войн
- 🏗️ **Отслеживание улучшений** - уведомления о завершении строительства (Premium)
- 💎 **Premium функции** - расширенная статистика и множественные профили

### Технические характеристики:
- **Язык программирования**: Go (Golang) 1.21+
- **База данных**: SQLite 3
- **API**: Clash of Clans Official API
- **Telegram**: telegram-bot-api v5
- **Платежи**: YooKassa (для Premium подписок)

### Архитектура:
- **Основной бот** - обработка команд и сообщений пользователей
- **War Archiver** - фоновый сервис для автоматического сохранения завершенных войн
- **Building Monitor** - фоновый сервис для отслеживания улучшений зданий (для Premium пользователей)
- **База данных** - хранение информации о пользователях, войнах и подписках

---

## 💻 Требования к системе

### Минимальные требования:
- **OS**: Ubuntu 24.04 LTS (64-bit)
- **RAM**: 512 MB (рекомендуется 1 GB)
- **Диск**: 100 MB свободного места
- **CPU**: 1 ядро (рекомендуется 2)
- **Сеть**: Стабильное интернет-соединение

### Необходимые компоненты:
- Go 1.21 или выше
- SQLite3
- Git

---

## 🔧 Установка зависимостей

### Шаг 1: Обновление системы

```bash
sudo apt update
sudo apt upgrade -y
```

### Шаг 2: Установка Go

```bash
# Скачиваем последнюю версию Go (проверьте актуальную версию на golang.org)
wget https://go.dev/dl/go1.21.6.linux-amd64.tar.gz

# Удаляем старую версию (если есть)
sudo rm -rf /usr/local/go

# Распаковываем новую версию
sudo tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz

# Удаляем архив
rm go1.21.6.linux-amd64.tar.gz

# Добавляем Go в PATH
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc

# Применяем изменения
source ~/.bashrc

# Проверяем установку
go version
```

Вы должны увидеть что-то вроде: `go version go1.21.6 linux/amd64`

### Шаг 3: Установка дополнительных зависимостей

```bash
# Устанавливаем необходимые пакеты
sudo apt install -y git sqlite3 build-essential

# Проверяем установку
git --version
sqlite3 --version
```

---

## ⚙️ Настройка бота

### Шаг 1: Клонирование репозитория

```bash
# Переходим в домашнюю директорию
cd ~

# Клонируем репозиторий
git clone https://github.com/SpencerMSU/ClashBOfClashBot.git

# Переходим в директорию проекта
cd ClashBOfClashBot
```

### Шаг 2: Получение необходимых токенов

#### 2.1 Telegram Bot Token

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям:
   - Введите имя бота (например, "My Clash Bot")
   - Введите username бота (должен заканчиваться на "bot", например, "my_clash_bot")
4. Скопируйте полученный токен (выглядит как `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 2.2 Clash of Clans API Token

1. Зарегистрируйтесь на [Clash of Clans Developer Portal](https://developer.clashofclans.com/)
2. Войдите в аккаунт
3. Перейдите в раздел "My Account"
4. Нажмите "Create New Key"
5. Заполните форму:
   - **Name**: ClashBot (любое название)
   - **Description**: Bot API key (любое описание)
   - **IP Address**: Ваш IP адрес сервера (узнать можно командой `curl ifconfig.me`)
6. Скопируйте полученный токен

#### 2.3 YooKassa (опционально, для Premium подписок)

1. Зарегистрируйтесь на [YooKassa](https://yookassa.ru/)
2. Перейдите в личный кабинет
3. Получите:
   - **Shop ID** (идентификатор магазина)
   - **Secret Key** (секретный ключ)

### Шаг 3: Конфигурация бота

Создайте файл с токенами:

```bash
cd ~/ClashBOfClashBot
nano api_tokens.txt
```

Вставьте следующее содержимое (замените значения на свои):

```
BOT_TOKEN=ваш_telegram_bot_token
BOT_USERNAME=ваш_bot_username
COC_API_TOKEN=ваш_clash_of_clans_api_token
YOOKASSA_SHOP_ID=ваш_yookassa_shop_id
YOOKASSA_SECRET_KEY=ваш_yookassa_secret_key
```

Сохраните файл:
- Нажмите `Ctrl + O` (сохранить)
- Нажмите `Enter` (подтвердить имя файла)
- Нажмите `Ctrl + X` (выход)

**Важно**: Если вы не планируете использовать Premium подписки, можете не указывать YooKassa параметры.

### Шаг 4: Установка Go зависимостей

```bash
cd ~/ClashBOfClashBot

# Загрузка зависимостей
go mod download

# Проверка зависимостей
go mod verify
```

---

## 🚀 Запуск бота

### Вариант 1: Запуск в foreground режиме (для тестирования)

```bash
cd ~/ClashBOfClashBot

# Сборка проекта
go build -o clashbot main.go

# Запуск бота
./clashbot
```

Вы увидите логи запуска:

```
🚀 Запуск бота Clash of Clans...
✅ Конфигурация загружена успешно
📱 Bot Username: your_bot_username
🗄️  Database: clashbot.db

┌─────────────────────────────────────────────┐
│                                             │
│    🎮 ClashBot - Golang Edition 🎮         │
│                                             │
│    ✅ Конфигурация загружена                │
│    🔄 Инициализация компонентов...          │
│                                             │
└─────────────────────────────────────────────┘

✅ Бот успешно инициализирован
🤖 Бот запущен и готов к работе!
```

Для остановки нажмите `Ctrl + C`.

### Вариант 2: Запуск в background режиме

```bash
cd ~/ClashBOfClashBot

# Запуск в фоновом режиме с перенаправлением логов
nohup ./clashbot > bot.log 2>&1 &

# Проверка логов
tail -f bot.log
```

---

## 🔄 Автозапуск через systemd

Для автоматического запуска бота при старте системы используйте systemd.

### Шаг 1: Создание systemd service файла

```bash
sudo nano /etc/systemd/system/clashbot.service
```

Вставьте следующее содержимое (замените `your_username` на ваше имя пользователя):

```ini
[Unit]
Description=ClashBot - Clash of Clans Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/ClashBOfClashBot
ExecStart=/home/your_username/ClashBOfClashBot/clashbot
Restart=always
RestartSec=10
StandardOutput=append:/home/your_username/ClashBOfClashBot/bot.log
StandardError=append:/home/your_username/ClashBOfClashBot/bot_error.log

# Environment variables (опционально, если не используете api_tokens.txt)
# Environment="BOT_TOKEN=your_token"
# Environment="COC_API_TOKEN=your_token"

[Install]
WantedBy=multi-user.target
```

Сохраните файл (`Ctrl + O`, `Enter`, `Ctrl + X`).

### Шаг 2: Активация и запуск сервиса

```bash
# Перезагрузка systemd конфигурации
sudo systemctl daemon-reload

# Включение автозапуска при старте системы
sudo systemctl enable clashbot

# Запуск бота
sudo systemctl start clashbot

# Проверка статуса
sudo systemctl status clashbot
```

### Шаг 3: Управление сервисом

```bash
# Остановка бота
sudo systemctl stop clashbot

# Перезапуск бота
sudo systemctl restart clashbot

# Просмотр логов
sudo journalctl -u clashbot -f

# Или через файл логов
tail -f ~/ClashBOfClashBot/bot.log
```

---

## ✅ Проверка работы

### 1. Проверка процесса

```bash
# Проверка запущенных процессов
ps aux | grep clashbot

# Проверка портов (если используется webhook)
sudo netstat -tulpn | grep clashbot
```

### 2. Проверка базы данных

```bash
cd ~/ClashBOfClashBot

# Открытие базы данных
sqlite3 clashbot.db

# Просмотр таблиц
.tables

# Проверка пользователей
SELECT * FROM users LIMIT 5;

# Выход
.quit
```

### 3. Тестирование в Telegram

1. Найдите вашего бота в Telegram по username
2. Нажмите "Start" или отправьте `/start`
3. Вы должны увидеть главное меню бота
4. Попробуйте команды:
   - **👤 Профиль** - управление вашим игровым аккаунтом
   - **🏰 Клан** - информация о вашем клане
   - **💎 Подписки** - информация о Premium функциях

---

## 🔄 Обновление бота

### Шаг 1: Остановка бота

```bash
# Если используете systemd
sudo systemctl stop clashbot

# Если запущен вручную
pkill clashbot
```

### Шаг 2: Обновление кода

```bash
cd ~/ClashBOfClashBot

# Сохранение изменений (если есть)
git stash

# Получение обновлений
git pull origin master

# Восстановление изменений (если были)
git stash pop

# Обновление зависимостей
go mod download
```

### Шаг 3: Пересборка

```bash
# Пересборка проекта
go build -o clashbot main.go
```

### Шаг 4: Запуск обновленной версии

```bash
# Если используете systemd
sudo systemctl start clashbot

# Если запускаете вручную
./clashbot
```

---

## 🔧 Устранение неполадок

### Проблема 1: Бот не запускается

**Симптом**: Ошибка "BOT_TOKEN is not set"

**Решение**:
```bash
# Проверьте файл api_tokens.txt
cat ~/ClashBOfClashBot/api_tokens.txt

# Убедитесь, что токены указаны правильно (без лишних пробелов)
nano ~/ClashBOfClashBot/api_tokens.txt
```

### Проблема 2: Ошибка подключения к Clash of Clans API

**Симптом**: Ошибки "403 Forbidden" или "Invalid IP"

**Решение**:
1. Проверьте ваш IP адрес:
   ```bash
   curl ifconfig.me
   ```
2. Обновите IP адрес в [Clash of Clans Developer Portal](https://developer.clashofclans.com/)
3. Перезапустите бота

### Проблема 3: База данных заблокирована

**Симптом**: Ошибка "database is locked"

**Решение**:
```bash
# Остановите все процессы бота
pkill clashbot

# Проверьте блокировки
lsof ~/ClashBOfClashBot/clashbot.db

# Перезапустите бота
sudo systemctl start clashbot
```

### Проблема 4: Бот не отвечает на команды

**Решение**:
```bash
# Проверьте логи
tail -n 100 ~/ClashBOfClashBot/bot.log

# Или через systemd
sudo journalctl -u clashbot -n 100 --no-pager

# Перезапустите бота
sudo systemctl restart clashbot
```

### Проблема 5: Большой размер логов

**Решение**: Настройка ротации логов
```bash
sudo nano /etc/logrotate.d/clashbot
```

Добавьте:
```
/home/your_username/ClashBOfClashBot/bot.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0644 your_username your_username
}
```

---

## 📊 Мониторинг и производительность

### Просмотр использования ресурсов

```bash
# Использование CPU и RAM
top -p $(pgrep clashbot)

# Размер базы данных
du -h ~/ClashBOfClashBot/clashbot.db

# Размер логов
du -h ~/ClashBOfClashBot/bot.log
```

### Статистика бота

```bash
cd ~/ClashBOfClashBot

# Количество пользователей
sqlite3 clashbot.db "SELECT COUNT(*) FROM users;"

# Количество сохраненных войн
sqlite3 clashbot.db "SELECT COUNT(*) FROM wars;"

# Активных Premium подписок
sqlite3 clashbot.db "SELECT COUNT(*) FROM subscriptions WHERE end_date > datetime('now');"
```

---

## 🛡️ Безопасность

### Рекомендации:

1. **Защита токенов**:
   ```bash
   # Ограничение прав доступа к файлу токенов
   chmod 600 ~/ClashBOfClashBot/api_tokens.txt
   ```

2. **Обновления системы**:
   ```bash
   # Регулярно обновляйте систему
   sudo apt update && sudo apt upgrade -y
   ```

3. **Firewall**:
   ```bash
   # Настройка базовых правил firewall
   sudo ufw allow 22/tcp  # SSH
   sudo ufw enable
   ```

4. **Бэкапы базы данных**:
   ```bash
   # Создание резервной копии
   cp ~/ClashBOfClashBot/clashbot.db ~/ClashBOfClashBot/clashbot.db.backup

   # Автоматический бэкап (добавьте в crontab)
   crontab -e
   # Добавьте строку:
   # 0 3 * * * cp ~/ClashBOfClashBot/clashbot.db ~/ClashBOfClashBot/backups/clashbot.db.$(date +\%Y\%m\%d)
   ```

---

## 📞 Поддержка

### Проблемы с установкой?

1. Проверьте логи: `tail -f ~/ClashBOfClashBot/bot.log`
2. Создайте Issue на [GitHub](https://github.com/SpencerMSU/ClashBOfClashBot/issues)
3. Обратитесь к администратору: [@Negodayo](https://t.me/Negodayo)

### Полезные ссылки:

- [Clash of Clans API Documentation](https://developer.clashofclans.com/api-docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Go Documentation](https://golang.org/doc/)

---

## 🎉 Готово!

Ваш ClashBot теперь установлен и готов к работе! 

### Следующие шаги:

1. Протестируйте основные функции в Telegram
2. Привяжите свой игровой аккаунт Clash of Clans
3. Изучите Premium возможности
4. Настройте уведомления (если есть Premium подписка)

**Приятного использования!** 🎮
