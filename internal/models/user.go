package models

import (
	"time"

	"gorm.io/gorm"
)

// User represents a Telegram user - exact copy from Python models/user.py
type User struct {
	ID          uint           `gorm:"primaryKey" json:"id"`
	TelegramID  int64          `gorm:"uniqueIndex;not null" json:"telegram_id"`
	Username    string         `gorm:"size:255" json:"username"`
	FirstName   string         `gorm:"size:255" json:"first_name"`
	LastName    string         `gorm:"size:255" json:"last_name"`
	PlayerTag   string         `gorm:"size:50" json:"player_tag"`
	IsBot       bool           `gorm:"not null;default:false" json:"is_bot"`
	LanguageCode string        `gorm:"size:10" json:"language_code"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	DeletedAt   gorm.DeletedAt `gorm:"index" json:"deleted_at"`
}

// TableName returns the table name for the User model
func (User) TableName() string {
	return "users"
}

// BeforeCreate hook to set creation timestamp
func (u *User) BeforeCreate(tx *gorm.DB) error {
	if u.CreatedAt.IsZero() {
		u.CreatedAt = time.Now()
	}
	return nil
}

// BeforeUpdate hook to set update timestamp
func (u *User) BeforeUpdate(tx *gorm.DB) error {
	u.UpdatedAt = time.Now()
	return nil
}

// IsLinked checks if user has linked a player
func (u *User) IsLinked() bool {
	return u.PlayerTag != ""
}

// FullName returns the user's full name
func (u *User) FullName() string {
	if u.LastName != "" {
		return u.FirstName + " " + u.LastName
	}
	return u.FirstName
}

// DisplayName returns the best available name for display
func (u *User) DisplayName() string {
	if u.Username != "" {
		return "@" + u.Username
	}
	if u.FirstName != "" {
		return u.FullName()
	}
	return "Пользователь"
}