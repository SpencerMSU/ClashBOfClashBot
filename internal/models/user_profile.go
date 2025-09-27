package models

import (
	"time"

	"gorm.io/gorm"
)

// UserProfile represents a user's player profile - exact copy from Python models/user_profile.py
type UserProfile struct {
	ID          uint           `gorm:"primaryKey" json:"id"`
	TelegramID  int64          `gorm:"not null;index" json:"telegram_id"`
	PlayerTag   string         `gorm:"size:50;not null" json:"player_tag"`
	PlayerName  string         `gorm:"size:255" json:"player_name"`
	IsPrimary   bool           `gorm:"not null;default:false" json:"is_primary"`
	IsActive    bool           `gorm:"not null;default:true" json:"is_active"`
	AddedAt     time.Time      `json:"added_at"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	DeletedAt   gorm.DeletedAt `gorm:"index" json:"deleted_at"`
}

// TableName returns the table name for the UserProfile model
func (UserProfile) TableName() string {
	return "user_profiles"
}

// BeforeCreate hook to set creation timestamp
func (up *UserProfile) BeforeCreate(tx *gorm.DB) error {
	now := time.Now()
	if up.CreatedAt.IsZero() {
		up.CreatedAt = now
	}
	if up.AddedAt.IsZero() {
		up.AddedAt = now
	}
	return nil
}

// BeforeUpdate hook to set update timestamp
func (up *UserProfile) BeforeUpdate(tx *gorm.DB) error {
	up.UpdatedAt = time.Now()
	return nil
}

// Activate sets the profile as active
func (up *UserProfile) Activate() {
	up.IsActive = true
}

// Deactivate sets the profile as inactive
func (up *UserProfile) Deactivate() {
	up.IsActive = false
}

// SetAsPrimary sets this profile as the primary profile
func (up *UserProfile) SetAsPrimary() {
	up.IsPrimary = true
}

// UnsetAsPrimary removes the primary status from this profile
func (up *UserProfile) UnsetAsPrimary() {
	up.IsPrimary = false
}

// IsValidPlayerTag checks if the player tag is valid format
func (up *UserProfile) IsValidPlayerTag() bool {
	if len(up.PlayerTag) < 3 {
		return false
	}
	// Player tags start with # in Clash of Clans
	if up.PlayerTag[0] != '#' {
		return false
	}
	return true
}