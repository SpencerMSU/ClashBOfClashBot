package models

import "time"

// LinkedClan represents a linked clan in the system
type LinkedClan struct {
	ClanTag     string    `json:"clan_tag"`
	ClanName    string    `json:"clan_name"`
	LinkedBy    int64     `json:"linked_by"` // telegram_id of user who linked
	LinkedAt    time.Time `json:"linked_at"`
	IsActive    bool      `json:"is_active"`
	Description *string   `json:"description,omitempty"`
}

// NewLinkedClan creates a new LinkedClan instance
func NewLinkedClan(clanTag, clanName string, linkedBy int64) *LinkedClan {
	return &LinkedClan{
		ClanTag:  clanTag,
		ClanName: clanName,
		LinkedBy: linkedBy,
		LinkedAt: time.Now(),
		IsActive: true,
	}
}
