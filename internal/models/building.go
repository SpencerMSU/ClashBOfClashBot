package models

import "time"

// Building представляет здание в игре
type Building struct {
	Name        string `json:"name"`
	Level       int    `json:"level"`
	MaxLevel    int    `json:"max_level"`
	Village     string `json:"village"` // "home" или "builderBase"
}

// BuildingSnapshot представляет снимок зданий игрока
type BuildingSnapshot struct {
	ID          int64     `json:"id" db:"id"`
	PlayerTag   string    `json:"player_tag" db:"player_tag"`
	PlayerName  string    `json:"player_name" db:"player_name"`
	Buildings   string    `json:"buildings" db:"buildings"` // JSON строка с данными о зданиях
	SnapshotDate time.Time `json:"snapshot_date" db:"snapshot_date"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
}

// BuildingTracker представляет отслеживание зданий игрока
type BuildingTracker struct {
	ID               int64     `json:"id" db:"id"`
	TelegramID       int64     `json:"telegram_id" db:"telegram_id"`
	PlayerTag        string    `json:"player_tag" db:"player_tag"`
	PlayerName       string    `json:"player_name" db:"player_name"`
	IsActive         bool      `json:"is_active" db:"is_active"`
	LastCheck        time.Time `json:"last_check" db:"last_check"`
	NotificationsSent int      `json:"notifications_sent" db:"notifications_sent"`
	CreatedAt        time.Time `json:"created_at" db:"created_at"`
	UpdatedAt        time.Time `json:"updated_at" db:"updated_at"`
}

// BuildingUpgrade представляет улучшение здания
type BuildingUpgrade struct {
	ID             int64     `json:"id" db:"id"`
	PlayerTag      string    `json:"player_tag" db:"player_tag"`
	PlayerName     string    `json:"player_name" db:"player_name"`
	BuildingName   string    `json:"building_name" db:"building_name"`
	OldLevel       int       `json:"old_level" db:"old_level"`
	NewLevel       int       `json:"new_level" db:"new_level"`
	Village        string    `json:"village" db:"village"`
	UpgradeDate    time.Time `json:"upgrade_date" db:"upgrade_date"`
	IsNotified     bool      `json:"is_notified" db:"is_notified"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
}