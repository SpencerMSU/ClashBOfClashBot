package models

import "time"

// User представляет пользователя бота
type User struct {
	ID           int64     `json:"id" db:"id"`
	TelegramID   int64     `json:"telegram_id" db:"telegram_id"`
	Username     string    `json:"username" db:"username"`
	FirstName    string    `json:"first_name" db:"first_name"`
	LastName     string    `json:"last_name" db:"last_name"`
	PlayerTag    string    `json:"player_tag" db:"player_tag"`
	ClanTag      string    `json:"clan_tag" db:"clan_tag"`
	IsActive     bool      `json:"is_active" db:"is_active"`
	JoinedAt     time.Time `json:"joined_at" db:"joined_at"`
	LastActivity time.Time `json:"last_activity" db:"last_activity"`
}

// UserProfile представляет профиль пользователя
type UserProfile struct {
	UserID             int64     `json:"user_id" db:"user_id"`
	PlayerTag          string    `json:"player_tag" db:"player_tag"`
	PlayerName         string    `json:"player_name" db:"player_name"`
	TownHallLevel      int       `json:"town_hall_level" db:"town_hall_level"`
	ExpLevel           int       `json:"exp_level" db:"exp_level"`
	Trophies           int       `json:"trophies" db:"trophies"`
	BestTrophies       int       `json:"best_trophies" db:"best_trophies"`
	WarStars           int       `json:"war_stars" db:"war_stars"`
	AttackWins         int       `json:"attack_wins" db:"attack_wins"`
	DefenseWins        int       `json:"defense_wins" db:"defense_wins"`
	ClanName           string    `json:"clan_name" db:"clan_name"`
	ClanTag            string    `json:"clan_tag" db:"clan_tag"`
	ClanRole           string    `json:"clan_role" db:"clan_role"`
	DonationsReceived  int       `json:"donations_received" db:"donations_received"`
	DonationsGiven     int       `json:"donations_given" db:"donations_given"`
	UpdatedAt          time.Time `json:"updated_at" db:"updated_at"`
}

// Subscription представляет подписку пользователя
type Subscription struct {
	ID               int64     `json:"id" db:"id"`
	TelegramID       int64     `json:"telegram_id" db:"telegram_id"`
	SubscriptionType string    `json:"subscription_type" db:"subscription_type"`
	StartDate        time.Time `json:"start_date" db:"start_date"`
	EndDate          time.Time `json:"end_date" db:"end_date"`
	IsActive         bool      `json:"is_active" db:"is_active"`
	PaymentID        string    `json:"payment_id" db:"payment_id"`
	Amount           float64   `json:"amount" db:"amount"`
	CreatedAt        time.Time `json:"created_at" db:"created_at"`
}