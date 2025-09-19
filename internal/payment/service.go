package payment

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"strconv"
	"time"
)

// PaymentService обертка для Python YooKassa API
type PaymentService struct {
	botUsername string
	pythonPath  string
	scriptPath  string
}

// PaymentData представляет данные платежа
type PaymentData struct {
	ID           string                 `json:"id"`
	Status       string                 `json:"status"`
	Amount       map[string]interface{} `json:"amount"`
	Confirmation map[string]interface{} `json:"confirmation"`
	Metadata     map[string]string      `json:"metadata"`
}

// PaymentResponse представляет ответ от Python скрипта
type PaymentResponse struct {
	Error string      `json:"error,omitempty"`
	Data  PaymentData `json:",inline"`
}

// PriceResponse представляет ответ с ценой
type PriceResponse struct {
	Error string  `json:"error,omitempty"`
	Price float64 `json:"price"`
}

// NameResponse представляет ответ с названием
type NameResponse struct {
	Error string `json:"error,omitempty"`
	Name  string `json:"name"`
}

// New создает новый экземпляр PaymentService
func New(botUsername, pythonPath, scriptPath string) *PaymentService {
	if pythonPath == "" {
		pythonPath = "python3"
	}
	if scriptPath == "" {
		scriptPath = "./payment_bridge.py"
	}
	
	return &PaymentService{
		botUsername: botUsername,
		pythonPath:  pythonPath,
		scriptPath:  scriptPath,
	}
}

// CreatePayment создает платеж через Python YooKassa API
func (p *PaymentService) CreatePayment(telegramID int64, subscriptionType, returnURL string) (*PaymentData, error) {
	args := []string{
		p.scriptPath,
		"create_payment",
		strconv.FormatInt(telegramID, 10),
		subscriptionType,
	}
	
	if returnURL != "" {
		args = append(args, returnURL)
	}
	
	cmd := exec.Command(p.pythonPath, args...)
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("ошибка выполнения Python скрипта: %v", err)
	}
	
	var response PaymentResponse
	if err := json.Unmarshal(output, &response); err != nil {
		return nil, fmt.Errorf("ошибка парсинга ответа: %v", err)
	}
	
	if response.Error != "" {
		return nil, fmt.Errorf("ошибка в Python скрипте: %s", response.Error)
	}
	
	return &response.Data, nil
}

// CheckPaymentStatus проверяет статус платежа
func (p *PaymentService) CheckPaymentStatus(paymentID string) (*PaymentData, error) {
	cmd := exec.Command(p.pythonPath, p.scriptPath, "check_payment", paymentID)
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("ошибка выполнения Python скрипта: %v", err)
	}
	
	var response PaymentResponse
	if err := json.Unmarshal(output, &response); err != nil {
		return nil, fmt.Errorf("ошибка парсинга ответа: %v", err)
	}
	
	if response.Error != "" {
		return nil, fmt.Errorf("ошибка в Python скрипте: %s", response.Error)
	}
	
	return &response.Data, nil
}

// GetSubscriptionPrice получает цену подписки
func (p *PaymentService) GetSubscriptionPrice(subscriptionType string) (float64, error) {
	cmd := exec.Command(p.pythonPath, p.scriptPath, "get_price", subscriptionType)
	output, err := cmd.Output()
	if err != nil {
		return 0, fmt.Errorf("ошибка выполнения Python скрипта: %v", err)
	}
	
	var response PriceResponse
	if err := json.Unmarshal(output, &response); err != nil {
		return 0, fmt.Errorf("ошибка парсинга ответа: %v", err)
	}
	
	if response.Error != "" {
		return 0, fmt.Errorf("ошибка в Python скрипте: %s", response.Error)
	}
	
	return response.Price, nil
}

// GetSubscriptionName получает название подписки
func (p *PaymentService) GetSubscriptionName(subscriptionType string) (string, error) {
	cmd := exec.Command(p.pythonPath, p.scriptPath, "get_name", subscriptionType)
	output, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("ошибка выполнения Python скрипта: %v", err)
	}
	
	var response NameResponse
	if err := json.Unmarshal(output, &response); err != nil {
		return "", fmt.Errorf("ошибка парсинга ответа: %v", err)
	}
	
	if response.Error != "" {
		return "", fmt.Errorf("ошибка в Python скрипте: %s", response.Error)
	}
	
	return response.Name, nil
}

// GetSubscriptionDuration возвращает длительность подписки
func (p *PaymentService) GetSubscriptionDuration(subscriptionType string) time.Duration {
	if subscriptionType == "permanent" {
		return time.Hour * 24 * 365 * 100 // 100 лет для вечной подписки
	}
	
	switch {
	case contains(subscriptionType, "1month"):
		return time.Hour * 24 * 30
	case contains(subscriptionType, "3months"):
		return time.Hour * 24 * 90
	case contains(subscriptionType, "6months"):
		return time.Hour * 24 * 180
	case contains(subscriptionType, "1year"):
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
		return time.Hour * 24 * 30 // По умолчанию 1 месяц
	}
}

// contains проверяет, содержит ли строка подстроку
func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || 
		(len(s) > len(substr) && s[len(s)-len(substr):] == substr))
}