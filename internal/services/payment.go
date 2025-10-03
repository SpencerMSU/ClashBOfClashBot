// Package services предоставляет бизнес-логику и сервисы бота
package services

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/google/uuid"
)

// YooKassaService - сервис для работы с платежами через YooKassa
type YooKassaService struct {
	client      *http.Client
	shopID      string
	secretKey   string
	botUsername string
	apiURL      string
}

// Константы для YooKassa
const (
	TestShopID    = "1164328"
	TestSecretKey = "live_FVe4M7peyvzGPRZrM4UJq4pF6soCfuv4VZEgntsPmhs"
	APIURL        = "https://api.yookassa.ru/v3"
)

// SubscriptionPrices - цены подписок в рублях
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

// SubscriptionNames - названия подписок
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

// AmountInfo - информация о сумме
type AmountInfo struct {
	Value    string `json:"value"`
	Currency string `json:"currency"`
}

// Confirmation - информация о подтверждении платежа
type Confirmation struct {
	Type      string `json:"type"`
	ReturnURL string `json:"return_url"`
}

// Metadata - метаданные платежа
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

// RefundRequest - структура запроса возврата
type RefundRequest struct {
	Amount      AmountInfo `json:"amount"`
	PaymentID   string     `json:"payment_id"`
	Description string     `json:"description,omitempty"`
}

// RefundResponse - структура ответа на возврат
type RefundResponse struct {
	ID          string     `json:"id"`
	Status      string     `json:"status"`
	Amount      AmountInfo `json:"amount"`
	PaymentID   string     `json:"payment_id"`
	Description string     `json:"description"`
	CreatedAt   time.Time  `json:"created_at"`
}

// NewYooKassaService создает новый экземпляр YooKassaService
func NewYooKassaService(shopID, secretKey, botUsername string) *YooKassaService {
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
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
		shopID:      shopID,
		secretKey:   secretKey,
		botUsername: botUsername,
		apiURL:      APIURL,
	}
}

// getAuthHeaders получает заголовки авторизации для YooKassa API
func (y *YooKassaService) getAuthHeaders() map[string]string {
	credentials := fmt.Sprintf("%s:%s", y.shopID, y.secretKey)
	encodedCredentials := base64.StdEncoding.EncodeToString([]byte(credentials))

	return map[string]string{
		"Authorization":  fmt.Sprintf("Basic %s", encodedCredentials),
		"Content-Type":   "application/json",
		"Idempotence-Key": uuid.New().String(),
	}
}

// CreatePayment создает платеж в YooKassa
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

	// Формируем данные запроса
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

	// Преобразуем в JSON
	jsonData, err := json.Marshal(paymentData)
	if err != nil {
		return nil, fmt.Errorf("ошибка при сериализации данных платежа: %w", err)
	}

	// Создаем HTTP запрос
	req, err := http.NewRequest("POST", fmt.Sprintf("%s/payments", y.apiURL), bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("ошибка при создании запроса: %w", err)
	}

	// Устанавливаем заголовки
	for key, value := range y.getAuthHeaders() {
		req.Header.Set(key, value)
	}

	// Выполняем запрос
	resp, err := y.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("ошибка при выполнении запроса: %w", err)
	}
	defer resp.Body.Close()

	// Проверяем статус ответа
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("ошибка создания платежа: статус %d", resp.StatusCode)
	}

	// Парсим ответ
	var payment PaymentResponse
	if err := json.NewDecoder(resp.Body).Decode(&payment); err != nil {
		return nil, fmt.Errorf("ошибка при парсинге ответа: %w", err)
	}

	log.Printf("Платеж создан: %s", payment.ID)
	return &payment, nil
}

// CheckPaymentStatus проверяет статус платежа
func (y *YooKassaService) CheckPaymentStatus(paymentID string) (*PaymentResponse, error) {
	// Создаем HTTP запрос
	req, err := http.NewRequest("GET", fmt.Sprintf("%s/payments/%s", y.apiURL, paymentID), nil)
	if err != nil {
		return nil, fmt.Errorf("ошибка при создании запроса: %w", err)
	}

	// Устанавливаем заголовки
	for key, value := range y.getAuthHeaders() {
		req.Header.Set(key, value)
	}

	// Выполняем запрос
	resp, err := y.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("ошибка при выполнении запроса: %w", err)
	}
	defer resp.Body.Close()

	// Проверяем статус ответа
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("ошибка проверки платежа: статус %d", resp.StatusCode)
	}

	// Парсим ответ
	var payment PaymentResponse
	if err := json.NewDecoder(resp.Body).Decode(&payment); err != nil {
		return nil, fmt.Errorf("ошибка при парсинге ответа: %w", err)
	}

	return &payment, nil
}

// GetSubscriptionDuration возвращает длительность подписки
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

// GetSubscriptionPrice возвращает цену подписки
func (y *YooKassaService) GetSubscriptionPrice(subscriptionType string) float64 {
	if price, exists := SubscriptionPrices[subscriptionType]; exists {
		return price
	}
	return 0.0
}

// GetSubscriptionName возвращает название подписки
func (y *YooKassaService) GetSubscriptionName(subscriptionType string) string {
	if name, exists := SubscriptionNames[subscriptionType]; exists {
		return name
	}
	return "Неизвестная подписка"
}

// CreateRefund создает возврат платежа
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

	// Преобразуем в JSON
	jsonData, err := json.Marshal(refundData)
	if err != nil {
		return nil, fmt.Errorf("ошибка при сериализации данных возврата: %w", err)
	}

	// Создаем HTTP запрос
	req, err := http.NewRequest("POST", fmt.Sprintf("%s/refunds", y.apiURL), bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("ошибка при создании запроса: %w", err)
	}

	// Устанавливаем заголовки
	for key, value := range y.getAuthHeaders() {
		req.Header.Set(key, value)
	}

	// Выполняем запрос
	resp, err := y.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("ошибка при выполнении запроса: %w", err)
	}
	defer resp.Body.Close()

	// Проверяем статус ответа
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("ошибка создания возврата: статус %d", resp.StatusCode)
	}

	// Парсим ответ
	var refund RefundResponse
	if err := json.NewDecoder(resp.Body).Decode(&refund); err != nil {
		return nil, fmt.Errorf("ошибка при парсинге ответа: %w", err)
	}

	log.Printf("Возврат создан: %s", refund.ID)
	return &refund, nil
}

// Close закрывает HTTP клиент (для совместимости с Python версией)
func (y *YooKassaService) Close() {
	// В Go нет необходимости в явном закрытии HTTP клиента
	// Но для совместимости оставляем метод
}
