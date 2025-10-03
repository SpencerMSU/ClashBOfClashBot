# 🎯 СТРУКТУРА ПОЛНОГО ПЕРЕНОСА БОТА НА GO

## 📋 КРАТКОЕ РЕЗЮМЕ

**Статус**: Фаза 1 завершена ✅  
**Дата начала**: 2024  
**Всего компонентов для миграции**: 22  
**Завершено**: 7 (32%)  
**Python строк в oldpy/**: ~9000  
**Go строк готово**: ~600  

---

## 🗂️ ПОЛНАЯ СТРУКТУРА ПЕРЕНОСА

### ✅ ЗАВЕРШЕННЫЕ КОМПОНЕНТЫ

#### 1. Конфигурация (config/)
**Файл**: `config/config.go` (160 строк)

**Функции**:
- ✅ `LoadConfig()` - загрузка конфигурации
- ✅ `Validate()` - валидация параметров
- ✅ `readAPITokens()` - чтение из api_tokens.txt
- ✅ `getConfigValue()` - получение значений с приоритетами

**Оригинал**: `oldpy/config.py` (78 строк)

**Структура Config**:
```go
type Config struct {
    BotToken              string
    BotUsername           string
    CocAPIToken           string
    CocAPIBaseURL         string
    YooKassaShopID        string
    YooKassaSecretKey     string
    DatabasePath          string
    OurClanTag            string
    ArchiveCheckInterval  int
    DonationSnapshotInterval int
}
```

---

#### 2. Модели (internal/models/)

##### 2.1 User (user.go) - 15 строк
**Оригинал**: `oldpy/models/user.py` (15 строк)

**Структура**:
```go
type User struct {
    TelegramID int64
    PlayerTag  string
}
```

**Функции**:
- ✅ `NewUser()` - конструктор

---

##### 2.2 Subscription (subscription.go) - 65 строк
**Оригинал**: `oldpy/models/subscription.py` (41 строк)

**Структура**:
```go
type Subscription struct {
    TelegramID       int64
    SubscriptionType string
    StartDate        time.Time
    EndDate          time.Time
    IsActive         bool
    PaymentID        *string
    Amount           *float64
    Currency         string
}
```

**Функции**:
- ✅ `NewSubscription()` - конструктор
- ✅ `IsExpired()` - проверка истечения
- ✅ `DaysRemaining()` - дни до истечения
- ✅ `IsPremium()` - проверка Premium
- ✅ `IsProPlus()` - проверка PRO PLUS

---

##### 2.3 UserProfile (user_profile.go) - 25 строк
**Оригинал**: `oldpy/models/user_profile.py` (23 строк)

**Структура**:
```go
type UserProfile struct {
    ID          int64
    TelegramID  int64
    PlayerTag   string
    ProfileName *string
    IsPrimary   bool
    CreatedAt   time.Time
}
```

**Функции**:
- ✅ `NewUserProfile()` - конструктор

---

##### 2.4 War (war.go) - 60 строк
**Оригинал**: `oldpy/models/war.py` (45 строк)

**Структуры**:
```go
type WarToSave struct {
    ClanTag                       string
    State                         string
    TeamSize                      int
    PreparationTime               time.Time
    StartTime                     time.Time
    EndTime                       time.Time
    ClanName                      string
    ClanLevel                     int
    ClanStars                     int
    ClanDestructionPercentage     float64
    OpponentName                  string
    OpponentTag                   string
    OpponentLevel                 int
    OpponentStars                 int
    OpponentDestructionPercentage float64
    Result                        string
    IsCWL                         bool
}

type AttackData struct {
    AttackerTag           string
    AttackerName          string
    DefenderTag           string
    DefenderName          string
    Stars                 int
    DestructionPercentage float64
    Order                 int
    IsViolation           bool
}
```

**Функции**:
- ✅ `NewWarToSave()` - конструктор войны
- ✅ `NewAttackData()` - конструктор атаки

---

##### 2.5 Building (building.go) - 70 строк
**Оригинал**: `oldpy/models/building.py` (55 строк)

**Структуры**:
```go
type BuildingSnapshot struct {
    PlayerTag    string
    BuildingType string
    Level        int
    SnapshotTime time.Time
}

type BuildingUpgrade struct {
    PlayerTag    string
    PlayerName   string
    BuildingType string
    OldLevel     int
    NewLevel     int
    UpgradeTime  time.Time
}

type BuildingTracker struct {
    TelegramID           int64
    PlayerTag            string
    LastCheck            time.Time
    NotificationsEnabled bool
}
```

**Функции**:
- ✅ `NewBuildingSnapshot()` - конструктор снимка
- ✅ `NewBuildingUpgrade()` - конструктор апгрейда
- ✅ `NewBuildingTracker()` - конструктор трекера

---

##### 2.6 LinkedClan (linked_clan.go) - 25 строк
**Оригинал**: `oldpy/models/linked_clan.py` (20 строк)

**Структура**:
```go
type LinkedClan struct {
    ClanTag     string
    ClanName    string
    LinkedBy    int64
    LinkedAt    time.Time
    IsActive    bool
    Description *string
}
```

**Функции**:
- ✅ `NewLinkedClan()` - конструктор

---

#### 3. Точка входа (main.go) - 80 строк

**Функции**:
- ✅ Загрузка конфигурации
- ✅ Graceful shutdown
- ✅ Отображение статуса миграции
- ✅ Signal handling (SIGTERM, SIGINT)

---

## ⏳ КОМПОНЕНТЫ В РАЗРАБОТКЕ

### 🗄️ База данных (internal/database/database.go)

**Планируется**: ~1000 строк  
**Оригинал**: `oldpy/database.py` (646 строк)

#### Таблицы (10 штук):

1. **users** - основные пользователи
2. **user_profiles** - профили для PRO PLUS
3. **subscriptions** - подписки
4. **wars** - архив войн
5. **attacks** - атаки в войнах
6. **cwl_seasons** - CWL сезоны
7. **cwl_rounds** - раунды CWL
8. **linked_clans** - связанные кланы
9. **building_snapshots** - снимки зданий
10. **notifications** - настройки уведомлений

#### Функции для реализации:

##### Users
- [ ] `InitDB()` - инициализация всех таблиц
- [ ] `CreateUser(user *models.User)` - создание пользователя
- [ ] `GetUser(telegramID int64)` - получение пользователя
- [ ] `GetUserByPlayerTag(playerTag string)` - поиск по тегу
- [ ] `UpdateUser(user *models.User)` - обновление
- [ ] `DeleteUser(telegramID int64)` - удаление

##### User Profiles (Premium)
- [ ] `CreateProfile(profile *models.UserProfile)` - создание профиля
- [ ] `GetProfiles(telegramID int64)` - все профили пользователя
- [ ] `GetProfile(telegramID int64, playerTag string)` - конкретный профиль
- [ ] `UpdateProfile(profile *models.UserProfile)` - обновление
- [ ] `DeleteProfile(id int64)` - удаление
- [ ] `SetPrimaryProfile(telegramID int64, playerTag string)` - установка основного
- [ ] `GetPrimaryProfile(telegramID int64)` - получение основного

##### Subscriptions
- [ ] `CreateSubscription(sub *models.Subscription)` - создание подписки
- [ ] `GetSubscription(telegramID int64)` - получение подписки
- [ ] `UpdateSubscription(sub *models.Subscription)` - обновление
- [ ] `CheckExpiredSubscriptions()` - проверка истекших
- [ ] `GrantPermanentSubscription(telegramID int64, subType string)` - вечная подписка
- [ ] `GetSubscriptionHistory(telegramID int64)` - история

##### Wars
- [ ] `SaveWar(war *models.WarToSave)` - сохранение войны
- [ ] `GetWars(clanTag string, limit int)` - список войн
- [ ] `GetWarDetails(endTime string)` - детали войны
- [ ] `DeleteOldWars(days int)` - удаление старых
- [ ] `GetWarStats(clanTag string)` - статистика

##### Attacks
- [ ] `SaveAttacks(warEndTime string, attacks []models.AttackData)` - сохранение атак
- [ ] `GetAttacks(warEndTime string)` - получение атак войны
- [ ] `GetPlayerAttacks(playerTag string)` - атаки игрока

##### CWL
- [ ] `SaveCWLSeason(season CWLSeason)` - сохранение сезона
- [ ] `GetCWLSeasons(clanTag string)` - список сезонов
- [ ] `SaveCWLRound(round CWLRound)` - сохранение раунда
- [ ] `GetCWLRounds(seasonID int64)` - раунды сезона

##### Building Monitoring
- [ ] `SaveBuildingSnapshot(snapshot *models.BuildingSnapshot)` - сохранение снимка
- [ ] `GetBuildingChanges(playerTag string)` - получение изменений
- [ ] `DeleteOldSnapshots(days int)` - удаление старых
- [ ] `TrackBuildings(tracker *models.BuildingTracker)` - включение трекинга
- [ ] `UntrackBuildings(telegramID int64)` - отключение

##### Linked Clans
- [ ] `LinkClan(clan *models.LinkedClan)` - привязка клана
- [ ] `GetLinkedClans()` - список кланов
- [ ] `UnlinkClan(clanTag string)` - отвязка

##### Notifications
- [ ] `ToggleNotifications(telegramID int64)` - переключение уведомлений
- [ ] `GetNotificationSettings(telegramID int64)` - получение настроек

---

### 🌐 COC API Client (internal/api/coc_api.go)

**Планируется**: ~800 строк  
**Оригинал**: `oldpy/coc_api.py` (~700 строк)

#### Функции для реализации:

##### Основные методы
- [ ] `NewCocAPIClient(token string)` - конструктор
- [ ] `makeRequest(endpoint string)` - базовый HTTP запрос
- [ ] `Close()` - закрытие клиента

##### Player API
- [ ] `GetPlayer(playerTag string)` - информация об игроке
- [ ] `VerifyPlayerToken(playerTag, token string)` - верификация токена

##### Clan API
- [ ] `GetClan(clanTag string)` - информация о клане
- [ ] `GetClanMembers(clanTag string)` - участники клана
- [ ] `SearchClans(params SearchParams)` - поиск кланов

##### War API
- [ ] `GetCurrentWar(clanTag string)` - текущая война
- [ ] `GetCWLWar(warTag string)` - CWL война
- [ ] `GetCWLGroup(clanTag string)` - CWL группа
- [ ] `GetWarLog(clanTag string)` - лог войн

##### League API
- [ ] `GetLeagueSeasons(leagueID string)` - сезоны лиги
- [ ] `GetLeagueRanking(leagueID, seasonID string)` - рейтинг

##### Utility
- [ ] `NormalizeTag(tag string)` - нормализация тега
- [ ] `trackError(endpoint, error string)` - трекинг ошибок
- [ ] `GetErrors()` - получение ошибок
- [ ] `ClearErrors()` - очистка ошибок

##### Rate Limiting
- [ ] Rate limiter для API запросов
- [ ] Retry логика с exponential backoff
- [ ] Connection pooling

---

### 💳 Payment Service (internal/services/payment.go)

**Планируется**: ~500 строк  
**Оригинал**: `oldpy/payment_service.py` (300 строк)

#### Константы:

```go
const (
    APIURL = "https://api.yookassa.ru/v3"
)

var SubscriptionPrices = map[string]float64{
    // Premium
    "premium_1month":   49.00,
    "premium_3months":  119.00,
    "premium_6months":  199.00,
    "premium_1year":    349.00,
    // PRO PLUS
    "proplus_1month":   99.00,
    "proplus_3months":  249.00,
    "proplus_6months":  449.00,
    "proplus_1year":    799.00,
}

var SubscriptionNames = map[string]string{
    "premium_1month":   "ClashBot Премиум подписка на 1 месяц",
    "proplus_1month":   "ClashBot ПРО ПЛЮС подписка на 1 месяц",
    // ... остальные
}
```

#### Функции для реализации:

- [ ] `NewYooKassaService(shopID, secretKey, botUsername string)` - конструктор
- [ ] `CreatePayment(telegramID int64, subscriptionType string)` - создание платежа
- [ ] `ConfirmPayment(paymentID string)` - подтверждение платежа
- [ ] `GetPaymentStatus(paymentID string)` - статус платежа
- [ ] `HandleWebhook(webhookData []byte)` - обработка webhook
- [ ] `GetSubscriptionPrice(subscriptionType string)` - получение цены
- [ ] `GetSubscriptionName(subscriptionType string)` - получение названия
- [ ] `GeneratePaymentURL(paymentID, telegramID int64)` - генерация URL
- [ ] `getAuthHeaders()` - заголовки авторизации (Basic Auth)
- [ ] `generateIdempotencyKey()` - генерация ключа идемпотентности

---

### 📝 Message Generator (internal/services/message_generator.go)

**Планируется**: ~2500 строк  
**Оригинал**: `oldpy/message_generator.py` (1743 строки!) - САМЫЙ БОЛЬШОЙ КОМПОНЕНТ

#### Функции для реализации:

##### Player Messages
- [ ] `GeneratePlayerInfo(playerData map[string]interface{})` - информация об игроке
- [ ] `GeneratePlayerStats(playerData map[string]interface{})` - статистика игрока
- [ ] `GeneratePlayerTroops(playerData map[string]interface{})` - войска
- [ ] `GeneratePlayerHeroes(playerData map[string]interface{})` - герои
- [ ] `GeneratePlayerSpells(playerData map[string]interface{})` - заклинания

##### Clan Messages
- [ ] `GenerateClanInfo(clanData map[string]interface{})` - информация о клане
- [ ] `GenerateClanMembers(members []interface{}, sortBy string)` - участники
- [ ] `GenerateClanStats(clanData map[string]interface{})` - статистика клана
- [ ] `FormatMembersList(members []interface{}, page int)` - список участников с пагинацией

##### War Messages
- [ ] `GenerateCurrentWar(warData map[string]interface{})` - текущая война
- [ ] `GenerateWarDetails(warData map[string]interface{})` - детали войны
- [ ] `GenerateWarAttacks(attacks []models.AttackData)` - атаки в войне
- [ ] `GenerateWarStats(warData map[string]interface{})` - статистика войны

##### CWL Messages
- [ ] `GenerateCWLInfo(cwlData map[string]interface{})` - информация CWL
- [ ] `GenerateCWLRound(roundData map[string]interface{})` - раунд CWL
- [ ] `GenerateCWLStandings(standings []interface{})` - таблица CWL

##### Premium Messages
- [ ] `GenerateSubscriptionInfo(sub *models.Subscription)` - информация о подписке
- [ ] `GenerateSubscriptionMenu()` - меню подписок
- [ ] `GeneratePremiumFeatures()` - список Premium функций
- [ ] `GenerateProPlusFeatures()` - список PRO PLUS функций
- [ ] `GenerateBuildingUpdates(updates []models.BuildingUpgrade)` - апгрейды зданий

##### Profile Messages (PRO PLUS)
- [ ] `GenerateProfilesList(profiles []models.UserProfile)` - список профилей
- [ ] `GenerateProfileMenu(profiles []models.UserProfile)` - меню профилей
- [ ] `GenerateSwitchProfileMessage(profile *models.UserProfile)` - переключение профиля

##### Formatting
- [ ] `FormatTable(headers []string, rows [][]string)` - форматирование таблицы
- [ ] `FormatPercentage(value float64)` - форматирование процентов
- [ ] `FormatNumber(value int)` - форматирование чисел
- [ ] `GetTownHallEmoji(level int)` - эмодзи Town Hall
- [ ] `GetLeagueEmoji(league string)` - эмодзи лиги
- [ ] `GetTroopEmoji(troop string)` - эмодзи войск

---

### 🎮 Handlers (internal/handlers/)

#### message.go (~500 строк)
**Оригинал**: `oldpy/handlers.py` (MessageHandler, ~200 строк)

**Функции**:
- [ ] `NewMessageHandler(generator *MessageGenerator)` - конструктор
- [ ] `HandleMessage(update Update)` - главный обработчик
- [ ] `handlePlayerTag(chatID int64, tag string)` - обработка тега игрока
- [ ] `handleClanTag(chatID int64, tag string)` - обработка тега клана
- [ ] `handleProfileInput(chatID int64, text string)` - обработка профиля
- [ ] `validateInput(text string)` - валидация ввода

#### callback.go (~800 строк)
**Оригинал**: `oldpy/handlers.py` (CallbackHandler, ~420 строк)

**Функции**:
- [ ] `NewCallbackHandler(generator *MessageGenerator)` - конструктор
- [ ] `HandleCallback(query CallbackQuery)` - главный обработчик
- [ ] `handleMembersCallback(query CallbackQuery)` - участники клана
- [ ] `handleMembersSortCallback(query CallbackQuery, sort string)` - сортировка
- [ ] `handleWarListCallback(query CallbackQuery)` - список войн
- [ ] `handleWarInfoCallback(query CallbackQuery, warID string)` - информация о войне
- [ ] `handleCurrentWar(query CallbackQuery)` - текущая война
- [ ] `handleCWLInfo(query CallbackQuery)` - информация CWL
- [ ] `handleSubscriptionMenu(query CallbackQuery)` - меню подписок
- [ ] `handleSubscriptionType(query CallbackQuery, type string)` - тип подписки
- [ ] `handleSubscriptionPeriod(query CallbackQuery, period string)` - период
- [ ] `handleSubscriptionPayment(query CallbackQuery, data string)` - оплата
- [ ] `handleProfilesMenu(query CallbackQuery)` - меню профилей
- [ ] `handleProfileSwitch(query CallbackQuery, profileID string)` - переключение
- [ ] `handleProfileDelete(query CallbackQuery, profileID string)` - удаление
- [ ] `handleBuildingMonitor(query CallbackQuery)` - мониторинг зданий

---

### ⌨️ Keyboards (internal/keyboards/keyboards.go)

**Планируется**: ~700 строк  
**Оригинал**: `oldpy/keyboards.py` (417 строк)

#### Константы callback'ов:

```go
const (
    MembersCallback           = "members"
    MembersSortCallback       = "members_sort"
    WarListCallback           = "war_list"
    CurrentWarCallback        = "current_war"
    CWLInfoCallback           = "cwl_info"
    SubscriptionCallback      = "subscription"
    SubscriptionTypeCallback  = "sub_type"
    SubscriptionPeriodCallback = "sub_period"
    SubscriptionPayCallback   = "sub_pay"
    ProfilesCallback          = "profiles"
    ProfileSwitchCallback     = "profile_switch"
    ProfileDeleteCallback     = "profile_delete"
    BuildingMonitorCallback   = "building_monitor"
)
```

#### Функции для реализации:

##### Main Menus
- [ ] `MainMenu()` - главное меню
- [ ] `BackButton()` - кнопка назад
- [ ] `CancelButton()` - кнопка отмены

##### Clan Menus
- [ ] `ClanMenu(clanTag string)` - меню клана
- [ ] `MembersMenu(clanTag string, sortBy string, page int)` - участники с сортировкой
- [ ] `MembersSortMenu(clanTag string)` - меню сортировки

##### War Menus
- [ ] `WarMenu(clanTag string)` - меню войн
- [ ] `WarListMenu(wars []models.WarToSave, page int)` - список войн с пагинацией
- [ ] `WarDetailsMenu(warEndTime string)` - детали войны

##### Subscription Menus
- [ ] `SubscriptionMainMenu(hasSubscription bool)` - главное меню подписок
- [ ] `SubscriptionTypeMenu()` - выбор типа (Premium/PRO PLUS)
- [ ] `SubscriptionPeriodMenu(type string)` - выбор периода
- [ ] `PaymentMenu(subscriptionType, period string)` - оплата

##### Profile Menus (PRO PLUS)
- [ ] `ProfilesMenu(profiles []models.UserProfile)` - список профилей
- [ ] `ProfileActionsMenu(profileID int64)` - действия с профилем
- [ ] `AddProfileButton()` - добавить профиль

##### Building Monitor Menu
- [ ] `BuildingMonitorMenu(enabled bool)` - меню мониторинга

##### Pagination
- [ ] `PaginationButtons(currentPage, totalPages int, callbackPrefix string)` - кнопки пагинации

---

### 🤖 Bot Core (internal/bot/bot.go)

**Планируется**: ~500 строк  
**Оригинал**: `oldpy/bot.py` (341 строк)

#### Структура:

```go
type ClashBot struct {
    token            string
    api              *tgbotapi.BotAPI
    dbService        *database.DatabaseService
    cocClient        *api.CocApiClient
    paymentService   *services.YooKassaService
    messageGenerator *services.MessageGenerator
    messageHandler   *handlers.MessageHandler
    callbackHandler  *handlers.CallbackHandler
    warArchiver      *services.WarArchiver
    buildingMonitor  *services.BuildingMonitor
    clanScanner      *scanners.ClanScanner
    
    updatesChan      tgbotapi.UpdatesChannel
    shutdownChan     chan struct{}
}
```

#### Функции для реализации:

- [ ] `NewClashBot(config *config.Config)` - конструктор
- [ ] `Initialize()` - инициализация всех компонентов
- [ ] `initComponents()` - инициализация сервисов
- [ ] `registerHandlers()` - регистрация обработчиков
- [ ] `startCommand(update tgbotapi.Update)` - команда /start
- [ ] `handlePaymentSuccess(update tgbotapi.Update, args string)` - обработка успешного платежа
- [ ] `startWarArchiver()` - запуск архиватора войн
- [ ] `startBuildingMonitor()` - запуск монитора зданий
- [ ] `startClanScanner()` - запуск сканера кланов
- [ ] `Run()` - запуск бота
- [ ] `Shutdown()` - остановка бота
- [ ] `sendMessage(chatID int64, text string, keyboard interface{})` - отправка сообщения
- [ ] `editMessage(chatID int64, messageID int, text string, keyboard interface{})` - редактирование

---

### 🔄 Background Services

#### war_archiver.go (~400 строк)
**Оригинал**: `oldpy/war_archiver.py` (~200 строк)

**Функции**:
- [ ] `NewWarArchiver(db *database.DatabaseService, coc *api.CocApiClient)` - конструктор
- [ ] `Start()` - запуск фонового процесса
- [ ] `Stop()` - остановка
- [ ] `checkWars()` - проверка войн
- [ ] `archiveWar(clanTag string)` - архивация войны
- [ ] `detectViolations(war *models.WarToSave)` - обнаружение нарушений

#### building_monitor.go (~500 строк)
**Оригинал**: `oldpy/building_monitor.py` (254 строк)

**Функции**:
- [ ] `NewBuildingMonitor(db *database.DatabaseService, coc *api.CocApiClient, bot BotInterface)` - конструктор
- [ ] `Start()` - запуск мониторинга
- [ ] `Stop()` - остановка
- [ ] `checkBuildings()` - проверка зданий
- [ ] `detectChanges(playerTag string)` - обнаружение изменений
- [ ] `sendNotification(telegramID int64, upgrade *models.BuildingUpgrade)` - отправка уведомления

---

### 🔍 Scanners

#### clan_scanner.go (~300 строк)
**Оригинал**: `oldpy/scanners/clan_scanner.py`

**Функции**:
- [ ] `NewClanScanner(db *database.DatabaseService, coc *api.CocApiClient)` - конструктор
- [ ] `Start()` - запуск сканирования
- [ ] `Stop()` - остановка
- [ ] `scanClan(clanTag string)` - сканирование клана
- [ ] `compareMembers(old, new []Member)` - сравнение участников

#### war_importer.go (~400 строк)
**Оригинал**: `oldpy/scanners/war_importer.py`

**Функции**:
- [ ] `NewWarImporter(db *database.DatabaseService, coc *api.CocApiClient)` - конструктор
- [ ] `ImportWars(clanTag string, count int)` - импорт войн
- [ ] `validateWarData(war *models.WarToSave)` - валидация
- [ ] `batchSave(wars []models.WarToSave)` - batch сохранение

---

### 🛠️ Utilities

#### validate.go (~150 строк)
**Оригинал**: `oldpy/validate.py` (71 строк)

**Функции**:
- [ ] `ValidatePlayerTag(tag string)` - валидация тега игрока
- [ ] `ValidateClanTag(tag string)` - валидация тега клана
- [ ] `NormalizeTag(tag string)` - нормализация тега
- [ ] `IsValidTag(tag string)` - общая валидация

#### translations.go (~300 строк)
**Оригинал**: `oldpy/translations.py` (139 строк)

**Функции**:
- [ ] `GetTranslation(key string, lang string)` - получение перевода
- [ ] `FormatDuration(seconds int)` - форматирование длительности
- [ ] `FormatDate(date time.Time)` - форматирование даты
- [ ] `TranslateTroopName(name string)` - перевод названий войск
- [ ] `TranslateSpellName(name string)` - перевод названий заклинаний

#### policy.go (~100 строк)
**Оригинал**: `oldpy/policy.py` (47 строк)

**Функции**:
- [ ] `GetPolicyURL(botUsername string)` - получение URL политики
- [ ] `GetPolicyText()` - текст политики
- [ ] `GeneratePolicyMessage()` - сообщение с политикой

---

## 📦 ЗАВИСИМОСТИ GO

### Основные библиотеки:

```go
require (
    github.com/go-telegram-bot-api/telegram-bot-api/v5 v5.5.1
    github.com/mattn/go-sqlite3 v1.14.18
    github.com/go-resty/resty/v2 v2.10.0
    github.com/google/uuid v1.4.0
    github.com/sirupsen/logrus v1.9.3
    golang.org/x/time v0.5.0
)
```

### Команды установки:

```bash
go get github.com/go-telegram-bot-api/telegram-bot-api/v5
go get github.com/mattn/go-sqlite3
go get github.com/go-resty/resty/v2
go get github.com/google/uuid
go get github.com/sirupsen/logrus
go get golang.org/x/time/rate
go mod tidy
```

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

### Строки кода:

| Компонент | Python | Go (план) | Отношение |
|-----------|--------|-----------|-----------|
| Models | 199 | 260 | 1.31x |
| Config | 78 | 160 | 2.05x |
| Database | 646 | 1000 | 1.55x |
| COC API | 700 | 800 | 1.14x |
| Payment | 300 | 500 | 1.67x |
| Message Gen | 1743 | 2500 | 1.43x |
| Handlers | 620 | 1200 | 1.94x |
| Keyboards | 417 | 700 | 1.68x |
| Bot | 341 | 500 | 1.47x |
| Services | 454 | 900 | 1.98x |
| Scanners | 200 | 700 | 3.50x |
| Utils | 257 | 450 | 1.75x |
| **ВСЕГО** | **5955** | **9470** | **1.59x** |

### Объяснение увеличения кода:

1. **Explicit error handling** - Go требует явной обработки ошибок
2. **Type definitions** - статическая типизация требует больше определений
3. **Interface definitions** - для тестируемости и гибкости
4. **Documentation comments** - Go convention для godoc
5. **Более подробное логирование** - лучшая отладка

---

## 🎯 ВРЕМЕННЫЕ РАМКИ

### Оптимистичный сценарий (full-time работа):
- **Фаза 1**: ✅ Завершена (1 неделя)
- **Фаза 2**: Database + API (2 недели)
- **Фаза 3**: Services + Handlers (3 недели)
- **Фаза 4**: Background + Scanners (1 неделя)
- **Фаза 5**: Integration + Testing (2 недели)
- **Фаза 6**: Deploy + Monitoring (1 неделя)
- **ИТОГО**: ~10 недель

### Реалистичный сценарий (part-time):
- **ИТОГО**: 16-20 недель

---

## ✅ КРИТЕРИИ ГОТОВНОСТИ

### Функциональность:
- [ ] Все команды работают
- [ ] Все callback'и работают
- [ ] Платежи работают
- [ ] Премиум функции работают
- [ ] Мониторинг работает
- [ ] Архивация работает

### Качество:
- [ ] Unit тесты > 80%
- [ ] Integration тесты
- [ ] Performance тесты
- [ ] Memory leak тесты
- [ ] Concurrency тесты

### Документация:
- [ ] API документация (godoc)
- [ ] Deployment гайд
- [ ] Troubleshooting гайд
- [ ] Contribution гайд

---

**Дата создания**: 2024  
**Версия**: 1.0  
**Статус**: Фаза 1 завершена ✅

🎯 **Цель**: 100% функциональный перенос с улучшением производительности
