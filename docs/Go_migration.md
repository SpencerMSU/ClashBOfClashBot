# 🚀 ПОЛНЫЙ ПЛАН МИГРАЦИИ CLASHBOT С PYTHON НА GO

## 🎯 МАКСИМАЛЬНО ПОДРОБНОЕ РУКОВОДСТВО ДЛЯ НЕЙРОСЕТИ

> **КРИТИЧЕСКИ ВАЖНО**: Эта документация содержит АБСОЛЮТНО ВСЕ детали для миграции КАЖДОЙ функции бота с Python на Go. НИ ОДНА функция не должна быть пропущена или потеряна при миграции!

---

## 📊 ОБЗОР ПРОЕКТА И АРХИТЕКТУРА

### 📈 Статистика текущей кодовой базы Python
- **Общий объем**: 8,830+ строк Python кода
- **Основных модулей**: 17 компонентов
- **Функций для миграции**: 517 задач
- **Архитектура**: Полностью асинхронная с четким разделением ответственности
- **База данных**: 10 таблиц с полными отношениями
- **API интеграции**: Clash of Clans API + YooKassa платежи
- **Премиум функции**: Многопрофильность, мониторинг зданий, расширенная аналитика

### 🎯 ЦЕЛЬ МИГРАЦИИ
Перенести **ВСЮ** функциональность Python бота на Go с:
- ✅ **100% сохранением функциональности**
- ✅ **Улучшением производительности (2-5x быстрее)**
- ✅ **Снижением потребления памяти (30-50%)**
- ✅ **Упрощением развертывания**
- ✅ **Повышением стабильности**

---

## 🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: YOOKASSA ИНТЕГРАЦИЯ

### ❌ Проблема
**YooKassa не имеет официальной Go библиотеки!** 

В Python версии используется прямые HTTP вызовы к YooKassa API v3, что делает миграцию возможной.

### ✅ РЕШЕНИЕ: HTTP API ПОДХОД В GO

**АНАЛИЗ ТЕКУЩЕЙ PYTHON РЕАЛИЗАЦИИ:**

Текущий Python код НЕ использует специальную YooKassa библиотеку, а работает напрямую с HTTP API:

```python
# Текущая Python реализация
API_URL = "https://api.yookassa.ru/v3"

async def create_payment(self, telegram_id: int, subscription_type: str):
    # Прямой HTTP запрос
    async with session.post(
        f"{self.API_URL}/payments",
        headers=self._get_auth_headers(),
        data=json.dumps(payment_data)
    ) as response:
        return await response.json()
```

**ИДЕНТИЧНАЯ GO РЕАЛИЗАЦИЯ:**

```go
// Эквивалентная Go реализация
const APIURL = "https://api.yookassa.ru/v3"

func (y *YooKassaService) CreatePayment(telegramID int64, subscriptionType string) (*PaymentResponse, error) {
    // Прямой HTTP запрос через resty
    resp, err := y.client.R().
        SetHeaders(y.getAuthHeaders()).
        SetBody(paymentData).
        Post(APIURL + "/payments")
    
    var payment PaymentResponse
    return &payment, json.Unmarshal(resp.Body(), &payment)
}
```

### 🔧 ПОЛНАЯ YOOKASSA ИНТЕГРАЦИЯ В GO


#### 💳 ДЕТАЛЬНАЯ YOOKASSA GO РЕАЛИЗАЦИЯ

**1. СТРУКТУРЫ ДАННЫХ (точная копия Python):**

```go
package services

import (
    "encoding/base64"
    "encoding/json"
    "fmt"
    "time"
    
    "github.com/go-resty/resty/v2"
    "github.com/google/uuid"
)

// YooKassaService - точная копия Python класса
type YooKassaService struct {
    client      *resty.Client
    shopID      string
    secretKey   string
    botUsername string
}

// Константы - идентичные Python версии
const (
    TestShopID    = "1164328"
    TestSecretKey = "live_FVe4M7peyvzGPRZrM4UJq4pF6soCfuv4VZEgntsPmhs"
    APIURL        = "https://api.yookassa.ru/v3"
)

// SUBSCRIPTION_PRICES - точная копия из Python
var SubscriptionPrices = map[string]float64{
    // Premium
    "premium_1month":  49.00,
    "premium_3months": 119.00,
    "premium_6months": 199.00,
    "premium_1year":   349.00,
    // PRO PLUS
    "proplus_1month":  99.00,
    "proplus_3months": 249.00,
    "proplus_6months": 449.00,
    "proplus_1year":   799.00,
    // Legacy support
    "1month":  49.00,
    "3months": 119.00,
    "6months": 199.00,
    "1year":   349.00,
}

// SUBSCRIPTION_NAMES - точная копия из Python
var SubscriptionNames = map[string]string{
    // Premium
    "premium_1month":  "ClashBot Премиум подписка на 1 месяц",
    "premium_3months": "ClashBot Премиум подписка на 3 месяца",
    "premium_6months": "ClashBot Премиум подписка на 6 месяцев",
    "premium_1year":   "ClashBot Премиум подписка на 1 год",
    // PRO PLUS
    "proplus_1month":     "ClashBot ПРО ПЛЮС подписка на 1 месяц",
    "proplus_3months":    "ClashBot ПРО ПЛЮС подписка на 3 месяца",
    "proplus_6months":    "ClashBot ПРО ПЛЮС подписка на 6 месяцев",
    "proplus_1year":      "ClashBot ПРО ПЛЮС подписка на 1 год",
    "proplus_permanent":  "ClashBot ПРО ПЛЮС подписка (Вечная)",
    // Legacy support
    "1month":  "ClashBot Премиум подписка на 1 месяц",
    "3months": "ClashBot Премиум подписка на 3 месяца",
    "6months": "ClashBot Премиум подписка на 6 месяцев",
    "1year":   "ClashBot Премиум подписка на 1 год",
}

// PaymentRequest - структура запроса платежа
type PaymentRequest struct {
    Amount       AmountInfo   `json:"amount"`
    Confirmation Confirmation `json:"confirmation"`
    Capture      bool         `json:"capture"`
    Description  string       `json:"description"`
    Metadata     Metadata     `json:"metadata"`
}

type AmountInfo struct {
    Value    string `json:"value"`
    Currency string `json:"currency"`
}

type Confirmation struct {
    Type      string `json:"type"`
    ReturnURL string `json:"return_url"`
}

type Metadata struct {
    TelegramID       string `json:"telegram_id"`
    SubscriptionType string `json:"subscription_type"`
    CreatedAt        string `json:"created_at"`
}

// PaymentResponse - структура ответа платежа
type PaymentResponse struct {
    ID           string       `json:"id"`
    Status       string       `json:"status"`
    Amount       AmountInfo   `json:"amount"`
    Description  string       `json:"description"`
    Confirmation Confirmation `json:"confirmation"`
    CreatedAt    time.Time    `json:"created_at"`
    Metadata     Metadata     `json:"metadata"`
}
```

**2. ОСНОВНЫЕ МЕТОДЫ (точная копия Python функций):**

```go
// NewYooKassaService - конструктор (копия __init__)
func NewYooKassaService(shopID, secretKey, botUsername string) *YooKassaService {
    client := resty.New()
    client.SetTimeout(30 * time.Second)
    
    // Fallback на тестовые значения
    if shopID == "" {
        shopID = TestShopID
    }
    if secretKey == "" {
        secretKey = TestSecretKey
    }
    if botUsername == "" {
        botUsername = "YourBotUsername"
    }
    
    return &YooKassaService{
        client:      client,
        shopID:      shopID,
        secretKey:   secretKey,
        botUsername: botUsername,
    }
}

// getAuthHeaders - точная копия _get_auth_headers()
func (y *YooKassaService) getAuthHeaders() map[string]string {
    credentials := fmt.Sprintf("%s:%s", y.shopID, y.secretKey)
    encodedCredentials := base64.StdEncoding.EncodeToString([]byte(credentials))
    
    return map[string]string{
        "Authorization":  fmt.Sprintf("Basic %s", encodedCredentials),
        "Content-Type":   "application/json",
        "Idempotence-Key": uuid.New().String(),
    }
}

// CreatePayment - точная копия create_payment()
func (y *YooKassaService) CreatePayment(telegramID int64, subscriptionType string, returnURL string) (*PaymentResponse, error) {
    // Проверяем тип подписки
    amount, exists := SubscriptionPrices[subscriptionType]
    if !exists {
        return nil, fmt.Errorf("неизвестный тип подписки: %s", subscriptionType)
    }
    
    description, exists := SubscriptionNames[subscriptionType]
    if !exists {
        description = "Неизвестная подписка"
    }
    
    // Создаем return URL если не предоставлен
    if returnURL == "" {
        returnURL = fmt.Sprintf("https://t.me/%s", y.botUsername)
    }
    
    // Формируем данные запроса - точная копия Python
    paymentData := PaymentRequest{
        Amount: AmountInfo{
            Value:    fmt.Sprintf("%.2f", amount),
            Currency: "RUB",
        },
        Confirmation: Confirmation{
            Type:      "redirect",
            ReturnURL: returnURL,
        },
        Capture:     true,
        Description: description,
        Metadata: Metadata{
            TelegramID:       fmt.Sprintf("%d", telegramID),
            SubscriptionType: subscriptionType,
            CreatedAt:        time.Now().Format(time.RFC3339),
        },
    }
    
    // Выполняем HTTP запрос - идентично Python
    var response PaymentResponse
    resp, err := y.client.R().
        SetHeaders(y.getAuthHeaders()).
        SetBody(paymentData).
        SetResult(&response).
        Post(APIURL + "/payments")
    
    if err != nil {
        return nil, fmt.Errorf("ошибка при создании платежа: %w", err)
    }
    
    if resp.StatusCode() != 200 {
        return nil, fmt.Errorf("ошибка создания платежа: %d - %s", resp.StatusCode(), resp.String())
    }
    
    return &response, nil
}

// CheckPaymentStatus - точная копия check_payment_status()
func (y *YooKassaService) CheckPaymentStatus(paymentID string) (*PaymentResponse, error) {
    var response PaymentResponse
    resp, err := y.client.R().
        SetHeaders(y.getAuthHeaders()).
        SetResult(&response).
        Get(fmt.Sprintf("%s/payments/%s", APIURL, paymentID))
    
    if err != nil {
        return nil, fmt.Errorf("ошибка при проверке платежа: %w", err)
    }
    
    if resp.StatusCode() != 200 {
        return nil, fmt.Errorf("ошибка проверки платежа: %d - %s", resp.StatusCode(), resp.String())
    }
    
    return &response, nil
}

// GetSubscriptionDuration - точная копия get_subscription_duration()
func (y *YooKassaService) GetSubscriptionDuration(subscriptionType string) time.Duration {
    if strings.Contains(subscriptionType, "permanent") {
        return time.Hour * 24 * 36500 // 100 лет для вечной подписки
    }
    
    switch {
    case strings.Contains(subscriptionType, "1month"):
        return time.Hour * 24 * 30
    case strings.Contains(subscriptionType, "3months"):
        return time.Hour * 24 * 90
    case strings.Contains(subscriptionType, "6months"):
        return time.Hour * 24 * 180
    case strings.Contains(subscriptionType, "1year"):
        return time.Hour * 24 * 365
    default:
        // Fallback для legacy форматов
        durations := map[string]time.Duration{
            "1month":  time.Hour * 24 * 30,
            "3months": time.Hour * 24 * 90,
            "6months": time.Hour * 24 * 180,
            "1year":   time.Hour * 24 * 365,
        }
        if duration, exists := durations[subscriptionType]; exists {
            return duration
        }
        return time.Hour * 24 * 30 // По умолчанию 30 дней
    }
}

// GetSubscriptionPrice - точная копия get_subscription_price()
func (y *YooKassaService) GetSubscriptionPrice(subscriptionType string) float64 {
    if price, exists := SubscriptionPrices[subscriptionType]; exists {
        return price
    }
    return 0.0
}

// GetSubscriptionName - точная копия get_subscription_name()
func (y *YooKassaService) GetSubscriptionName(subscriptionType string) string {
    if name, exists := SubscriptionNames[subscriptionType]; exists {
        return name
    }
    return "Неизвестная подписка"
}

// CreateRefund - точная копия create_refund()
func (y *YooKassaService) CreateRefund(paymentID string, amount float64, reason string) (*RefundResponse, error) {
    refundData := RefundRequest{
        Amount: AmountInfo{
            Value:    fmt.Sprintf("%.2f", amount),
            Currency: "RUB",
        },
        PaymentID: paymentID,
    }
    
    if reason != "" {
        refundData.Description = reason
    }
    
    var response RefundResponse
    resp, err := y.client.R().
        SetHeaders(y.getAuthHeaders()).
        SetBody(refundData).
        SetResult(&response).
        Post(APIURL + "/refunds")
    
    if err != nil {
        return nil, fmt.Errorf("ошибка при создании возврата: %w", err)
    }
    
    if resp.StatusCode() != 200 {
        return nil, fmt.Errorf("ошибка создания возврата: %d - %s", resp.StatusCode(), resp.String())
    }
    
    return &response, nil
}

// Close - точная копия close()
func (y *YooKassaService) Close() {
    // В Go нет необходимости в явном закрытии HTTP клиента
    // Но для совместимости оставляем метод
}
```

**3. ДОПОЛНИТЕЛЬНЫЕ СТРУКТУРЫ:**

```go
// RefundRequest - для создания возвратов
type RefundRequest struct {
    Amount      AmountInfo `json:"amount"`
    PaymentID   string     `json:"payment_id"`
    Description string     `json:"description,omitempty"`
}

// RefundResponse - ответ на возврат
type RefundResponse struct {
    ID          string     `json:"id"`
    Status      string     `json:"status"`
    Amount      AmountInfo `json:"amount"`
    PaymentID   string     `json:"payment_id"`
    Description string     `json:"description"`
    CreatedAt   time.Time  `json:"created_at"`
}
```

---

## 📋 ПОЛНЫЙ ПЕРЕЧЕНЬ ФУНКЦИЙ ДЛЯ МИГРАЦИИ

### 🏗️ **ОСНОВНЫЕ КОМПОНЕНТЫ (все должны быть перенесены)**

#### 1. **bot.py** → **bot.go** (324 строки)
**КАЖДАЯ функция для переноса:**
- [ ] `ClashBot` - основной класс оркестрации бота
- [ ] `initialize()` - асинхронная инициализация компонентов
- [ ] `_init_components()` - инициализация базы данных и сервисов
- [ ] `_register_handlers()` - регистрация обработчиков команд
- [ ] `_start_command()` - обработчик команды /start
- [ ] `_start_war_archiver()` - запуск архиватора войн
- [ ] `_start_building_monitor()` - запуск мониторинга зданий
- [ ] `run()` - основной цикл работы бота
- [ ] `shutdown()` - корректное завершение работы
- [ ] `send_message()` - отправка сообщений
- [ ] `edit_message()` - редактирование сообщений
- [ ] `_cleanup()` - очистка ресурсов

#### 2. **config.py** → **config.go** (78 строк)
**КАЖДАЯ функция для переноса:**
- [ ] `BotConfig` - класс конфигурации
- [ ] `_read_api_tokens()` - чтение токенов из файла
- [ ] `_validate_config()` - валидация обязательных параметров
- [ ] **ВСЕ параметры конфигурации:**
  - [ ] `BOT_TOKEN` - токен Telegram бота
  - [ ] `BOT_USERNAME` - имя пользователя бота
  - [ ] `COC_API_TOKEN` - токен Clash of Clans API
  - [ ] `COC_API_BASE_URL` - базовый URL API
  - [ ] `DATABASE_PATH` - путь к базе данных
  - [ ] `YOOKASSA_SHOP_ID` - ID магазина YooKassa
  - [ ] `YOOKASSA_SECRET_KEY` - секретный ключ YooKassa
  - [ ] `ARCHIVE_CHECK_INTERVAL` - интервал архивации
  - [ ] `DONATION_SNAPSHOT_INTERVAL` - интервал снапшотов донатов
  - [ ] `OUR_CLAN_TAG` - тег нашего клана

#### 3. **database.py** → **database.go** (923 строки)
**ВСЕ таблицы и функции для переноса:**

**Таблица users:**
- [ ] `save_user()` - сохранение пользователя
- [ ] `find_user()` - поиск пользователя
- [ ] `user_exists()` - проверка существования
- [ ] `update_user_tag()` - обновление тега
- [ ] `delete_user()` - удаление пользователя

**Таблица user_profiles (Премиум):**
- [ ] `save_user_profile()` - сохранение профиля
- [ ] `get_user_profiles()` - получение всех профилей пользователя
- [ ] `get_primary_profile()` - получение основного профиля
- [ ] `set_primary_profile()` - установка основного профиля
- [ ] `delete_user_profile()` - удаление профиля
- [ ] `get_profile_count()` - подсчет профилей

**Таблица wars:**
- [ ] `save_war()` - сохранение войны
- [ ] `war_exists()` - проверка существования войны
- [ ] `get_recent_wars()` - получение последних войн
- [ ] `get_war_by_end_time()` - поиск войны по времени окончания

**Таблица attacks:**
- [ ] `save_attack()` - сохранение атаки
- [ ] `get_war_attacks()` - получение атак войны
- [ ] `calculate_war_violations()` - расчет нарушений

**Таблица cwl_seasons:**
- [ ] `save_cwl_season()` - сохранение сезона CWL
- [ ] `get_current_cwl_season()` - получение текущего сезона
- [ ] `cwl_season_exists()` - проверка существования сезона

**Таблица player_stats_snapshots:**
- [ ] `save_player_snapshot()` - сохранение снапшота игрока
- [ ] `get_player_snapshots()` - получение снапшотов
- [ ] `get_latest_snapshot()` - получение последнего снапшота

**Таблица notifications:**
- [ ] `is_notifications_enabled()` - проверка включенности уведомлений
- [ ] `enable_notifications()` - включение уведомлений
- [ ] `disable_notifications()` - отключение уведомлений
- [ ] `toggle_notifications()` - переключение уведомлений
- [ ] `get_notification_users()` - список пользователей с уведомлениями

**Таблица subscriptions:**
- [ ] `save_subscription()` - сохранение подписки
- [ ] `get_subscription()` - получение подписки
- [ ] `extend_subscription()` - продление подписки
- [ ] `deactivate_subscription()` - деактивация подписки

**Таблица building_trackers (Премиум):**
- [ ] `save_building_tracker()` - сохранение трекера зданий
- [ ] `get_building_tracker()` - получение трекера
- [ ] `get_active_building_trackers()` - получение активных трекеров
- [ ] `toggle_building_tracker()` - переключение трекера
- [ ] `is_tracking_active()` - проверка активности трекинга

**Таблица building_snapshots (Премиум):**
- [ ] `save_building_snapshot()` - сохранение снапшота зданий
- [ ] `get_building_snapshots()` - получение снапшотов
- [ ] `get_latest_building_snapshot()` - последний снапшот

**Таблица linked_clans (Премиум):**
- [ ] `save_linked_clan()` - сохранение привязанного клана
- [ ] `get_linked_clans()` - получение привязанных кланов
- [ ] `remove_linked_clan()` - удаление привязанного клана

#### 4. **coc_api.py** → **coc_api.go** (369 строк)
**ВСЕ функции для переноса:**
- [ ] `CocApiClient` - основной клиент API
- [ ] **Методы игрока:**
  - [ ] `get_player()` - получение данных игрока
  - [ ] `get_player_with_retry()` - получение с повторами
- [ ] **Методы клана:**
  - [ ] `get_clan()` - получение данных клана
  - [ ] `get_clan_members()` - получение участников клана
  - [ ] `get_clan_current_war()` - текущая война клана
  - [ ] `get_clan_warlog()` - лог войн клана
  - [ ] `get_clan_current_cwl()` - текущий CWL
- [ ] **Валидация и форматирование:**
  - [ ] `validate_player_tag()` - валидация тега игрока
  - [ ] `validate_clan_tag()` - валидация тега клана
  - [ ] `format_player_tag()` - форматирование тега игрока
  - [ ] `format_clan_tag()` - форматирование тега клана
  - [ ] `is_player_tag()` - определение типа тега
  - [ ] `is_clan_tag()` - определение типа тега
- [ ] **Утилиты войн:**
  - [ ] `is_war_ended()` - проверка окончания войны
  - [ ] `is_war_in_preparation()` - проверка подготовки к войне
  - [ ] `is_cwl_active()` - проверка активности CWL

#### 5. **payment_service.py** → **payment_service.go** (253 строки)
**ВСЕ функции платежной системы для переноса:**
- [ ] `YooKassaService` - основной класс платежей
- [ ] `create_payment()` - создание платежа (ДЕТАЛЬНО ОПИСАНО ВЫШЕ)
- [ ] `check_payment_status()` - проверка статуса платежа
- [ ] `create_refund()` - создание возврата
- [ ] `process_refund_notification()` - обработка уведомлений о возврате
- [ ] `_get_auth_headers()` - получение заголовков авторизации
- [ ] `get_subscription_duration()` - получение длительности подписки
- [ ] `get_subscription_price()` - получение цены подписки
- [ ] `get_subscription_name()` - получение названия подписки
- [ ] `close()` - закрытие сессии
- [ ] **SUBSCRIPTION_PRICES** - цены подписок (8 типов)
- [ ] **SUBSCRIPTION_NAMES** - названия подписок
- [ ] **TEST_SHOP_ID** и **TEST_SECRET_KEY** - тестовые данные
- [ ] **API_URL** - URL YooKassa API


#### 6. **handlers.py** → **handlers.go** (945 строк)
**ВСЕ обработчики для переноса:**

**MessageHandler класс:**
- [ ] `handle_message()` - основной обработчик сообщений
- [ ] `_handle_state_message()` - обработка сообщений в состоянии
- [ ] `_handle_menu_command()` - обработка команд меню
- [ ] `_handle_player_tag_input()` - обработка ввода тега игрока
- [ ] `_handle_clan_tag_input()` - обработка ввода тега клана
- [ ] `_handle_profile_addition()` - добавление профиля

**CallbackHandler класс:**
- [ ] `handle_callback()` - основной обработчик callback'ов
- [ ] `_handle_members_sort()` - сортировка участников
- [ ] `_handle_members_view()` - просмотр участников
- [ ] `_handle_war_list()` - список войн
- [ ] `_handle_war_info()` - информация о войне
- [ ] `_handle_profile_callback()` - callback профиля
- [ ] `_handle_cwl_bonus()` - бонусы CWL
- [ ] `_handle_current_war()` - текущая война
- [ ] `_handle_cwl_info()` - информация CWL
- [ ] `_handle_subscription_menu()` - меню подписки
- [ ] `_handle_subscription_extend()` - продление подписки
- [ ] `_handle_subscription_period()` - период подписки
- [ ] `_handle_subscription_type()` - тип подписки
- [ ] `_handle_subscription_payment()` - оплата подписки
- [ ] `_handle_premium_menu()` - премиум меню
- [ ] `_handle_notify_advanced()` - расширенные уведомления
- [ ] `_handle_building_tracker()` - трекер зданий
- [ ] `_handle_building_toggle()` - переключение трекера
- [ ] `_handle_analyzer_refresh()` - обновление анализатора

#### 7. **message_generator.py** → **message_generator.go** (2,891 строка - САМЫЙ БОЛЬШОЙ)
**ВСЕ генераторы сообщений для переноса:**

**Основные методы:**
- [ ] `MessageGenerator` - основной класс генератора
- [ ] `_format_datetime()` - форматирование времени
- [ ] `close()` - закрытие ресурсов

**Генерация профилей:**
- [ ] `generate_player_info()` - информация об игроке
- [ ] `generate_player_achievements()` - достижения игрока
- [ ] `generate_profile_manager()` - менеджер профилей
- [ ] `add_profile_dialog()` - диалог добавления профиля

**Генерация кланов:**
- [ ] `generate_clan_info()` - информация о клане
- [ ] `generate_clan_members()` - участники клана
- [ ] `generate_war_list()` - список войн
- [ ] `generate_war_info()` - информация о войне
- [ ] `generate_current_war()` - текущая война
- [ ] `generate_cwl_info()` - информация CWL
- [ ] `display_cwl_bonus_info()` - информация о бонусах CWL

**Генерация уведомлений:**
- [ ] `handle_notifications_menu()` - меню уведомлений
- [ ] `handle_notification_toggle()` - переключение уведомлений
- [ ] `_send_payment_notification()` - уведомления о платежах
- [ ] `_save_pending_notification()` - сохранение отложенных уведомлений

**Генерация подписок:**
- [ ] `generate_subscription_menu()` - меню подписки
- [ ] `generate_subscription_extend_menu()` - меню продления
- [ ] `generate_subscription_type_menu()` - выбор типа подписки
- [ ] `generate_subscription_period_menu()` - выбор периода
- [ ] `_generate_payment_button()` - кнопки оплаты

**Премиум функции:**
- [ ] `handle_building_tracker_toggle()` - переключение трекера зданий
- [ ] `display_war_violations()` - отображение нарушений войны

**Утилиты форматирования:**
- [ ] `_format_war_member()` - форматирование участника войны
- [ ] `_format_clan_member()` - форматирование участника клана
- [ ] `_format_attack()` - форматирование атаки
- [ ] `_get_war_state_emoji()` - эмодзи состояния войны

#### 8. **keyboards.py** → **keyboards.go** (786 строк)
**ВСЕ клавиатуры для переноса:**

**Основные клавиатуры:**
- [ ] `main_menu()` - главное меню
- [ ] `profile_menu()` - меню профиля
- [ ] `clan_menu()` - меню клана
- [ ] `back_to_main()` - возврат в главное меню

**Клавиатуры участников:**
- [ ] `members_keyboard()` - клавиатура участников
- [ ] `members_sort_keyboard()` - сортировка участников
- [ ] `members_view_keyboard()` - вид участников

**Клавиатуры войн:**
- [ ] `war_list_keyboard()` - список войн
- [ ] `war_info_keyboard()` - информация о войне
- [ ] `current_war_keyboard()` - текущая война

**Клавиатуры подписок:**
- [ ] `subscription_menu()` - меню подписки
- [ ] `subscription_extend_menu()` - продление подписки
- [ ] `subscription_type_keyboard()` - выбор типа
- [ ] `subscription_period_keyboard()` - выбор периода
- [ ] `payment_keyboard()` - клавиатуры оплаты

**Уведомления:**
- [ ] `notification_toggle()` - переключение уведомлений
- [ ] `notification_advanced()` - расширенные настройки

**Премиум клавиатуры:**
- [ ] `premium_menu()` - премиум меню
- [ ] `building_tracker_menu()` - меню трекера зданий
- [ ] `profile_manager_keyboard()` - менеджер профилей

**Константы:**
- [ ] Все текстовые константы кнопок (50+ констант)
- [ ] Все callback константы (30+ констант)

#### 9. **war_archiver.py** → **war_archiver.go** (318 строк)
**ВСЕ функции архиватора для переноса:**
- [ ] `WarArchiver` - основной класс архиватора
- [ ] `start()` - запуск сервиса архивации
- [ ] `stop()` - остановка сервиса
- [ ] `_archive_loop()` - основной цикл архивации
- [ ] `_check_and_archive_wars()` - проверка и архивация войн
- [ ] `_archive_war()` - архивация конкретной войны
- [ ] `_send_war_notification()` - отправка уведомлений о войне
- [ ] `_take_donation_snapshot()` - снапшот донатов
- [ ] `_should_take_donation_snapshot()` - проверка необходимости снапшота
- [ ] `set_bot_instance()` - установка экземпляра бота

#### 10. **building_monitor.py** → **building_monitor.go** (467 строк)
**ВСЕ функции мониторинга зданий для переноса:**
- [ ] `BuildingMonitor` - основной класс мониторинга
- [ ] `start()` - запуск мониторинга
- [ ] `stop()` - остановка мониторинга
- [ ] `_monitor_loop()` - основной цикл мониторинга
- [ ] `_check_building_updates()` - проверка обновлений зданий
- [ ] `_process_building_changes()` - обработка изменений зданий
- [ ] `_send_building_notification()` - уведомления об улучшениях
- [ ] `is_tracking_active()` - проверка активности трекинга
- [ ] `_compare_buildings()` - сравнение состояний зданий
- [ ] `set_bot_instance()` - установка экземпляра бота
- [ ] **building_names_ru** - словарь названий зданий на русском (50+ названий)

#### 11. **building_data.py** → **building_data.go** (895 строк)
**ВСЯ база данных зданий для переноса:**
- [ ] `BUILDING_DATA` - полная база данных всех зданий
- [ ] **Типы зданий:**
  - [ ] Defense buildings (оборонительные)
  - [ ] Resource buildings (ресурсные)
  - [ ] Army buildings (военные)
  - [ ] Other buildings (прочие)
- [ ] **Данные для каждого здания:**
  - [ ] Уровни улучшения
  - [ ] Стоимость улучшений
  - [ ] Время улучшений
  - [ ] Требования к ратуше
- [ ] `get_building_info()` - получение информации о здании
- [ ] `get_upgrade_cost()` - стоимость улучшения
- [ ] `get_upgrade_time()` - время улучшения

#### 12. **user_state.py** → **user_state.go** (15 строк)
**ВСЕ состояния пользователя для переноса:**
- [ ] `UserState` - енум состояний
- [ ] **Все состояния:**
  - [ ] `AWAITING_PLAYER_TAG_TO_LINK`
  - [ ] `AWAITING_PLAYER_TAG_TO_SEARCH`
  - [ ] `AWAITING_CLAN_TAG_TO_SEARCH`
  - [ ] `AWAITING_CLAN_TAG_TO_LINK`
  - [ ] `AWAITING_NOTIFICATION_TIME`
  - [ ] `AWAITING_PLAYER_TAG_TO_ADD_PROFILE`

#### 13. **translations.py** → **translations.go** (переводы)
**ВСЯ система переводов для переноса:**
- [ ] `TranslationManager` - менеджер переводов
- [ ] `get_text()` - получение переведенного текста
- [ ] `get_user_language()` - получение языка пользователя
- [ ] **Словари переводов:**
  - [ ] Русский язык (100+ строк)
  - [ ] Английский язык (100+ строк)
- [ ] **Категории переводов:**
  - [ ] CWL сообщения
  - [ ] Анализатор сообщения
  - [ ] Общие ошибки
  - [ ] Тексты кнопок
  - [ ] Названия достижений (200+ достижений)

#### 14. **policy.py** → **policy.go**
**ВСЕ политики и правила для переноса:**
- [ ] `get_policy_url()` - получение URL политики
- [ ] `get_terms_url()` - получение URL условий
- [ ] Политика конфиденциальности
- [ ] Пользовательское соглашение

#### 15. **models/** → **models/**
**ВСЕ модели данных для переноса:**

**models/user.py:**
- [ ] `User` - модель пользователя
- [ ] Валидация данных пользователя

**models/user_profile.py:**
- [ ] `UserProfile` - модель профиля пользователя
- [ ] Валидация профилей

**models/war.py:**
- [ ] `WarToSave` - модель войны для сохранения
- [ ] `AttackData` - модель данных атаки
- [ ] Валидация данных войн

**models/subscription.py:**
- [ ] `Subscription` - модель подписки
- [ ] `is_active()` - проверка активности
- [ ] `is_expired()` - проверка истечения
- [ ] `days_until_expiry()` - дни до истечения

**models/building.py:**
- [ ] `BuildingSnapshot` - снапшот зданий
- [ ] `BuildingUpgrade` - улучшение здания
- [ ] `BuildingTracker` - трекер зданий
- [ ] Валидация данных зданий

**models/linked_clan.py:**
- [ ] `LinkedClan` - привязанный клан
- [ ] Валидация привязанных кланов

#### 16. **main.py** → **main.go** (62 строки)
**ВСЯ точка входа для переноса:**
- [ ] `main()` - главная функция
- [ ] Настройка логирования
- [ ] Проверка переменных окружения
- [ ] Обработка сигналов завершения
- [ ] Graceful shutdown

#### 17. **validate.py** → **validate.go** (140 строк)
**ВСЯ система валидации для переноса:**
- [ ] `validate_components()` - валидация всех компонентов
- [ ] `create_test_tokens_file()` - создание тестовых токенов
- [ ] Тестирование всех модулей
- [ ] Проверка целостности системы

---

## 🛠️ ТЕХНИЧЕСКИЙ СТЕК GO

### 🔧 Основные библиотеки
```go
// Web Framework для HTTP и webhooks
"github.com/gofiber/fiber/v2" // или "github.com/gin-gonic/gin"

// ORM для работы с базой данных
"gorm.io/gorm"
"gorm.io/driver/sqlite"
"gorm.io/driver/postgres"

// Telegram Bot API
"github.com/go-telegram-bot-api/telegram-bot-api/v5"
// или "gopkg.in/telebot.v3"

// HTTP клиент (для YooKassa и COC API)
"github.com/go-resty/resty/v2"

// Конфигурация
"github.com/spf13/viper"

// Логирование
"github.com/sirupsen/logrus"
// или "github.com/rs/zerolog"

// Тестирование
"github.com/stretchr/testify"

// Utilities
"github.com/google/uuid"
"golang.org/x/time/rate"
```

### 📁 ТОЧНАЯ СТРУКТУРА ПРОЕКТА GO
```
clashbot-go/
├── cmd/
│   └── bot/
│       └── main.go                  # Точка входа (main.py)
├── internal/
│   ├── config/
│   │   └── config.go               # config.py
│   ├── models/
│   │   ├── user.go                 # models/user.py
│   │   ├── user_profile.go         # models/user_profile.py
│   │   ├── war.go                  # models/war.py
│   │   ├── subscription.go         # models/subscription.py
│   │   ├── building.go             # models/building.py
│   │   └── linked_clan.go          # models/linked_clan.py
│   ├── database/
│   │   ├── database.go             # database.py
│   │   ├── migrations.go           # Система миграций
│   │   └── repository/
│   │       ├── user.go             # Репозиторий пользователей
│   │       ├── clan.go             # Репозиторий кланов
│   │       └── war.go              # Репозиторий войн
│   ├── services/
│   │   ├── coc_api.go              # coc_api.py
│   │   ├── payment.go              # payment_service.py
│   │   ├── war_archiver.go         # war_archiver.py
│   │   ├── building_monitor.go     # building_monitor.py
│   │   └── message_generator.go    # message_generator.py
│   ├── handlers/
│   │   ├── message.go              # handlers.py (MessageHandler)
│   │   ├── callback.go             # handlers.py (CallbackHandler)
│   │   └── commands.go             # Обработчик команд
│   ├── keyboards/
│   │   └── keyboards.go            # keyboards.py
│   ├── bot/
│   │   └── bot.go                  # bot.py
│   ├── utils/
│   │   ├── translations.go         # translations.py
│   │   ├── validators.go           # validate.py
│   │   ├── user_state.go           # user_state.py
│   │   ├── policy.go               # policy.py
│   │   └── building_data.go        # building_data.py
│   └── types/
│       └── enums.go                # Все енумы и константы
├── pkg/
│   └── logger/
│       └── logger.go               # Система логирования
├── configs/
│   ├── config.yaml                 # Основная конфигурация
│   └── config.example.yaml         # Пример конфигурации
├── migrations/
│   ├── 001_initial.sql             # Начальная миграция
│   └── 002_premium_features.sql    # Премиум функции
├── docs/
│   └── api.md                      # API документация
├── tests/
│   ├── integration/                # Интеграционные тесты
│   └── unit/                       # Юнит тесты
├── go.mod
├── go.sum
├── Makefile
├── Dockerfile
└── docker-compose.yml
```

---

## ⏱️ ДЕТАЛЬНЫЙ ПЛАН ВЫПОЛНЕНИЯ

### **ЭТАП 1: Инфраструктура (2-3 недели)**
**Задачи:**
- [ ] Создание точной структуры проекта Go
- [ ] Настройка Go modules и всех зависимостей
- [ ] Настройка системы сборки (Makefile)
- [ ] Создание Dockerfile и docker-compose
- [ ] Настройка CI/CD pipeline
- [ ] Настройка линтеров и форматеров

**Критерии готовности:**
- [ ] Проект компилируется без ошибок
- [ ] Все зависимости установлены корректно
- [ ] CI/CD pipeline работает
- [ ] Docker образы собираются успешно

### **ЭТАП 2: Базовые компоненты (3-4 недели)**
**Задачи:**
- [ ] config.go - система конфигурации с полной совместимостью
- [ ] logger.go - система логирования  
- [ ] Все базовые модели данных (User, War, Subscription, Building)
- [ ] Система валидации (точная копия validate.py)
- [ ] Базовое подключение к Telegram Bot API

**Критерии готовности:**
- [ ] Конфигурация загружается как в Python
- [ ] Логирование работает идентично
- [ ] Бот может подключиться к Telegram API
- [ ] Все валидаторы работают

### **ЭТАП 3: База данных (2-3 недели)**
**Задачи:**
- [ ] Все 10 GORM моделей (точная копия таблиц)
- [ ] Система миграций с сохранением данных
- [ ] database.go - полный сервисный слой
- [ ] ВСЕ методы работы с БД (923 строки функций)
- [ ] Полные тесты для БД операций

**Критерии готовности:**
- [ ] Все таблицы создаются идентично Python
- [ ] Все CRUD операции работают точно так же
- [ ] Данные мигрируют без потерь
- [ ] Все тесты проходят

### **ЭТАП 4: API интеграции (2-3 недели)**  
**Задачи:**
- [ ] coc_api.go - полный Clash of Clans API клиент
- [ ] payment.go - ПОЛНАЯ YooKassa интеграция (детально выше)
- [ ] Система валидации тегов (точная копия)
- [ ] Обработка ошибок и retry логика
- [ ] Rate limiting для API

**Критерии готовности:**
- [ ] ВСЕ API методы работают идентично Python
- [ ] Валидация тегов работает точно так же
- [ ] YooKassa платежи обрабатываются полностью
- [ ] Rate limiting работает корректно

### **ЭТАП 5: Обработчики (4-5 недель)**
**Задачи:**
- [ ] message.go - обработчик сообщений (точная копия)
- [ ] callback.go - обработчик callback'ов (все функции)
- [ ] Система состояний пользователя (user_state.go)
- [ ] keyboards.go - генерация всех клавиатур
- [ ] message_generator.go - генерация всех сообщений (2,891 строка!)

**Критерии готовности:**
- [ ] ВСЕ команды обрабатываются идентично
- [ ] ВСЕ callback'и работают корректно
- [ ] ВСЕ клавиатуры генерируются правильно
- [ ] ВСЕ сообщения форматируются точно так же

### **ЭТАП 6: Продвинутые функции (3-4 недели)**
**Задачи:**
- [ ] war_archiver.go - полная архивация войн
- [ ] building_monitor.go - полный мониторинг зданий  
- [ ] Система уведомлений (все типы)
- [ ] Многопрофильность (премиум функция)
- [ ] building_data.go - полная база данных зданий

**Критерии готовности:**
- [ ] Войны архивируются точно так же
- [ ] Здания отслеживаются идентично
- [ ] ВСЕ уведомления приходят вовремя
- [ ] Многопрофильность работает полностью

### **ЭТАП 7: Премиум функции (2-3 недели)**
**Задачи:**
- [ ] Полное управление подписками
- [ ] ВСЕ ограничения для бесплатных пользователей
- [ ] Расширенная аналитика (все функции)
- [ ] ВСЕ премиум-только функции

**Критерии готовности:**
- [ ] Подписки работают точно как в Python
- [ ] ВСЕ ограничения применяются корректно
- [ ] ВСЕ премиум функции доступны только подписчикам

### **ЭТАП 8: Тестирование и развертывание (2-3 недели)**
**Задачи:**
- [ ] Полное тестирование ВСЕХ функций
- [ ] Нагрузочное тестирование
- [ ] Оптимизация производительности
- [ ] Полная документация API
- [ ] Развертывание в продакшн

**Критерии готовности:**
- [ ] ВСЕ тесты проходят (517 функций)
- [ ] Производительность лучше Python версии
- [ ] Документация полная и точная
- [ ] Бот работает в продакшн без ошибок

---

## 🎯 КРИТЕРИИ УСПЕШНОЙ МИГРАЦИИ

### ✅ Функциональные требования
- [ ] **100% функциональность** - ВСЕ 517 функций Python версии работают в Go
- [ ] **Все команды работают** - /start и все команды меню идентично
- [ ] **Все callback'и работают** - все кнопки интерфейса
- [ ] **ВСЕ премиум функции** - подписки, мониторинг зданий, множественные профили
- [ ] **Полная система платежей** - YooKassa интеграция 100% функциональна
- [ ] **ВСЕ уведомления** - все типы уведомлений работают
- [ ] **Полная архивация данных** - войны и статистика сохраняются

### ⚡ Производительные требования
- [ ] **Время ответа** - не больше 2 секунд для большинства операций
- [ ] **Потребление памяти** - меньше текущей Python версии
- [ ] **Стабильность** - отсутствие memory leaks
- [ ] **Конкурентность** - обработка множественных запросов

### 🧪 Качественные требования
- [ ] **Покрытие тестами** - минимум 80% для всех функций
- [ ] **Документация** - полная документация API и развертывания
- [ ] **Логирование** - подробные логи для debugging
- [ ] **Мониторинг** - метрики производительности

### 🔒 Безопасность
- [ ] **Валидация входных данных** - все пользовательские данные валидируются
- [ ] **Защита от SQL инъекций** - использование параметризованных запросов
- [ ] **Защита токенов** - безопасное хранение API ключей
- [ ] **Rate limiting** - защита от спама

---

## 📊 ВРЕМЕННАЯ ОЦЕНКА

| Этап | Функции | Время | Риски |
|------|---------|-------|--------|
| 1. Инфраструктура | Проект, CI/CD | 2-3 недели | Низкий |
| 2. Базовые компоненты | Config, Logger, Models | 3-4 недели | Низкий |
| 3. База данных | 10 таблиц + методы | 2-3 недели | Средний |
| 4. API интеграции | COC API + YooKassa | 2-3 недели | Средний |
| 5. Обработчики | Message + Callback handlers | 4-5 недели | Высокий |
| 6. Продвинутые функции | Войны + Мониторинг | 3-4 недели | Высокий |
| 7. Премиум функции | Подписки + Премиум | 2-3 недели | Средний |
| 8. Финализация | Тестирование + Деплой | 2-3 недели | Средний |

**Общее время: 20-26 недель (5-6.5 месяцев)**

---

## 🚨 КРИТИЧЕСКИЕ МОМЕНТЫ ДЛЯ НЕЙРОСЕТИ

### ❗ ОБЯЗАТЕЛЬНО УЧЕСТЬ

1. **YooKassa НЕ ПРОБЛЕМА** - используется HTTP API, легко мигрируется
2. **ВСЕ 517 функций ДОЛЖНЫ быть перенесены**
3. **НИ ОДНА функция не должна быть пропущена**
4. **Точная совместимость с текущими данными**
5. **Все премиум функции должны работать идентично**
6. **Система подписок критически важна**
7. **Архивация войн и мониторинг зданий - ключевые функции**

### ✅ ГАРАНТИИ УСПЕХА

- **HTTP подход для YooKassa** - проверенное решение
- **Поэтапная миграция** - минимизация рисков
- **Полное тестирование** - каждой функции
- **Совместимость данных** - без потерь
- **Детальная документация** - каждого шага

**РЕЗУЛЬТАТ: Полностью функциональный бот на Go с улучшенной производительностью и стабильностью, без потери единой функции!**

