package models

import "time"

// UserProfile represents a user profile for multi-profile premium users
type UserProfile struct {
	ID          int64     `json:"id"`
	TelegramID  int64     `json:"telegram_id"`
	PlayerTag   string    `json:"player_tag"`
	ProfileName *string   `json:"profile_name,omitempty"`
	IsPrimary   bool      `json:"is_primary"`
	CreatedAt   time.Time `json:"created_at"`
}

// NewUserProfile creates a new UserProfile instance
func NewUserProfile(telegramID int64, playerTag string) *UserProfile {
	return &UserProfile{
		TelegramID: telegramID,
		PlayerTag:  playerTag,
		IsPrimary:  false,
		CreatedAt:  time.Now(),
	}
}
