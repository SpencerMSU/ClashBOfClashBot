package models

import "time"

// WarToSave represents a clan war to be saved
type WarToSave struct {
	EndTime                       string    `json:"end_time"`
	OpponentName                  string    `json:"opponent_name"`
	TeamSize                      int       `json:"team_size"`
	ClanStars                     int       `json:"clan_stars"`
	OpponentStars                 int       `json:"opponent_stars"`
	ClanDestructionPercentage     float64   `json:"clan_destruction_percentage"`
	OpponentDestructionPercentage float64   `json:"opponent_destruction_percentage"`
	ClanAttacksUsed               int       `json:"clan_attacks_used"`
	Result                        string    `json:"result"` // "win", "lose", "tie"
	IsCWL                         bool      `json:"is_cwl"`
	TotalViolations               int       `json:"total_violations"`
	Attacks                       []AttackData `json:"attacks"`
}

// AttackData represents an attack in a clan war
type AttackData struct {
	AttackerName  string  `json:"attacker_name"`
	DefenderTag   string  `json:"defender_tag"`
	Stars         int     `json:"stars"`
	Destruction   float64 `json:"destruction"`
	Order         int     `json:"order"`
	Timestamp     int     `json:"timestamp"`
	IsViolation   int     `json:"is_violation"`
}

// NewWarToSave creates a new WarToSave instance with all parameters
func NewWarToSave(
	endTime string,
	opponentName string,
	teamSize int,
	clanStars int,
	opponentStars int,
	clanDestruction float64,
	opponentDestruction float64,
	clanAttacksUsed int,
	result string,
	isCWLWar bool,
	totalViolations int,
) *WarToSave {
	return &WarToSave{
		EndTime:                       endTime,
		OpponentName:                  opponentName,
		TeamSize:                      teamSize,
		ClanStars:                     clanStars,
		OpponentStars:                 opponentStars,
		ClanDestructionPercentage:     clanDestruction,
		OpponentDestructionPercentage: opponentDestruction,
		ClanAttacksUsed:               clanAttacksUsed,
		Result:                        result,
		IsCWL:                         isCWLWar,
		TotalViolations:               totalViolations,
	}
}

// NewAttackData creates a new AttackData instance
func NewAttackData(attackerName, defenderTag string) *AttackData {
	return &AttackData{
		AttackerName: attackerName,
		DefenderTag:  defenderTag,
		IsViolation:  0,
	}
}
