package models

import "time"

// War представляет клановую войну
type War struct {
	ID               int64     `json:"id" db:"id"`
	ClanTag          string    `json:"clan_tag" db:"clan_tag"`
	OpponentTag      string    `json:"opponent_tag" db:"opponent_tag"`
	OpponentName     string    `json:"opponent_name" db:"opponent_name"`
	TeamSize         int       `json:"team_size" db:"team_size"`
	State            string    `json:"state" db:"state"`
	PreparationStart time.Time `json:"preparation_start" db:"preparation_start"`
	StartTime        time.Time `json:"start_time" db:"start_time"`
	EndTime          time.Time `json:"end_time" db:"end_time"`
	ClanStars        int       `json:"clan_stars" db:"clan_stars"`
	OpponentStars    int       `json:"opponent_stars" db:"opponent_stars"`
	ClanDestruction  float64   `json:"clan_destruction" db:"clan_destruction"`
	OpponentDestruction float64 `json:"opponent_destruction" db:"opponent_destruction"`
	IsNotified       bool      `json:"is_notified" db:"is_notified"`
	CreatedAt        time.Time `json:"created_at" db:"created_at"`
	UpdatedAt        time.Time `json:"updated_at" db:"updated_at"`
}

// Attack представляет атаку в войне
type Attack struct {
	ID                int64   `json:"id" db:"id"`
	WarID            int64   `json:"war_id" db:"war_id"`
	AttackerTag      string  `json:"attacker_tag" db:"attacker_tag"`
	AttackerName     string  `json:"attacker_name" db:"attacker_name"`
	DefenderTag      string  `json:"defender_tag" db:"defender_tag"`
	DefenderName     string  `json:"defender_name" db:"defender_name"`
	Stars            int     `json:"stars" db:"stars"`
	Destruction      float64 `json:"destruction" db:"destruction"`
	Order            int     `json:"order" db:"order"`
	AttackerMapPosition int  `json:"attacker_map_position" db:"attacker_map_position"`
	DefenderMapPosition int  `json:"defender_map_position" db:"defender_map_position"`
	Duration         int     `json:"duration" db:"duration"`
}

// CWLSeason представляет сезон Лиги войн кланов
type CWLSeason struct {
	ID         int64     `json:"id" db:"id"`
	ClanTag    string    `json:"clan_tag" db:"clan_tag"`
	Season     string    `json:"season" db:"season"`
	League     string    `json:"league" db:"league"`
	State      string    `json:"state" db:"state"`
	TotalStars int       `json:"total_stars" db:"total_stars"`
	CreatedAt  time.Time `json:"created_at" db:"created_at"`
	UpdatedAt  time.Time `json:"updated_at" db:"updated_at"`
}

// PlayerStatsSnapshot представляет снимок статистики игрока
type PlayerStatsSnapshot struct {
	ID               int64     `json:"id" db:"id"`
	PlayerTag        string    `json:"player_tag" db:"player_tag"`
	PlayerName       string    `json:"player_name" db:"player_name"`
	ClanTag          string    `json:"clan_tag" db:"clan_tag"`
	DonationsGiven   int       `json:"donations_given" db:"donations_given"`
	DonationsReceived int      `json:"donations_received" db:"donations_received"`
	Trophies         int       `json:"trophies" db:"trophies"`
	WarStars         int       `json:"war_stars" db:"war_stars"`
	SnapshotDate     time.Time `json:"snapshot_date" db:"snapshot_date"`
	CreatedAt        time.Time `json:"created_at" db:"created_at"`
}