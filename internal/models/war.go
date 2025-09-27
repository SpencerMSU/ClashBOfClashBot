package models

import (
	"time"

	"gorm.io/gorm"
)

// WarState represents the state of a war
type WarState string

const (
	WarStateNotInWar       WarState = "notInWar"
	WarStatePreparation    WarState = "preparation"
	WarStateInWar         WarState = "inWar"
	WarStateWarEnded      WarState = "warEnded"
)

// WarResult represents the result of a war
type WarResult string

const (
	WarResultWin  WarResult = "win"
	WarResultLose WarResult = "lose"
	WarResultTie  WarResult = "tie"
)

// WarToSave represents a war to be saved - exact copy from Python models/war.py
type WarToSave struct {
	ID                   uint               `gorm:"primaryKey" json:"id"`
	EndTime              time.Time          `gorm:"not null;uniqueIndex" json:"end_time"`
	State                WarState           `gorm:"size:20;not null" json:"state"`
	TeamSize             int                `gorm:"not null" json:"team_size"`
	ClanTag              string             `gorm:"size:50;not null" json:"clan_tag"`
	ClanName             string             `gorm:"size:255" json:"clan_name"`
	ClanStars            int                `gorm:"not null;default:0" json:"clan_stars"`
	ClanAttacksUsed      int                `gorm:"not null;default:0" json:"clan_attacks_used"`
	ClanDestruction      float64            `gorm:"type:decimal(5,2);not null;default:0" json:"clan_destruction"`
	OpponentTag          string             `gorm:"size:50;not null" json:"opponent_tag"`
	OpponentName         string             `gorm:"size:255" json:"opponent_name"`
	OpponentStars        int                `gorm:"not null;default:0" json:"opponent_stars"`
	OpponentAttacksUsed  int                `gorm:"not null;default:0" json:"opponent_attacks_used"`
	OpponentDestruction  float64            `gorm:"type:decimal(5,2);not null;default:0" json:"opponent_destruction"`
	Result               WarResult          `gorm:"size:10" json:"result"`
	IsCWLWar             bool               `gorm:"not null;default:false" json:"is_cwl_war"`
	TotalViolations      int                `gorm:"not null;default:0" json:"total_violations"`
	CreatedAt            time.Time          `json:"created_at"`
	UpdatedAt            time.Time          `json:"updated_at"`
	DeletedAt            gorm.DeletedAt     `gorm:"index" json:"deleted_at"`
	
	// Relationships
	Attacks []AttackData `gorm:"foreignKey:WarEndTime;references:EndTime" json:"attacks"`
}

// TableName returns the table name for the WarToSave model
func (WarToSave) TableName() string {
	return "wars"
}

// AttackData represents an attack in a war - exact copy from Python
type AttackData struct {
	ID               uint               `gorm:"primaryKey" json:"id"`
	WarEndTime       time.Time          `gorm:"not null;index" json:"war_end_time"`
	AttackerTag      string             `gorm:"size:50;not null" json:"attacker_tag"`
	AttackerName     string             `gorm:"size:255" json:"attacker_name"`
	AttackerMapPos   int                `gorm:"not null" json:"attacker_map_position"`
	DefenderTag      string             `gorm:"size:50;not null" json:"defender_tag"`
	DefenderName     string             `gorm:"size:255" json:"defender_name"`
	DefenderMapPos   int                `gorm:"not null" json:"defender_map_position"`
	Stars            int                `gorm:"not null;default:0" json:"stars"`
	Destruction      float64            `gorm:"type:decimal(5,2);not null;default:0" json:"destruction"`
	AttackOrder      int                `gorm:"not null" json:"attack_order"`
	Duration         int                `gorm:"not null;default:0" json:"duration"`
	Timestamp        time.Time          `json:"timestamp"`
	IsNewBestAttack  bool               `gorm:"not null;default:false" json:"is_new_best_attack"`
	CreatedAt        time.Time          `json:"created_at"`
	UpdatedAt        time.Time          `json:"updated_at"`
	DeletedAt        gorm.DeletedAt     `gorm:"index" json:"deleted_at"`
}

// TableName returns the table name for the AttackData model
func (AttackData) TableName() string {
	return "attacks"
}

// BeforeCreate hook for WarToSave
func (w *WarToSave) BeforeCreate(tx *gorm.DB) error {
	if w.CreatedAt.IsZero() {
		w.CreatedAt = time.Now()
	}
	return nil
}

// BeforeUpdate hook for WarToSave
func (w *WarToSave) BeforeUpdate(tx *gorm.DB) error {
	w.UpdatedAt = time.Now()
	return nil
}

// BeforeCreate hook for AttackData
func (a *AttackData) BeforeCreate(tx *gorm.DB) error {
	if a.CreatedAt.IsZero() {
		a.CreatedAt = time.Now()
	}
	if a.Timestamp.IsZero() {
		a.Timestamp = time.Now()
	}
	return nil
}

// BeforeUpdate hook for AttackData
func (a *AttackData) BeforeUpdate(tx *gorm.DB) error {
	a.UpdatedAt = time.Now()
	return nil
}

// IsEnded checks if the war has ended
func (w *WarToSave) IsEnded() bool {
	return w.State == WarStateWarEnded
}

// IsInPreparation checks if the war is in preparation phase
func (w *WarToSave) IsInPreparation() bool {
	return w.State == WarStatePreparation
}

// IsActive checks if the war is currently active
func (w *WarToSave) IsActive() bool {
	return w.State == WarStateInWar
}

// GetStarDifference returns the star difference (positive if we're winning)
func (w *WarToSave) GetStarDifference() int {
	return w.ClanStars - w.OpponentStars
}

// GetDestructionDifference returns the destruction percentage difference
func (w *WarToSave) GetDestructionDifference() float64 {
	return w.ClanDestruction - w.OpponentDestruction
}

// CalculateResult calculates and sets the war result based on stars and destruction
func (w *WarToSave) CalculateResult() {
	if w.ClanStars > w.OpponentStars {
		w.Result = WarResultWin
	} else if w.ClanStars < w.OpponentStars {
		w.Result = WarResultLose
	} else {
		// Equal stars, check destruction
		if w.ClanDestruction > w.OpponentDestruction {
			w.Result = WarResultWin
		} else if w.ClanDestruction < w.OpponentDestruction {
			w.Result = WarResultLose
		} else {
			w.Result = WarResultTie
		}
	}
}

// GetFormattedEndTime returns formatted end time
func (w *WarToSave) GetFormattedEndTime() string {
	return w.EndTime.Format("2006-01-02 15:04:05")
}

// IsViolation checks if an attack is considered a violation (attacking lower)
func (a *AttackData) IsViolation() bool {
	return a.DefenderMapPos < a.AttackerMapPos
}

// GetStarRating returns star rating emoji
func (a *AttackData) GetStarRating() string {
	switch a.Stars {
	case 0:
		return "⭐"
	case 1:
		return "⭐"
	case 2:
		return "⭐⭐"
	case 3:
		return "⭐⭐⭐"
	default:
		return ""
	}
}

// GetDestructionPercent returns destruction as percentage
func (a *AttackData) GetDestructionPercent() int {
	return int(a.Destruction)
}

// IsGoodAttack checks if attack is considered good (2+ stars or high destruction)
func (a *AttackData) IsGoodAttack() bool {
	return a.Stars >= 2 || a.Destruction >= 85.0
}

// GetAttackScore calculates attack score for ranking
func (a *AttackData) GetAttackScore() float64 {
	return float64(a.Stars)*100 + a.Destruction
}