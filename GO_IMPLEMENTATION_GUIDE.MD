# 🛠️ ClashBot Go: Практическое руководство по реализации

## 📋 Пошаговое руководство с примерами кода

### 🚀 Этап 1: Настройка проекта

#### 1.1 Инициализация Go модуля
```bash
mkdir clashbot-go
cd clashbot-go
go mod init github.com/SpencerMSU/clashbot-go
```

#### 1.2 Структура проекта
```
clashbot-go/
├── cmd/
│   └── bot/
│       └── main.go                 # Точка входа
├── internal/
│   ├── config/
│   │   └── config.go              # Конфигурация
│   ├── models/
│   │   ├── user.go                # Модель пользователя
│   │   ├── clan.go                # Модель клана
│   │   ├── war.go                 # Модель войны
│   │   ├── subscription.go        # Модель подписки
│   │   └── building.go            # Модель зданий
│   ├── database/
│   │   ├── database.go            # Сервис БД
│   │   ├── migrations.go          # Миграции
│   │   └── repository/
│   │       ├── user.go            # Репозиторий пользователей
│   │       ├── clan.go            # Репозиторий кланов
│   │       └── war.go             # Репозиторий войн
│   ├── services/
│   │   ├── coc_api.go             # COC API клиент
│   │   ├── telegram.go            # Телеграм сервис
│   │   ├── payment.go             # Платежный сервис
│   │   ├── war_archiver.go        # Архиватор войн
│   │   └── building_monitor.go    # Монитор зданий
│   ├── handlers/
│   │   ├── message.go             # Обработчик сообщений
│   │   ├── callback.go            # Обработчик callback'ов
│   │   └── commands.go            # Обработчик команд
│   ├── keyboards/
│   │   └── keyboards.go           # Генерация клавиатур
│   ├── bot/
│   │   └── bot.go                 # Основной класс бота
│   └── utils/
│       ├── translations.go        # Система переводов
│       ├── validators.go          # Валидаторы
│       └── formatting.go         # Форматирование
├── pkg/
│   └── logger/
│       └── logger.go              # Логгер
├── configs/
│   ├── config.yaml               # Конфигурация
│   └── config.example.yaml       # Пример конфигурации
├── migrations/
│   ├── 001_initial.sql           # Начальная миграция
│   └── 002_premium_features.sql  # Премиум функции
├── docs/
│   └── api.md                    # API документация
├── tests/
│   ├── integration/              # Интеграционные тесты
│   └── unit/                     # Юнит тесты
├── go.mod
├── go.sum
├── Makefile
├── Dockerfile
└── docker-compose.yml
```

#### 1.3 Основные зависимости (go.mod)
```go
module github.com/SpencerMSU/clashbot-go

go 1.21

require (
    github.com/go-telegram-bot-api/telegram-bot-api/v5 v5.5.1
    gorm.io/gorm v1.25.5
    gorm.io/driver/sqlite v1.5.4
    gorm.io/driver/postgres v1.5.4
    github.com/go-resty/resty/v2 v2.10.0
    github.com/spf13/viper v1.17.0
    github.com/sirupsen/logrus v1.9.3
    github.com/google/uuid v1.4.0
    golang.org/x/time v0.5.0
    github.com/stretchr/testify v1.8.4
)
```

#### 1.4 Makefile
```makefile
.PHONY: build run test clean lint

# Переменные
BINARY_NAME=clashbot-go
CMD_PATH=./cmd/bot

# Сборка
build:
	go build -o bin/$(BINARY_NAME) $(CMD_PATH)

# Запуск
run:
	go run $(CMD_PATH)/main.go

# Тестирование
test:
	go test -v ./...

test-coverage:
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out

# Линтинг
lint:
	golangci-lint run

# Очистка
clean:
	rm -rf bin/
	rm -f coverage.out

# Установка зависимостей
deps:
	go mod download
	go mod tidy

# Запуск в Docker
docker-build:
	docker build -t clashbot-go .

docker-run:
	docker-compose up -d

# Миграции
migrate-up:
	go run cmd/migrate/main.go up

migrate-down:
	go run cmd/migrate/main.go down
```

---

### 🔧 Этап 2: Базовые компоненты

#### 2.1 Конфигурация (internal/config/config.go)
```go
package config

import (
    "fmt"
    "os"
    "strings"
    
    "github.com/spf13/viper"
)

type Config struct {
    // Telegram Bot
    BotToken    string `mapstructure:"BOT_TOKEN"`
    BotUsername string `mapstructure:"BOT_USERNAME"`
    
    // Clash of Clans API
    COCAPIToken  string `mapstructure:"COC_API_TOKEN"`
    COCAPIBaseURL string `mapstructure:"COC_API_BASE_URL"`
    
    // Database
    DatabaseURL  string `mapstructure:"DATABASE_URL"`
    DatabasePath string `mapstructure:"DATABASE_PATH"`
    
    // YooKassa
    YooKassaShopID    string `mapstructure:"YOOKASSA_SHOP_ID"`
    YooKassaSecretKey string `mapstructure:"YOOKASSA_SECRET_KEY"`
    
    // Intervals
    ArchiveCheckInterval    int `mapstructure:"ARCHIVE_CHECK_INTERVAL"`
    DonationSnapshotInterval int `mapstructure:"DONATION_SNAPSHOT_INTERVAL"`
    
    // Server
    ServerPort string `mapstructure:"SERVER_PORT"`
    LogLevel   string `mapstructure:"LOG_LEVEL"`
}

var cfg *Config

func Load() (*Config, error) {
    viper.SetConfigName("config")
    viper.SetConfigType("yaml")
    viper.AddConfigPath("./configs/")
    
    // Читаем из переменных окружения
    viper.AutomaticEnv()
    
    // Читаем из файла api_tokens.txt (совместимость с Python версией)
    if err := readAPITokensFile(); err != nil {
        return nil, fmt.Errorf("failed to read api tokens: %w", err)
    }
    
    // Читаем конфиг файл
    if err := viper.ReadInConfig(); err != nil {
        if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
            return nil, fmt.Errorf("failed to read config: %w", err)
        }
    }
    
    cfg = &Config{}
    if err := viper.Unmarshal(cfg); err != nil {
        return nil, fmt.Errorf("failed to unmarshal config: %w", err)
    }
    
    // Устанавливаем значения по умолчанию
    setDefaults(cfg)
    
    // Валидация
    if err := validateConfig(cfg); err != nil {
        return nil, fmt.Errorf("config validation failed: %w", err)
    }
    
    return cfg, nil
}

func readAPITokensFile() error {
    file, err := os.Open("api_tokens.txt")
    if err != nil {
        return nil // Файл не обязателен
    }
    defer file.Close()
    
    content, err := os.ReadFile("api_tokens.txt")
    if err != nil {
        return err
    }
    
    lines := strings.Split(string(content), "\n")
    for _, line := range lines {
        line = strings.TrimSpace(line)
        if line == "" || strings.HasPrefix(line, "#") {
            continue
        }
        
        parts := strings.SplitN(line, "=", 2)
        if len(parts) == 2 {
            key := strings.TrimSpace(parts[0])
            value := strings.TrimSpace(parts[1])
            viper.Set(key, value)
        }
    }
    
    return nil
}

func setDefaults(cfg *Config) {
    if cfg.COCAPIBaseURL == "" {
        cfg.COCAPIBaseURL = "https://api.clashofclans.com/v1"
    }
    if cfg.DatabasePath == "" {
        cfg.DatabasePath = "clashbot.db"
    }
    if cfg.ArchiveCheckInterval == 0 {
        cfg.ArchiveCheckInterval = 900 // 15 минут
    }
    if cfg.DonationSnapshotInterval == 0 {
        cfg.DonationSnapshotInterval = 21600 // 6 часов
    }
    if cfg.ServerPort == "" {
        cfg.ServerPort = "8080"
    }
    if cfg.LogLevel == "" {
        cfg.LogLevel = "info"
    }
}

func validateConfig(cfg *Config) error {
    if cfg.BotToken == "" {
        return fmt.Errorf("BOT_TOKEN is required")
    }
    if cfg.COCAPIToken == "" {
        return fmt.Errorf("COC_API_TOKEN is required")
    }
    return nil
}

func Get() *Config {
    if cfg == nil {
        panic("config not loaded")
    }
    return cfg
}
```

#### 2.2 Логгер (pkg/logger/logger.go)
```go
package logger

import (
    "os"
    
    "github.com/sirupsen/logrus"
)

var log *logrus.Logger

func Init(level string) *logrus.Logger {
    log = logrus.New()
    
    // Настройка уровня логирования
    logLevel, err := logrus.ParseLevel(level)
    if err != nil {
        logLevel = logrus.InfoLevel
    }
    log.SetLevel(logLevel)
    
    // Настройка формата
    log.SetFormatter(&logrus.TextFormatter{
        FullTimestamp: true,
        ForceColors:   true,
    })
    
    // Настройка вывода
    log.SetOutput(os.Stdout)
    
    return log
}

func Get() *logrus.Logger {
    if log == nil {
        return Init("info")
    }
    return log
}

// Convenience methods
func Info(args ...interface{}) {
    Get().Info(args...)
}

func Infof(format string, args ...interface{}) {
    Get().Infof(format, args...)
}

func Warn(args ...interface{}) {
    Get().Warn(args...)
}

func Warnf(format string, args ...interface{}) {
    Get().Warnf(format, args...)
}

func Error(args ...interface{}) {
    Get().Error(args...)
}

func Errorf(format string, args ...interface{}) {
    Get().Errorf(format, args...)
}

func Fatal(args ...interface{}) {
    Get().Fatal(args...)
}

func Fatalf(format string, args ...interface{}) {
    Get().Fatalf(format, args...)
}
```

---

### 🗄️ Этап 3: Модели данных

#### 3.1 Модель пользователя (internal/models/user.go)
```go
package models

import (
    "time"
    
    "gorm.io/gorm"
)

type User struct {
    TelegramID int64  `gorm:"primaryKey" json:"telegram_id"`
    PlayerTag  string `gorm:"not null;uniqueIndex" json:"player_tag"`
    CreatedAt  time.Time `json:"created_at"`
    UpdatedAt  time.Time `json:"updated_at"`
    
    // Связи
    Profiles      []UserProfile      `gorm:"foreignKey:TelegramID" json:"profiles"`
    Subscription  *Subscription      `gorm:"foreignKey:TelegramID" json:"subscription"`
    Notifications *NotificationSettings `gorm:"foreignKey:TelegramID" json:"notifications"`
    BuildingTrackers []BuildingTracker `gorm:"foreignKey:TelegramID" json:"building_trackers"`
}

type UserProfile struct {
    ID         uint   `gorm:"primaryKey" json:"id"`
    TelegramID int64  `gorm:"not null;index" json:"telegram_id"`
    PlayerTag  string `gorm:"not null" json:"player_tag"`
    ProfileName *string `json:"profile_name"`
    IsPrimary  bool   `gorm:"default:false" json:"is_primary"`
    CreatedAt  time.Time `json:"created_at"`
    
    // Связи
    User User `gorm:"foreignKey:TelegramID" json:"user"`
}

type NotificationSettings struct {
    TelegramID   int64 `gorm:"primaryKey" json:"telegram_id"`
    Enabled      bool  `gorm:"default:true" json:"enabled"`
    WarStart     bool  `gorm:"default:true" json:"war_start"`
    WarEnd       bool  `gorm:"default:true" json:"war_end"`
    AttackReminder bool `gorm:"default:true" json:"attack_reminder"`
    BuildingComplete bool `gorm:"default:false" json:"building_complete"` // Премиум
    CustomTime   *string `json:"custom_time"` // Премиум
    CreatedAt    time.Time `json:"created_at"`
    UpdatedAt    time.Time `json:"updated_at"`
    
    // Связи
    User User `gorm:"foreignKey:TelegramID" json:"user"`
}

// Валидация тега игрока
func (u *User) ValidatePlayerTag() error {
    if len(u.PlayerTag) < 8 || len(u.PlayerTag) > 12 {
        return fmt.Errorf("invalid player tag length")
    }
    if !strings.HasPrefix(u.PlayerTag, "#") {
        u.PlayerTag = "#" + u.PlayerTag
    }
    return nil
}

// Проверка на премиум пользователя
func (u *User) IsPremium() bool {
    return u.Subscription != nil && u.Subscription.IsActive()
}

// Получение основного профиля
func (u *User) GetPrimaryProfile() *UserProfile {
    for _, profile := range u.Profiles {
        if profile.IsPrimary {
            return &profile
        }
    }
    return nil
}
```

#### 3.2 Модель войн (internal/models/war.go)
```go
package models

import (
    "time"
    
    "gorm.io/gorm"
)

type War struct {
    ID                uint      `gorm:"primaryKey" json:"id"`
    ClanTag          string    `gorm:"not null;index" json:"clan_tag"`
    OpponentTag      string    `gorm:"not null" json:"opponent_tag"`
    StartTime        time.Time `gorm:"not null" json:"start_time"`
    EndTime          time.Time `gorm:"not null;uniqueIndex" json:"end_time"`
    PreparationStartTime time.Time `gorm:"not null" json:"preparation_start_time"`
    TeamSize         int       `gorm:"not null" json:"team_size"`
    State            string    `gorm:"not null" json:"state"`
    Result           *string   `json:"result"`
    ClanStars        *int      `json:"clan_stars"`
    OpponentStars    *int      `json:"opponent_stars"`
    ClanDestruction  *float64  `json:"clan_destruction"`
    OpponentDestruction *float64 `json:"opponent_destruction"`
    WarData          string    `gorm:"type:text" json:"war_data"` // JSON данные войны
    CreatedAt        time.Time `json:"created_at"`
    UpdatedAt        time.Time `json:"updated_at"`
    
    // Связи
    Attacks []Attack `gorm:"foreignKey:WarID" json:"attacks"`
}

type Attack struct {
    ID                uint      `gorm:"primaryKey" json:"id"`
    WarID            uint      `gorm:"not null;index" json:"war_id"`
    AttackerTag      string    `gorm:"not null" json:"attacker_tag"`
    DefenderTag      string    `gorm:"not null" json:"defender_tag"`
    Stars            int       `gorm:"not null" json:"stars"`
    DestructionPercentage float64 `gorm:"not null" json:"destruction_percentage"`
    Order            int       `gorm:"not null" json:"order"`
    Duration         int       `json:"duration"`
    AttackOrder      int       `json:"attack_order"`
    CreatedAt        time.Time `json:"created_at"`
    
    // Связи
    War War `gorm:"foreignKey:WarID" json:"war"`
}

type CWLSeason struct {
    ID            uint      `gorm:"primaryKey" json:"id"`
    ClanTag      string    `gorm:"not null;index" json:"clan_tag"`
    Season       string    `gorm:"not null" json:"season"`
    State        string    `gorm:"not null" json:"state"`
    CWLData      string    `gorm:"type:text" json:"cwl_data"` // JSON данные CWL
    CreatedAt    time.Time `json:"created_at"`
    UpdatedAt    time.Time `json:"updated_at"`
}

// Методы для War
func (w *War) IsEnded() bool {
    return w.State == "warEnded"
}

func (w *War) IsInPreparation() bool {
    return w.State == "preparation"
}

func (w *War) IsInWar() bool {
    return w.State == "inWar"
}

func (w *War) GetWinner() string {
    if w.Result == nil {
        return "unknown"
    }
    return *w.Result
}
```

#### 3.3 Модель подписок (internal/models/subscription.go)
```go
package models

import (
    "time"
    
    "gorm.io/gorm"
)

type Subscription struct {
    ID          uint      `gorm:"primaryKey" json:"id"`
    TelegramID  int64     `gorm:"not null;uniqueIndex" json:"telegram_id"`
    Type        string    `gorm:"not null" json:"type"` // premium, proplus
    StartDate   time.Time `gorm:"not null" json:"start_date"`
    EndDate     time.Time `gorm:"not null" json:"end_date"`
    PaymentID   *string   `json:"payment_id"`
    Amount      float64   `json:"amount"`
    Currency    string    `gorm:"default:RUB" json:"currency"`
    Status      string    `gorm:"default:active" json:"status"` // active, cancelled, expired
    AutoRenew   bool      `gorm:"default:false" json:"auto_renew"`
    CreatedAt   time.Time `json:"created_at"`
    UpdatedAt   time.Time `json:"updated_at"`
    
    // Связи
    User User `gorm:"foreignKey:TelegramID" json:"user"`
}

// Проверка активности подписки
func (s *Subscription) IsActive() bool {
    if s.Status != "active" {
        return false
    }
    return time.Now().Before(s.EndDate)
}

// Проверка истечения подписки
func (s *Subscription) IsExpired() bool {
    return time.Now().After(s.EndDate)
}

// Дни до истечения
func (s *Subscription) DaysUntilExpiry() int {
    if s.IsExpired() {
        return 0
    }
    duration := s.EndDate.Sub(time.Now())
    return int(duration.Hours() / 24)
}

// Получение лимитов в зависимости от типа подписки
func (s *Subscription) GetProfileLimit() int {
    switch s.Type {
    case "premium":
        return 3
    case "proplus":
        return 5
    default:
        return 1
    }
}

func (s *Subscription) GetLinkedClanLimit() int {
    switch s.Type {
    case "premium":
        return 3
    case "proplus":
        return 10
    default:
        return 1
    }
}

func (s *Subscription) HasBuildingTracking() bool {
    return s.Type == "premium" || s.Type == "proplus"
}

func (s *Subscription) HasAdvancedNotifications() bool {
    return s.Type == "premium" || s.Type == "proplus"
}
```

---

### 🌐 Этап 4: API интеграции

#### 4.1 Clash of Clans API клиент (internal/services/coc_api.go)
```go
package services

import (
    "context"
    "encoding/json"
    "fmt"
    "net/http"
    "strings"
    "time"
    
    "github.com/go-resty/resty/v2"
    "golang.org/x/time/rate"
    
    "github.com/SpencerMSU/clashbot-go/internal/config"
    "github.com/SpencerMSU/clashbot-go/pkg/logger"
)

type COCAPIClient struct {
    client     *resty.Client
    baseURL    string
    apiToken   string
    rateLimiter *rate.Limiter
}

type Player struct {
    Tag                string `json:"tag"`
    Name               string `json:"name"`
    TownHallLevel     int    `json:"townHallLevel"`
    ExpLevel          int    `json:"expLevel"`
    Trophies          int    `json:"trophies"`
    BestTrophies      int    `json:"bestTrophies"`
    WarStars          int    `json:"warStars"`
    AttackWins        int    `json:"attackWins"`
    DefenseWins       int    `json:"defenseWins"`
    BuilderHallLevel  int    `json:"builderHallLevel"`
    Clan              *Clan  `json:"clan,omitempty"`
    Achievements      []Achievement `json:"achievements"`
    Troops            []Troop `json:"troops"`
    Heroes            []Hero  `json:"heroes"`
    Spells            []Spell `json:"spells"`
}

type Clan struct {
    Tag           string `json:"tag"`
    Name          string `json:"name"`
    Type          string `json:"type"`
    Description   string `json:"description"`
    Location      *Location `json:"location,omitempty"`
    BadgeUrls     BadgeUrls `json:"badgeUrls"`
    ClanLevel     int    `json:"clanLevel"`
    ClanPoints    int    `json:"clanPoints"`
    ClanVersusPoints int `json:"clanVersusPoints"`
    RequiredTrophies int `json:"requiredTrophies"`
    WarFrequency  string `json:"warFrequency"`
    WarWinStreak  int    `json:"warWinStreak"`
    WarWins       int    `json:"warWins"`
    WarTies       int    `json:"warTies"`
    WarLosses     int    `json:"warLosses"`
    IsWarLogPublic bool  `json:"isWarLogPublic"`
    Members       int    `json:"members"`
    MemberList    []ClanMember `json:"memberList,omitempty"`
}

type ClanMember struct {
    Tag                string `json:"tag"`
    Name               string `json:"name"`
    Role               string `json:"role"`
    ExpLevel           int    `json:"expLevel"`
    League             *League `json:"league,omitempty"`
    Trophies           int    `json:"trophies"`
    ClanRank           int    `json:"clanRank"`
    PreviousClanRank   int    `json:"previousClanRank"`
    Donations          int    `json:"donations"`
    DonationsReceived  int    `json:"donationsReceived"`
}

type WarLog struct {
    Items []WarLogEntry `json:"items"`
    Paging Paging       `json:"paging,omitempty"`
}

type WarLogEntry struct {
    Result           string    `json:"result"`
    EndTime          string    `json:"endTime"`
    TeamSize         int       `json:"teamSize"`
    Clan             WarClan   `json:"clan"`
    Opponent         WarClan   `json:"opponent"`
}

type CurrentWar struct {
    State                string    `json:"state"`
    TeamSize             int       `json:"teamSize"`
    PreparationStartTime string    `json:"preparationStartTime"`
    StartTime            string    `json:"startTime"`
    EndTime              string    `json:"endTime"`
    Clan                 WarClan   `json:"clan"`
    Opponent             WarClan   `json:"opponent"`
}

type WarClan struct {
    Tag            string      `json:"tag"`
    Name           string      `json:"name"`
    BadgeUrls      BadgeUrls   `json:"badgeUrls"`
    ClanLevel      int         `json:"clanLevel"`
    Attacks        int         `json:"attacks"`
    Stars          int         `json:"stars"`
    DestructionPercentage float64 `json:"destructionPercentage"`
    Members        []WarMember `json:"members"`
}

type WarMember struct {
    Tag                string   `json:"tag"`
    Name               string   `json:"name"`
    MapPosition        int      `json:"mapPosition"`
    TownhallLevel      int      `json:"townhallLevel"`
    OpponentAttacks    int      `json:"opponentAttacks"`
    BestOpponentAttack *Attack  `json:"bestOpponentAttack,omitempty"`
    Attacks            []Attack `json:"attacks,omitempty"`
}

type Attack struct {
    Order                int     `json:"order"`
    AttackerTag          string  `json:"attackerTag"`
    DefenderTag          string  `json:"defenderTag"`
    Stars                int     `json:"stars"`
    DestructionPercentage float64 `json:"destructionPercentage"`
    Duration             int     `json:"duration"`
}

// Дополнительные структуры
type Achievement struct {
    Name           string `json:"name"`
    Stars          int    `json:"stars"`
    Value          int    `json:"value"`
    Target         int    `json:"target"`
    Info           string `json:"info"`
    CompletionInfo string `json:"completionInfo"`
    Village        string `json:"village"`
}

type Troop struct {
    Name     string `json:"name"`
    Level    int    `json:"level"`
    MaxLevel int    `json:"maxLevel"`
    Village  string `json:"village"`
}

type Hero struct {
    Name     string `json:"name"`
    Level    int    `json:"level"`
    MaxLevel int    `json:"maxLevel"`
    Village  string `json:"village"`
}

type Spell struct {
    Name     string `json:"name"`
    Level    int    `json:"level"`
    MaxLevel int    `json:"maxLevel"`
    Village  string `json:"village"`
}

type Location struct {
    ID          int    `json:"id"`
    Name        string `json:"name"`
    IsCountry   bool   `json:"isCountry"`
    CountryCode string `json:"countryCode"`
}

type League struct {
    ID   int       `json:"id"`
    Name string    `json:"name"`
    IconUrls IconUrls `json:"iconUrls"`
}

type BadgeUrls struct {
    Small  string `json:"small"`
    Large  string `json:"large"`
    Medium string `json:"medium"`
}

type IconUrls struct {
    Small string `json:"small"`
    Tiny  string `json:"tiny"`
}

type Paging struct {
    Cursors Cursors `json:"cursors"`
}

type Cursors struct {
    After  string `json:"after,omitempty"`
    Before string `json:"before,omitempty"`
}

func NewCOCAPIClient(cfg *config.Config) *COCAPIClient {
    client := resty.New()
    client.SetBaseURL(cfg.COCAPIBaseURL)
    client.SetHeader("Authorization", "Bearer "+cfg.COCAPIToken)
    client.SetHeader("Content-Type", "application/json")
    client.SetTimeout(30 * time.Second)
    
    // Rate limiter: 30 запросов в секунду (лимит Supercell)
    rateLimiter := rate.NewLimiter(rate.Limit(30), 1)
    
    return &COCAPIClient{
        client:      client,
        baseURL:     cfg.COCAPIBaseURL,
        apiToken:    cfg.COCAPIToken,
        rateLimiter: rateLimiter,
    }
}

// Получение игрока
func (c *COCAPIClient) GetPlayer(ctx context.Context, playerTag string) (*Player, error) {
    if err := c.rateLimiter.Wait(ctx); err != nil {
        return nil, fmt.Errorf("rate limiter error: %w", err)
    }
    
    playerTag = FormatPlayerTag(playerTag)
    encodedTag := strings.ReplaceAll(playerTag, "#", "%23")
    
    var player Player
    resp, err := c.client.R().
        SetContext(ctx).
        SetResult(&player).
        Get(fmt.Sprintf("/players/%s", encodedTag))
    
    if err != nil {
        return nil, fmt.Errorf("failed to get player: %w", err)
    }
    
    if resp.StatusCode() != http.StatusOK {
        return nil, fmt.Errorf("API error: %d - %s", resp.StatusCode(), resp.String())
    }
    
    return &player, nil
}

// Получение клана
func (c *COCAPIClient) GetClan(ctx context.Context, clanTag string) (*Clan, error) {
    if err := c.rateLimiter.Wait(ctx); err != nil {
        return nil, fmt.Errorf("rate limiter error: %w", err)
    }
    
    clanTag = FormatClanTag(clanTag)
    encodedTag := strings.ReplaceAll(clanTag, "#", "%23")
    
    var clan Clan
    resp, err := c.client.R().
        SetContext(ctx).
        SetResult(&clan).
        Get(fmt.Sprintf("/clans/%s", encodedTag))
    
    if err != nil {
        return nil, fmt.Errorf("failed to get clan: %w", err)
    }
    
    if resp.StatusCode() != http.StatusOK {
        return nil, fmt.Errorf("API error: %d - %s", resp.StatusCode(), resp.String())
    }
    
    return &clan, nil
}

// Получение участников клана
func (c *COCAPIClient) GetClanMembers(ctx context.Context, clanTag string) ([]ClanMember, error) {
    clan, err := c.GetClan(ctx, clanTag)
    if err != nil {
        return nil, err
    }
    
    return clan.MemberList, nil
}

// Получение текущей войны клана
func (c *COCAPIClient) GetClanCurrentWar(ctx context.Context, clanTag string) (*CurrentWar, error) {
    if err := c.rateLimiter.Wait(ctx); err != nil {
        return nil, fmt.Errorf("rate limiter error: %w", err)
    }
    
    clanTag = FormatClanTag(clanTag)
    encodedTag := strings.ReplaceAll(clanTag, "#", "%23")
    
    var war CurrentWar
    resp, err := c.client.R().
        SetContext(ctx).
        SetResult(&war).
        Get(fmt.Sprintf("/clans/%s/currentwar", encodedTag))
    
    if err != nil {
        return nil, fmt.Errorf("failed to get current war: %w", err)
    }
    
    if resp.StatusCode() != http.StatusOK {
        return nil, fmt.Errorf("API error: %d - %s", resp.StatusCode(), resp.String())
    }
    
    return &war, nil
}

// Получение лога войн клана
func (c *COCAPIClient) GetClanWarLog(ctx context.Context, clanTag string, limit int) (*WarLog, error) {
    if err := c.rateLimiter.Wait(ctx); err != nil {
        return nil, fmt.Errorf("rate limiter error: %w", err)
    }
    
    clanTag = FormatClanTag(clanTag)
    encodedTag := strings.ReplaceAll(clanTag, "#", "%23")
    
    var warLog WarLog
    resp, err := c.client.R().
        SetContext(ctx).
        SetQueryParam("limit", fmt.Sprintf("%d", limit)).
        SetResult(&warLog).
        Get(fmt.Sprintf("/clans/%s/warlog", encodedTag))
    
    if err != nil {
        return nil, fmt.Errorf("failed to get war log: %w", err)
    }
    
    if resp.StatusCode() != http.StatusOK {
        return nil, fmt.Errorf("API error: %d - %s", resp.StatusCode(), resp.String())
    }
    
    return &warLog, nil
}

// Валидация и форматирование тегов
func ValidatePlayerTag(tag string) error {
    if len(tag) < 8 || len(tag) > 12 {
        return fmt.Errorf("player tag must be 8-12 characters long")
    }
    
    tag = strings.ToUpper(strings.TrimPrefix(tag, "#"))
    
    // Проверяем, что тег содержит только допустимые символы
    for _, char := range tag {
        if !((char >= '0' && char <= '9') || 
             (char >= 'A' && char <= 'Z') || 
             char == 'O' || char == 'I') {
            return fmt.Errorf("invalid characters in player tag")
        }
    }
    
    return nil
}

func ValidateClanTag(tag string) error {
    if len(tag) < 8 || len(tag) > 12 {
        return fmt.Errorf("clan tag must be 8-12 characters long")
    }
    
    tag = strings.ToUpper(strings.TrimPrefix(tag, "#"))
    
    // Проверяем, что тег содержит только допустимые символы
    for _, char := range tag {
        if !((char >= '0' && char <= '9') || 
             (char >= 'A' && char <= 'Z') || 
             char == 'O' || char == 'I') {
            return fmt.Errorf("invalid characters in clan tag")
        }
    }
    
    return nil
}

func FormatPlayerTag(tag string) string {
    if !strings.HasPrefix(tag, "#") {
        tag = "#" + tag
    }
    return strings.ToUpper(tag)
}

func FormatClanTag(tag string) string {
    if !strings.HasPrefix(tag, "#") {
        tag = "#" + tag
    }
    return strings.ToUpper(tag)
}

func IsPlayerTag(tag string) bool {
    return ValidatePlayerTag(tag) == nil
}

func IsClanTag(tag string) bool {
    return ValidateClanTag(tag) == nil
}

// Проверка состояния войны
func IsWarEnded(state string) bool {
    return state == "warEnded"
}

func IsWarInPreparation(state string) bool {
    return state == "preparation"
}

func IsWarInProgress(state string) bool {
    return state == "inWar"
}
```

---

### 🤖 Этап 5: Основной бот

#### 5.1 Основной класс бота (internal/bot/bot.go)
```go
package bot

import (
    "context"
    "fmt"
    "os"
    "os/signal"
    "sync"
    "syscall"
    "time"
    
    tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
    "gorm.io/gorm"
    
    "github.com/SpencerMSU/clashbot-go/internal/config"
    "github.com/SpencerMSU/clashbot-go/internal/database"
    "github.com/SpencerMSU/clashbot-go/internal/handlers"
    "github.com/SpencerMSU/clashbot-go/internal/services"
    "github.com/SpencerMSU/clashbot-go/pkg/logger"
)

type Bot struct {
    api          *tgbotapi.BotAPI
    config       *config.Config
    db           *gorm.DB
    cocAPI       *services.COCAPIClient
    paymentService *services.PaymentService
    warArchiver  *services.WarArchiver
    buildingMonitor *services.BuildingMonitor
    
    messageHandler  *handlers.MessageHandler
    callbackHandler *handlers.CallbackHandler
    
    ctx    context.Context
    cancel context.CancelFunc
    wg     sync.WaitGroup
}

func New(cfg *config.Config) (*Bot, error) {
    // Создаем Telegram bot API
    api, err := tgbotapi.NewBotAPI(cfg.BotToken)
    if err != nil {
        return nil, fmt.Errorf("failed to create bot API: %w", err)
    }
    
    logger.Infof("Авторизован как %s", api.Self.UserName)
    
    // Подключаемся к базе данных
    db, err := database.Connect(cfg)
    if err != nil {
        return nil, fmt.Errorf("failed to connect to database: %w", err)
    }
    
    // Создаем сервисы
    cocAPI := services.NewCOCAPIClient(cfg)
    paymentService := services.NewPaymentService(cfg)
    
    ctx, cancel := context.WithCancel(context.Background())
    
    bot := &Bot{
        api:            api,
        config:         cfg,
        db:             db,
        cocAPI:         cocAPI,
        paymentService: paymentService,
        ctx:            ctx,
        cancel:         cancel,
    }
    
    // Создаем обработчики
    bot.messageHandler = handlers.NewMessageHandler(bot.db, bot.cocAPI, bot.paymentService)
    bot.callbackHandler = handlers.NewCallbackHandler(bot.db, bot.cocAPI, bot.paymentService)
    
    return bot, nil
}

func (b *Bot) Start() error {
    logger.Info("Запуск бота...")
    
    // Инициализируем компоненты
    if err := b.initComponents(); err != nil {
        return fmt.Errorf("failed to initialize components: %w", err)
    }
    
    // Запускаем фоновые сервисы
    b.startBackgroundServices()
    
    // Настраиваем обновления
    u := tgbotapi.NewUpdate(0)
    u.Timeout = 60
    
    updates := b.api.GetUpdatesChan(u)
    
    // Обрабатываем обновления
    b.wg.Add(1)
    go func() {
        defer b.wg.Done()
        b.handleUpdates(updates)
    }()
    
    // Ждем сигнал завершения
    b.waitForShutdown()
    
    return nil
}

func (b *Bot) initComponents() error {
    // Запускаем миграции базы данных
    if err := database.Migrate(b.db); err != nil {
        return fmt.Errorf("failed to run migrations: %w", err)
    }
    
    // Проверяем соединение с Telegram API
    if _, err := b.api.GetMe(); err != nil {
        return fmt.Errorf("failed to connect to Telegram API: %w", err)
    }
    
    // Инициализируем архиватор войн
    b.warArchiver = services.NewWarArchiver(b.db, b.cocAPI, b.api)
    
    // Инициализируем монитор зданий
    b.buildingMonitor = services.NewBuildingMonitor(b.db, b.cocAPI, b.api)
    
    return nil
}

func (b *Bot) startBackgroundServices() {
    // Запускаем архиватор войн
    b.wg.Add(1)
    go func() {
        defer b.wg.Done()
        if err := b.warArchiver.Start(b.ctx); err != nil {
            logger.Errorf("War archiver error: %v", err)
        }
    }()
    
    // Запускаем монитор зданий
    b.wg.Add(1)
    go func() {
        defer b.wg.Done()
        if err := b.buildingMonitor.Start(b.ctx); err != nil {
            logger.Errorf("Building monitor error: %v", err)
        }
    }()
}

func (b *Bot) handleUpdates(updates tgbotapi.UpdatesChannel) {
    for {
        select {
        case update := <-updates:
            b.processUpdate(update)
        case <-b.ctx.Done():
            return
        }
    }
}

func (b *Bot) processUpdate(update tgbotapi.Update) {
    defer func() {
        if r := recover(); r != nil {
            logger.Errorf("Panic while processing update: %v", r)
        }
    }()
    
    if update.Message != nil {
        // Обрабатываем сообщения
        if err := b.messageHandler.Handle(b.ctx, b.api, update); err != nil {
            logger.Errorf("Error handling message: %v", err)
        }
    } else if update.CallbackQuery != nil {
        // Обрабатываем callback запросы
        if err := b.callbackHandler.Handle(b.ctx, b.api, update); err != nil {
            logger.Errorf("Error handling callback: %v", err)
        }
    }
}

func (b *Bot) waitForShutdown() {
    sigChan := make(chan os.Signal, 1)
    signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
    
    <-sigChan
    logger.Info("Получен сигнал завершения, останавливаем бота...")
    
    b.Shutdown()
}

func (b *Bot) Shutdown() {
    logger.Info("Завершение работы бота...")
    
    // Отменяем контекст
    b.cancel()
    
    // Ждем завершения горутин
    done := make(chan struct{})
    go func() {
        b.wg.Wait()
        close(done)
    }()
    
    select {
    case <-done:
        logger.Info("Все горутины завершены")
    case <-time.After(30 * time.Second):
        logger.Warn("Таймаут при завершении горутин")
    }
    
    // Закрываем соединения
    if b.paymentService != nil {
        b.paymentService.Close()
    }
    
    logger.Info("Бот остановлен")
}

// Отправка сообщения
func (b *Bot) SendMessage(chatID int64, text string, keyboard interface{}) error {
    msg := tgbotapi.NewMessage(chatID, text)
    msg.ParseMode = tgbotapi.ModeHTML
    
    if keyboard != nil {
        switch kb := keyboard.(type) {
        case tgbotapi.InlineKeyboardMarkup:
            msg.ReplyMarkup = kb
        case tgbotapi.ReplyKeyboardMarkup:
            msg.ReplyMarkup = kb
        }
    }
    
    _, err := b.api.Send(msg)
    return err
}

// Редактирование сообщения
func (b *Bot) EditMessage(chatID int64, messageID int, text string, keyboard *tgbotapi.InlineKeyboardMarkup) error {
    msg := tgbotapi.NewEditMessageText(chatID, messageID, text)
    msg.ParseMode = tgbotapi.ModeHTML
    
    if keyboard != nil {
        msg.ReplyMarkup = keyboard
    }
    
    _, err := b.api.Send(msg)
    return err
}
```

#### 5.2 Точка входа (cmd/bot/main.go)
```go
package main

import (
    "os"
    
    "github.com/SpencerMSU/clashbot-go/internal/bot"
    "github.com/SpencerMSU/clashbot-go/internal/config"
    "github.com/SpencerMSU/clashbot-go/pkg/logger"
)

func main() {
    // Загружаем конфигурацию
    cfg, err := config.Load()
    if err != nil {
        logger.Fatalf("Failed to load config: %v", err)
    }
    
    // Инициализируем логгер
    logger.Init(cfg.LogLevel)
    
    logger.Info("🚀 Запуск ClashBot Go...")
    
    // Создаем и запускаем бота
    clashBot, err := bot.New(cfg)
    if err != nil {
        logger.Fatalf("Failed to create bot: %v", err)
    }
    
    if err := clashBot.Start(); err != nil {
        logger.Fatalf("Bot error: %v", err)
        os.Exit(1)
    }
}
```

---

## 📋 Следующие шаги реализации

### 1. **Создание базовой структуры** (Неделя 1-2)
```bash
# Создание проекта
mkdir clashbot-go && cd clashbot-go
go mod init github.com/SpencerMSU/clashbot-go

# Создание структуры директорий
mkdir -p {cmd/bot,internal/{config,models,database,services,handlers,keyboards,bot,utils},pkg/logger,configs,migrations,docs,tests/{unit,integration}}

# Создание основных файлов
touch cmd/bot/main.go
touch internal/config/config.go
touch pkg/logger/logger.go
touch go.mod go.sum Makefile Dockerfile docker-compose.yml
```

### 2. **Настройка зависимостей** (Неделя 2)
```bash
# Установка основных зависимостей
go get github.com/go-telegram-bot-api/telegram-bot-api/v5
go get gorm.io/gorm
go get gorm.io/driver/sqlite
go get gorm.io/driver/postgres
go get github.com/go-resty/resty/v2
go get github.com/spf13/viper
go get github.com/sirupsen/logrus
go get github.com/google/uuid
go get golang.org/x/time
go get github.com/stretchr/testify
```

### 3. **Постепенная реализация модулей** (Недели 3-20)
- Реализовать каждый модуль по примерам выше
- Написать тесты для каждого модуля
- Провести интеграционное тестирование
- Оптимизировать производительность

### 4. **Финальная интеграция** (Недели 21-26)
- Полное тестирование всей системы
- Настройка мониторинга и метрик
- Подготовка к развертыванию
- Документация

Этот план обеспечивает поэтапную миграцию всех функций Python бота на Go с сохранением полной функциональности и улучшением производительности.