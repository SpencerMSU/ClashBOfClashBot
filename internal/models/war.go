package models

import "time"

// WarToSave represents a clan war to be saved
type WarToSave struct {
	ClanTag                       string    `json:"clan_tag"`
	State                         string    `json:"state"`
	TeamSize                      int       `json:"team_size"`
	PreparationTime               time.Time `json:"preparation_start_time"`
	StartTime                     time.Time `json:"start_time"`
	EndTime                       time.Time `json:"end_time"`
	ClanName                      string    `json:"clan_name"`
	ClanLevel                     int       `json:"clan_level"`
	ClanStars                     int       `json:"clan_stars"`
	ClanDestructionPercentage     float64   `json:"clan_destruction_percentage"`
	OpponentName                  string    `json:"opponent_name"`
	OpponentTag                   string    `json:"opponent_tag"`
	OpponentLevel                 int       `json:"opponent_level"`
	OpponentStars                 int       `json:"opponent_stars"`
	OpponentDestructionPercentage float64   `json:"opponent_destruction_percentage"`
	Result                        string    `json:"result"` // "win", "lose", "tie"
	IsCWL                         bool      `json:"is_cwl"`
}

// AttackData represents an attack in a clan war
type AttackData struct {
	AttackerTag           string  `json:"attacker_tag"`
	AttackerName          string  `json:"attacker_name"`
	DefenderTag           string  `json:"defender_tag"`
	DefenderName          string  `json:"defender_name"`
	Stars                 int     `json:"stars"`
	DestructionPercentage float64 `json:"destruction_percentage"`
	Order                 int     `json:"order"`
	IsViolation           bool    `json:"is_violation"`
}

// NewWarToSave creates a new WarToSave instance
func NewWarToSave(clanTag string) *WarToSave {
	return &WarToSave{
		ClanTag: clanTag,
		State:   "notInWar",
		IsCWL:   false,
	}
}

// NewAttackData creates a new AttackData instance
func NewAttackData(attackerTag, defenderTag string) *AttackData {
	return &AttackData{
		AttackerTag: attackerTag,
		DefenderTag: defenderTag,
		IsViolation: false,
	}
}
