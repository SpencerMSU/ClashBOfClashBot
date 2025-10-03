package models

// User represents a bot user
type User struct {
	TelegramID int64  `json:"telegram_id"`
	PlayerTag  string `json:"player_tag"`
}

// NewUser creates a new User instance
func NewUser(telegramID int64, playerTag string) *User {
	return &User{
		TelegramID: telegramID,
		PlayerTag:  playerTag,
	}
}
