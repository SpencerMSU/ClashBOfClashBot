package models

import (
	"time"

	"gorm.io/gorm"
)

// SubscriptionType represents the type of subscription
type SubscriptionType string

const (
	// Premium subscriptions
	Premium1Month  SubscriptionType = "premium_1month"
	Premium3Months SubscriptionType = "premium_3months"
	Premium6Months SubscriptionType = "premium_6months"
	Premium1Year   SubscriptionType = "premium_1year"

	// PRO PLUS subscriptions
	ProPlus1Month    SubscriptionType = "proplus_1month"
	ProPlus3Months   SubscriptionType = "proplus_3months"
	ProPlus6Months   SubscriptionType = "proplus_6months"
	ProPlus1Year     SubscriptionType = "proplus_1year"
	ProPlusPermanent SubscriptionType = "proplus_permanent"

	// Legacy support
	Legacy1Month  SubscriptionType = "1month"
	Legacy3Months SubscriptionType = "3months"
	Legacy6Months SubscriptionType = "6months"
	Legacy1Year   SubscriptionType = "1year"
)

// SubscriptionStatus represents the status of subscription
type SubscriptionStatus string

const (
	SubscriptionActive   SubscriptionStatus = "active"
	SubscriptionExpired  SubscriptionStatus = "expired"
	SubscriptionCanceled SubscriptionStatus = "canceled"
)

// Subscription represents a user subscription - exact copy from Python models/subscription.py
type Subscription struct {
	ID                uint               `gorm:"primaryKey" json:"id"`
	TelegramID        int64              `gorm:"not null;index" json:"telegram_id"`
	SubscriptionType  SubscriptionType   `gorm:"size:50;not null" json:"subscription_type"`
	Status            SubscriptionStatus `gorm:"size:20;not null;default:'active'" json:"status"`
	StartDate         time.Time          `gorm:"not null" json:"start_date"`
	EndDate           time.Time          `gorm:"not null" json:"end_date"`
	PaymentID         string             `gorm:"size:255" json:"payment_id"`
	PaymentAmount     float64            `gorm:"type:decimal(10,2)" json:"payment_amount"`
	PaymentCurrency   string             `gorm:"size:10;default:'RUB'" json:"payment_currency"`
	IsAutoRenewal     bool               `gorm:"not null;default:false" json:"is_auto_renewal"`
	RenewalAttempts   int                `gorm:"not null;default:0" json:"renewal_attempts"`
	LastNotification  *time.Time         `json:"last_notification"`
	CreatedAt         time.Time          `json:"created_at"`
	UpdatedAt         time.Time          `json:"updated_at"`
	DeletedAt         gorm.DeletedAt     `gorm:"index" json:"deleted_at"`
}

// TableName returns the table name for the Subscription model
func (Subscription) TableName() string {
	return "subscriptions"
}

// BeforeCreate hook to set creation timestamp
func (s *Subscription) BeforeCreate(tx *gorm.DB) error {
	now := time.Now()
	if s.CreatedAt.IsZero() {
		s.CreatedAt = now
	}
	if s.StartDate.IsZero() {
		s.StartDate = now
	}
	return nil
}

// BeforeUpdate hook to set update timestamp
func (s *Subscription) BeforeUpdate(tx *gorm.DB) error {
	s.UpdatedAt = time.Now()
	return nil
}

// IsActive checks if subscription is currently active - exact copy from Python
func (s *Subscription) IsActive() bool {
	now := time.Now()
	return s.Status == SubscriptionActive && 
		   (now.After(s.StartDate) || now.Equal(s.StartDate)) && 
		   now.Before(s.EndDate)
}

// IsExpired checks if subscription has expired - exact copy from Python
func (s *Subscription) IsExpired() bool {
	now := time.Now()
	return now.After(s.EndDate) || s.Status == SubscriptionExpired
}

// DaysUntilExpiry returns days until subscription expires - exact copy from Python
func (s *Subscription) DaysUntilExpiry() int {
	if s.IsExpired() {
		return 0
	}
	
	now := time.Now()
	duration := s.EndDate.Sub(now)
	days := int(duration.Hours() / 24)
	
	if days < 0 {
		return 0
	}
	return days
}

// IsExpiringSoon checks if subscription expires within 7 days
func (s *Subscription) IsExpiringSoon() bool {
	return s.DaysUntilExpiry() <= 7 && s.DaysUntilExpiry() > 0
}

// Cancel marks the subscription as canceled
func (s *Subscription) Cancel() {
	s.Status = SubscriptionCanceled
}

// Expire marks the subscription as expired
func (s *Subscription) Expire() {
	s.Status = SubscriptionExpired
}

// Extend extends the subscription by the given duration
func (s *Subscription) Extend(duration time.Duration) {
	if s.IsActive() {
		s.EndDate = s.EndDate.Add(duration)
	} else {
		now := time.Now()
		s.StartDate = now
		s.EndDate = now.Add(duration)
		s.Status = SubscriptionActive
	}
}

// IsPremium checks if this is a premium subscription
func (s *Subscription) IsPremium() bool {
	switch s.SubscriptionType {
	case Premium1Month, Premium3Months, Premium6Months, Premium1Year,
		 Legacy1Month, Legacy3Months, Legacy6Months, Legacy1Year:
		return true
	default:
		return false
	}
}

// IsProPlus checks if this is a PRO PLUS subscription
func (s *Subscription) IsProPlus() bool {
	switch s.SubscriptionType {
	case ProPlus1Month, ProPlus3Months, ProPlus6Months, ProPlus1Year, ProPlusPermanent:
		return true
	default:
		return false
	}
}

// IsPermanent checks if this is a permanent subscription
func (s *Subscription) IsPermanent() bool {
	return s.SubscriptionType == ProPlusPermanent
}

// GetSubscriptionLevel returns the subscription level (0=none, 1=premium, 2=proplus)
func (s *Subscription) GetSubscriptionLevel() int {
	if !s.IsActive() {
		return 0
	}
	
	if s.IsProPlus() {
		return 2
	}
	
	if s.IsPremium() {
		return 1
	}
	
	return 0
}