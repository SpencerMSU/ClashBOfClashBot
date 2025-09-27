package services

import (
	"encoding/base64"
	"fmt"
	"strings"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

// YooKassaService provides payment processing via YooKassa API - exact copy from Python payment_service.py
type YooKassaService struct {
	client      *resty.Client
	shopID      string
	secretKey   string
	botUsername string
	logger      *logrus.Logger
}

// Constants from Python payment_service.py
const (
	TestShopID    = "1164328"
	TestSecretKey = "live_FVe4M7peyvzGPRZrM4UJq4pF6soCfuv4VZEgntsPmhs"
	APIURL        = "https://api.yookassa.ru/v3"
)

// SubscriptionPrices - exact copy from Python SUBSCRIPTION_PRICES
var SubscriptionPrices = map[string]float64{
	// Premium subscriptions
	"premium_1month":  49.00,
	"premium_3months": 119.00,
	"premium_6months": 199.00,
	"premium_1year":   349.00,
	
	// PRO PLUS subscriptions
	"proplus_1month":    99.00,
	"proplus_3months":   249.00,
	"proplus_6months":   449.00,
	"proplus_1year":     799.00,
	"proplus_permanent": 1999.00,
	
	// Legacy support
	"1month":  49.00,
	"3months": 119.00,
	"6months": 199.00,
	"1year":   349.00,
}

// SubscriptionNames - exact copy from Python SUBSCRIPTION_NAMES
var SubscriptionNames = map[string]string{
	// Premium subscriptions
	"premium_1month":  "ClashBot Премиум подписка на 1 месяц",
	"premium_3months": "ClashBot Премиум подписка на 3 месяца",
	"premium_6months": "ClashBot Премиум подписка на 6 месяцев",
	"premium_1year":   "ClashBot Премиум подписка на 1 год",
	
	// PRO PLUS subscriptions
	"proplus_1month":    "ClashBot ПРО ПЛЮС подписка на 1 месяц",
	"proplus_3months":   "ClashBot ПРО ПЛЮС подписка на 3 месяца",
	"proplus_6months":   "ClashBot ПРО ПЛЮС подписка на 6 месяцев",
	"proplus_1year":     "ClashBot ПРО ПЛЮС подписка на 1 год",
	"proplus_permanent": "ClashBot ПРО ПЛЮС подписка (Вечная)",
	
	// Legacy support
	"1month":  "ClashBot Премиум подписка на 1 месяц",
	"3months": "ClashBot Премиум подписка на 3 месяца",
	"6months": "ClashBot Премиум подписка на 6 месяцев",
	"1year":   "ClashBot Премиум подписка на 1 год",
}

// Payment request structures - exact copy from Python
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

// Payment response structures - exact copy from Python
type PaymentResponse struct {
	ID           string       `json:"id"`
	Status       string       `json:"status"`
	Amount       AmountInfo   `json:"amount"`
	Description  string       `json:"description"`
	Confirmation Confirmation `json:"confirmation"`
	CreatedAt    time.Time    `json:"created_at"`
	Metadata     Metadata     `json:"metadata"`
}

// Refund structures
type RefundRequest struct {
	Amount      AmountInfo `json:"amount"`
	PaymentID   string     `json:"payment_id"`
	Description string     `json:"description,omitempty"`
}

type RefundResponse struct {
	ID          string     `json:"id"`
	Status      string     `json:"status"`
	Amount      AmountInfo `json:"amount"`
	PaymentID   string     `json:"payment_id"`
	Description string     `json:"description"`
	CreatedAt   time.Time  `json:"created_at"`
}

// NewYooKassaService creates a new YooKassa service instance - exact copy from Python __init__
func NewYooKassaService(shopID, secretKey, botUsername string) *YooKassaService {
	client := resty.New()
	client.SetTimeout(30 * time.Second)

	// Use test credentials as fallback - exact copy from Python
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
		logger:      logrus.StandardLogger(),
	}
}

// getAuthHeaders returns authorization headers - exact copy from Python _get_auth_headers
func (y *YooKassaService) getAuthHeaders() map[string]string {
	credentials := fmt.Sprintf("%s:%s", y.shopID, y.secretKey)
	encodedCredentials := base64.StdEncoding.EncodeToString([]byte(credentials))

	return map[string]string{
		"Authorization":  fmt.Sprintf("Basic %s", encodedCredentials),
		"Content-Type":   "application/json",
		"Idempotence-Key": uuid.New().String(),
	}
}

// CreatePayment creates a new payment - exact copy from Python create_payment
func (y *YooKassaService) CreatePayment(telegramID int64, subscriptionType string, returnURL string) (*PaymentResponse, error) {
	// Check subscription type
	amount, exists := SubscriptionPrices[subscriptionType]
	if !exists {
		return nil, fmt.Errorf("неизвестный тип подписки: %s", subscriptionType)
	}

	description, exists := SubscriptionNames[subscriptionType]
	if !exists {
		description = "Неизвестная подписка"
	}

	// Create return URL if not provided
	if returnURL == "" {
		returnURL = fmt.Sprintf("https://t.me/%s", y.botUsername)
	}

	// Prepare payment data - exact copy from Python
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

	// Make HTTP request - identical to Python
	var response PaymentResponse
	resp, err := y.client.R().
		SetHeaders(y.getAuthHeaders()).
		SetBody(paymentData).
		SetResult(&response).
		Post(APIURL + "/payments")

	if err != nil {
		y.logger.Errorf("Error creating payment: %v", err)
		return nil, fmt.Errorf("ошибка при создании платежа: %w", err)
	}

	if resp.StatusCode() != 200 {
		y.logger.Errorf("YooKassa API error: %d - %s", resp.StatusCode(), resp.String())
		return nil, fmt.Errorf("ошибка создания платежа: %d - %s", resp.StatusCode(), resp.String())
	}

	y.logger.Infof("Payment created successfully: %s for user %d", response.ID, telegramID)
	return &response, nil
}

// CheckPaymentStatus checks payment status - exact copy from Python check_payment_status
func (y *YooKassaService) CheckPaymentStatus(paymentID string) (*PaymentResponse, error) {
	var response PaymentResponse
	resp, err := y.client.R().
		SetHeaders(y.getAuthHeaders()).
		SetResult(&response).
		Get(fmt.Sprintf("%s/payments/%s", APIURL, paymentID))

	if err != nil {
		y.logger.Errorf("Error checking payment status: %v", err)
		return nil, fmt.Errorf("ошибка при проверке платежа: %w", err)
	}

	if resp.StatusCode() != 200 {
		y.logger.Errorf("YooKassa API error: %d - %s", resp.StatusCode(), resp.String())
		return nil, fmt.Errorf("ошибка проверки платежа: %d - %s", resp.StatusCode(), resp.String())
	}

	return &response, nil
}

// GetSubscriptionDuration returns subscription duration - exact copy from Python get_subscription_duration
func (y *YooKassaService) GetSubscriptionDuration(subscriptionType string) time.Duration {
	if strings.Contains(subscriptionType, "permanent") {
		return time.Hour * 24 * 36500 // 100 years for permanent subscription
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
		// Fallback for legacy formats
		durations := map[string]time.Duration{
			"1month":  time.Hour * 24 * 30,
			"3months": time.Hour * 24 * 90,
			"6months": time.Hour * 24 * 180,
			"1year":   time.Hour * 24 * 365,
		}
		if duration, exists := durations[subscriptionType]; exists {
			return duration
		}
		return time.Hour * 24 * 30 // Default to 30 days
	}
}

// GetSubscriptionPrice returns subscription price - exact copy from Python get_subscription_price
func (y *YooKassaService) GetSubscriptionPrice(subscriptionType string) float64 {
	if price, exists := SubscriptionPrices[subscriptionType]; exists {
		return price
	}
	return 0.0
}

// GetSubscriptionName returns subscription name - exact copy from Python get_subscription_name
func (y *YooKassaService) GetSubscriptionName(subscriptionType string) string {
	if name, exists := SubscriptionNames[subscriptionType]; exists {
		return name
	}
	return "Неизвестная подписка"
}

// CreateRefund creates a refund - exact copy from Python create_refund
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
		y.logger.Errorf("Error creating refund: %v", err)
		return nil, fmt.Errorf("ошибка при создании возврата: %w", err)
	}

	if resp.StatusCode() != 200 {
		y.logger.Errorf("YooKassa API error: %d - %s", resp.StatusCode(), resp.String())
		return nil, fmt.Errorf("ошибка создания возврата: %d - %s", resp.StatusCode(), resp.String())
	}

	y.logger.Infof("Refund created successfully: %s for payment %s", response.ID, paymentID)
	return &response, nil
}

// ProcessRefundNotification processes refund notifications
func (y *YooKassaService) ProcessRefundNotification(notification map[string]interface{}) error {
	// Extract notification data
	eventType, _ := notification["event"].(string)
	object, _ := notification["object"].(map[string]interface{})

	if eventType == "refund.succeeded" {
		refundID, _ := object["id"].(string)
		paymentID, _ := object["payment_id"].(string)
		
		y.logger.Infof("Refund succeeded: %s for payment %s", refundID, paymentID)
		// Additional processing can be added here
	}

	return nil
}

// IsValidSubscriptionType checks if subscription type is valid
func (y *YooKassaService) IsValidSubscriptionType(subscriptionType string) bool {
	_, exists := SubscriptionPrices[subscriptionType]
	return exists
}

// GetAllSubscriptionTypes returns all available subscription types
func (y *YooKassaService) GetAllSubscriptionTypes() []string {
	var types []string
	for subscriptionType := range SubscriptionPrices {
		types = append(types, subscriptionType)
	}
	return types
}

// Close closes the payment service - exact copy from Python close
func (y *YooKassaService) Close() {
	// No explicit cleanup needed for HTTP client in Go
	y.logger.Info("YooKassa service closed")
}