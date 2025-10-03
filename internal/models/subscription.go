package models

import "time"

// Subscription represents a user's subscription
type Subscription struct {
	TelegramID       int64     `json:"telegram_id"`
	SubscriptionType string    `json:"subscription_type"` // "premium_1month", "proplus_1month", etc.
	StartDate        time.Time `json:"start_date"`
	EndDate          time.Time `json:"end_date"`
	IsActive         bool      `json:"is_active"`
	PaymentID        string    `json:"payment_id"`
	Amount           float64   `json:"amount"`
	Currency         string    `json:"currency"`
	CreatedAt        time.Time `json:"created_at"`
	UpdatedAt        time.Time `json:"updated_at"`
}

// NewSubscription creates a new Subscription instance
func NewSubscription(telegramID int64, subscriptionType string, startDate, endDate time.Time, isActive bool, paymentID string, amount float64, currency string) *Subscription {
	now := time.Now()
	return &Subscription{
		TelegramID:       telegramID,
		SubscriptionType: subscriptionType,
		StartDate:        startDate,
		EndDate:          endDate,
		IsActive:         isActive,
		PaymentID:        paymentID,
		Amount:           amount,
		Currency:         currency,
		CreatedAt:        now,
		UpdatedAt:        now,
	}
}

// IsExpired checks if the subscription has expired
func (s *Subscription) IsExpired() bool {
	return time.Now().After(s.EndDate)
}

// DaysRemaining returns the number of days remaining in the subscription
func (s *Subscription) DaysRemaining() int {
	if s.IsExpired() {
		return 0
	}
	duration := time.Until(s.EndDate)
	return int(duration.Hours() / 24)
}

// IsPremium checks if subscription is premium type
func (s *Subscription) IsPremium() bool {
	switch s.SubscriptionType {
	case "premium_1month", "premium_3months", "premium_6months", "premium_1year",
		"1month", "3months", "6months", "1year": // legacy support
		return true
	}
	return false
}

// IsProPlus checks if subscription is PRO PLUS type
func (s *Subscription) IsProPlus() bool {
	switch s.SubscriptionType {
	case "proplus_1month", "proplus_3months", "proplus_6months", "proplus_1year", "proplus_permanent":
		return true
	}
	return false
}
