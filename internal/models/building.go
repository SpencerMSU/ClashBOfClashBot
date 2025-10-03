package models

import "time"

// BuildingSnapshot represents a snapshot of a player's building
type BuildingSnapshot struct {
	SnapshotID    int64     `json:"snapshot_id"`
	PlayerTag     string    `json:"player_tag"`
	BuildingType  string    `json:"building_type"`
	Level         int       `json:"level"`
	SnapshotTime  time.Time `json:"snapshot_time"`
	BuildingsData string    `json:"buildings_data"` // JSON string of all buildings
}

// BuildingUpgrade represents a building upgrade event
type BuildingUpgrade struct {
	PlayerTag    string    `json:"player_tag"`
	PlayerName   string    `json:"player_name"`
	BuildingType string    `json:"building_type"`
	OldLevel     int       `json:"old_level"`
	NewLevel     int       `json:"new_level"`
	UpgradeTime  time.Time `json:"upgrade_time"`
}

// BuildingTracker represents tracking information for building monitoring
type BuildingTracker struct {
	TrackerID            int64     `json:"tracker_id"`
	TelegramID           int64     `json:"telegram_id"`
	PlayerTag            string    `json:"player_tag"`
	LastCheck            time.Time `json:"last_check"`
	NotificationsEnabled bool      `json:"notifications_enabled"`
	IsActive             bool      `json:"is_active"`
	CreatedAt            time.Time `json:"created_at"`
}

// NewBuildingSnapshot creates a new BuildingSnapshot instance
func NewBuildingSnapshot(playerTag, buildingType string, level int) *BuildingSnapshot {
	return &BuildingSnapshot{
		SnapshotID:    0, // Set by database
		PlayerTag:     playerTag,
		BuildingType:  buildingType,
		Level:         level,
		SnapshotTime:  time.Now(),
		BuildingsData: "",
	}
}

// NewBuildingUpgrade creates a new BuildingUpgrade instance
func NewBuildingUpgrade(playerTag, playerName, buildingType string, oldLevel, newLevel int) *BuildingUpgrade {
	return &BuildingUpgrade{
		PlayerTag:    playerTag,
		PlayerName:   playerName,
		BuildingType: buildingType,
		OldLevel:     oldLevel,
		NewLevel:     newLevel,
		UpgradeTime:  time.Now(),
	}
}

// NewBuildingTracker creates a new BuildingTracker instance
func NewBuildingTracker(telegramID int64, playerTag string) *BuildingTracker {
	now := time.Now()
	return &BuildingTracker{
		TrackerID:            0, // Will be set by database
		TelegramID:           telegramID,
		PlayerTag:            playerTag,
		LastCheck:            now,
		NotificationsEnabled: true,
		IsActive:             true,
		CreatedAt:            now,
	}
}
