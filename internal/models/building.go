package models

import "time"

// BuildingSnapshot represents a snapshot of a player's building
type BuildingSnapshot struct {
	PlayerTag    string    `json:"player_tag"`
	BuildingType string    `json:"building_type"`
	Level        int       `json:"level"`
	SnapshotTime time.Time `json:"snapshot_time"`
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
	TelegramID           int64     `json:"telegram_id"`
	PlayerTag            string    `json:"player_tag"`
	LastCheck            time.Time `json:"last_check"`
	NotificationsEnabled bool      `json:"notifications_enabled"`
}

// NewBuildingSnapshot creates a new BuildingSnapshot instance
func NewBuildingSnapshot(playerTag, buildingType string, level int) *BuildingSnapshot {
	return &BuildingSnapshot{
		PlayerTag:    playerTag,
		BuildingType: buildingType,
		Level:        level,
		SnapshotTime: time.Now(),
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
	return &BuildingTracker{
		TelegramID:           telegramID,
		PlayerTag:            playerTag,
		LastCheck:            time.Now(),
		NotificationsEnabled: true,
	}
}
