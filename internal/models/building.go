package models

import (
	"time"

	"gorm.io/gorm"
)

// BuildingSnapshot represents a snapshot of player's buildings - exact copy from Python models/building.py
type BuildingSnapshot struct {
	ID         uint           `gorm:"primaryKey" json:"id"`
	TelegramID int64          `gorm:"not null;index" json:"telegram_id"`
	PlayerTag  string         `gorm:"size:50;not null;index" json:"player_tag"`
	PlayerName string         `gorm:"size:255" json:"player_name"`
	
	// Town Hall and other main buildings
	TownHallLevel        int       `gorm:"not null;default:0" json:"town_hall_level"`
	BuilderHallLevel     int       `gorm:"not null;default:0" json:"builder_hall_level"`
	
	// Defense buildings
	CannonLevel          int       `gorm:"not null;default:0" json:"cannon_level"`
	ArcherTowerLevel     int       `gorm:"not null;default:0" json:"archer_tower_level"`
	MortarLevel          int       `gorm:"not null;default:0" json:"mortar_level"`
	AirDefenseLevel      int       `gorm:"not null;default:0" json:"air_defense_level"`
	WizardTowerLevel     int       `gorm:"not null;default:0" json:"wizard_tower_level"`
	AirSweeperLevel      int       `gorm:"not null;default:0" json:"air_sweeper_level"`
	HiddenTeslaLevel     int       `gorm:"not null;default:0" json:"hidden_tesla_level"`
	BombTowerLevel       int       `gorm:"not null;default:0" json:"bomb_tower_level"`
	XBowLevel            int       `gorm:"not null;default:0" json:"x_bow_level"`
	InfernoTowerLevel    int       `gorm:"not null;default:0" json:"inferno_tower_level"`
	EagleArtilleryLevel  int       `gorm:"not null;default:0" json:"eagle_artillery_level"`
	ScattershotLevel     int       `gorm:"not null;default:0" json:"scattershot_level"`
	
	// Resource buildings
	GoldMineLevel        int       `gorm:"not null;default:0" json:"gold_mine_level"`
	ElixirCollectorLevel int       `gorm:"not null;default:0" json:"elixir_collector_level"`
	DarkElixirDrillLevel int       `gorm:"not null;default:0" json:"dark_elixir_drill_level"`
	
	// Army buildings
	ArmyCampLevel        int       `gorm:"not null;default:0" json:"army_camp_level"`
	BarracksLevel        int       `gorm:"not null;default:0" json:"barracks_level"`
	DarkBarracksLevel    int       `gorm:"not null;default:0" json:"dark_barracks_level"`
	LaboratoryLevel      int       `gorm:"not null;default:0" json:"laboratory_level"`
	SpellFactoryLevel    int       `gorm:"not null;default:0" json:"spell_factory_level"`
	DarkSpellFactoryLevel int      `gorm:"not null;default:0" json:"dark_spell_factory_level"`
	
	// Other buildings
	ClanCastleLevel      int       `gorm:"not null;default:0" json:"clan_castle_level"`
	WallLevel            int       `gorm:"not null;default:0" json:"wall_level"`
	
	SnapshotTime         time.Time `gorm:"not null" json:"snapshot_time"`
	CreatedAt            time.Time `json:"created_at"`
	UpdatedAt            time.Time `json:"updated_at"`
	DeletedAt            gorm.DeletedAt `gorm:"index" json:"deleted_at"`
}

// TableName returns the table name for the BuildingSnapshot model
func (BuildingSnapshot) TableName() string {
	return "building_snapshots"
}

// BuildingTracker represents a tracker for monitoring building upgrades - exact copy from Python
type BuildingTracker struct {
	ID              uint           `gorm:"primaryKey" json:"id"`
	TelegramID      int64          `gorm:"not null;index" json:"telegram_id"`
	PlayerTag       string         `gorm:"size:50;not null;index" json:"player_tag"`
	PlayerName      string         `gorm:"size:255" json:"player_name"`
	IsActive        bool           `gorm:"not null;default:true" json:"is_active"`
	NotifyUpgrades  bool           `gorm:"not null;default:true" json:"notify_upgrades"`
	NotifyFinish    bool           `gorm:"not null;default:true" json:"notify_finish"`
	LastCheckedAt   *time.Time     `json:"last_checked_at"`
	CreatedAt       time.Time      `json:"created_at"`
	UpdatedAt       time.Time      `json:"updated_at"`
	DeletedAt       gorm.DeletedAt `gorm:"index" json:"deleted_at"`
}

// TableName returns the table name for the BuildingTracker model
func (BuildingTracker) TableName() string {
	return "building_trackers"
}

// BuildingUpgrade represents a detected building upgrade - exact copy from Python
type BuildingUpgrade struct {
	ID              uint           `gorm:"primaryKey" json:"id"`
	TrackerID       uint           `gorm:"not null;index" json:"tracker_id"`
	TelegramID      int64          `gorm:"not null;index" json:"telegram_id"`
	PlayerTag       string         `gorm:"size:50;not null" json:"player_tag"`
	PlayerName      string         `gorm:"size:255" json:"player_name"`
	BuildingType    string         `gorm:"size:100;not null" json:"building_type"`
	BuildingName    string         `gorm:"size:255" json:"building_name"`
	OldLevel        int            `gorm:"not null" json:"old_level"`
	NewLevel        int            `gorm:"not null" json:"new_level"`
	UpgradeCost     int64          `gorm:"not null;default:0" json:"upgrade_cost"`
	UpgradeTime     int            `gorm:"not null;default:0" json:"upgrade_time"` // in minutes
	ResourceType    string         `gorm:"size:20" json:"resource_type"` // gold, elixir, dark_elixir
	DetectedAt      time.Time      `gorm:"not null" json:"detected_at"`
	NotifiedAt      *time.Time     `json:"notified_at"`
	IsNotified      bool           `gorm:"not null;default:false" json:"is_notified"`
	CreatedAt       time.Time      `json:"created_at"`
	UpdatedAt       time.Time      `json:"updated_at"`
	DeletedAt       gorm.DeletedAt `gorm:"index" json:"deleted_at"`
	
	// Relationships
	Tracker BuildingTracker `gorm:"foreignKey:TrackerID;references:ID" json:"tracker"`
}

// TableName returns the table name for the BuildingUpgrade model
func (BuildingUpgrade) TableName() string {
	return "building_upgrades"
}

// BeforeCreate hooks
func (bs *BuildingSnapshot) BeforeCreate(tx *gorm.DB) error {
	now := time.Now()
	if bs.CreatedAt.IsZero() {
		bs.CreatedAt = now
	}
	if bs.SnapshotTime.IsZero() {
		bs.SnapshotTime = now
	}
	return nil
}

func (bt *BuildingTracker) BeforeCreate(tx *gorm.DB) error {
	if bt.CreatedAt.IsZero() {
		bt.CreatedAt = time.Now()
	}
	return nil
}

func (bu *BuildingUpgrade) BeforeCreate(tx *gorm.DB) error {
	now := time.Now()
	if bu.CreatedAt.IsZero() {
		bu.CreatedAt = now
	}
	if bu.DetectedAt.IsZero() {
		bu.DetectedAt = now
	}
	return nil
}

// BeforeUpdate hooks
func (bs *BuildingSnapshot) BeforeUpdate(tx *gorm.DB) error {
	bs.UpdatedAt = time.Now()
	return nil
}

func (bt *BuildingTracker) BeforeUpdate(tx *gorm.DB) error {
	bt.UpdatedAt = time.Now()
	return nil
}

func (bu *BuildingUpgrade) BeforeUpdate(tx *gorm.DB) error {
	bu.UpdatedAt = time.Now()
	return nil
}

// Methods for BuildingTracker
func (bt *BuildingTracker) Enable() {
	bt.IsActive = true
}

func (bt *BuildingTracker) Disable() {
	bt.IsActive = false
}

func (bt *BuildingTracker) UpdateLastChecked() {
	now := time.Now()
	bt.LastCheckedAt = &now
}

// Methods for BuildingUpgrade
func (bu *BuildingUpgrade) MarkAsNotified() {
	now := time.Now()
	bu.NotifiedAt = &now
	bu.IsNotified = true
}

func (bu *BuildingUpgrade) GetLevelIncrease() int {
	return bu.NewLevel - bu.OldLevel
}

func (bu *BuildingUpgrade) IsSignificantUpgrade() bool {
	// Town Hall upgrades are always significant
	if bu.BuildingType == "town_hall" || bu.BuildingType == "builder_hall" {
		return true
	}
	
	// Multi-level upgrades are significant
	if bu.GetLevelIncrease() > 1 {
		return true
	}
	
	// High-level upgrades (15+) are significant
	if bu.NewLevel >= 15 {
		return true
	}
	
	return false
}

func (bu *BuildingUpgrade) GetUpgradeMessage() string {
	emoji := "🔨"
	if bu.IsSignificantUpgrade() {
		emoji = "🎉"
	}
	
	return emoji + " Улучшение здания обнаружено!"
}