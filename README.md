# Clash of Clans Telegram Bot

Telegram-бот для отслеживания кланов в Clash of Clans с расширенным функционалом анализа войн.

## Особенности

- 🔗 Привязка игровых аккаунтов к Telegram
- 🛡️ Поиск и отображение информации о кланах  
- 👥 Список участников клана с сортировкой
- ⚔️ Автоматическое архивирование войн
- 📊 Статистика войн и атак
- 🔄 Конвертация HTML файлов войн в JSON

## Настройка

### 1. Конфигурация

Скопируйте файл конфигурации:
```bash
cp src/main/resources/config.properties.example src/main/resources/config.properties
```

Заполните следующие параметры в `config.properties`:

```properties
# Telegram Bot Configuration
bot.token=YOUR_BOT_TOKEN_HERE
bot.username=YOUR_BOT_USERNAME_HERE

# Clash of Clans API Configuration  
coc.api.token=YOUR_COC_API_TOKEN_HERE

# Application Configuration
app.htmls.directory=data/htmls
app.output.json=data/war_data.json
app.clan.tag=#YOUR_CLAN_TAG
```

### 2. Альтернативная настройка через переменные окружения

Вместо файла конфигурации можно использовать переменные окружения:

```bash
export BOT_TOKEN="your_bot_token"
export BOT_USERNAME="your_bot_username"  
export COC_API_TOKEN="your_coc_api_token"
export CLAN_TAG="#your_clan_tag"
```

### 3. Получение токенов

#### Telegram Bot Token
1. Найдите @BotFather в Telegram
2. Создайте нового бота командой `/newbot`
3. Следуйте инструкциям и получите токен

#### Clash of Clans API Token
1. Перейдите на https://developer.clashofclans.com/
2. Войдите в аккаунт и создайте новый ключ API
3. Укажите ваш IP-адрес

## Сборка и запуск

### Требования
- Java 11+
- Maven 3.6+

### Компиляция
```bash
mvn compile
```

### Запуск
```bash
mvn exec:java -Dexec.mainClass="org.example.Main"
```

### Создание JAR файла
```bash
mvn package
java -jar target/MainPr-1.0-SNAPSHOT-jar-with-dependencies.jar
```

## Структура проекта

```
src/main/java/org/example/
├── Main.java                      # Точка входа
├── HtmlToJsonConverter.java       # Конвертер HTML → JSON
├── WarArchiver.java              # Архиватор войн
├── bot/                          # Telegram bot компоненты
├── cocapi/                       # Clash of Clans API клиент
├── config/                       # Конфигурация
└── database/                     # Работа с базой данных
```

## Использование

### Команды бота
- `/start` - Начать работу с ботом
- **👤 Профиль** - Управление игровым профилем
- **🛡 Клан** - Информация о кланах
- **🔗 Привязать аккаунт** - Связать Telegram с игровым аккаунтом

### Конвертация HTML файлов
Поместите HTML файлы войн в директорию `data/htmls/` и запустите:
```bash
java -cp target/classes org.example.HtmlToJsonConverter
```

## База данных

Бот использует SQLite базу данных `clashbot.db` для хранения:
- Связей пользователей с игровыми аккаунтами
- Истории войн  
- Статистики атак
- Настроек уведомлений

## Troubleshooting

### Ошибка 403 при запросах к API
- Проверьте правильность API ключа
- Убедитесь, что ваш IP-адрес добавлен в настройки API ключа

### Файлы конфигурации не найдены
- Убедитесь, что `config.properties` существует в `src/main/resources/`
- Проверьте права доступа к файлу

### База данных не создается
- Проверьте права записи в директории проекта
- Убедитесь, что SQLite драйвер включен в classpath

## Разработка

### Добавление новых функций
1. Создайте новые классы в соответствующих пакетах
2. Обновите `BotConfig.java` для новых конфигурационных параметров
3. Добавьте обработчики в `MessageHandler` или `CallbackHandler`

### Тестирование
```bash
mvn test
```

## Лицензия

Этот проект предназначен для образовательных целей.