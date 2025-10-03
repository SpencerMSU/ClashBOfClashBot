package models

import "time"

// LinkedClan represents a linked clan in the system
type LinkedClan struct {
	ID          int64     `json:"id"`
	TelegramID  int64     `json:"telegram_id"` // Alias for LinkedBy
	ClanTag     string    `json:"clan_tag"`
	ClanName    string    `json:"clan_name"`
	LinkedBy    int64     `json:"linked_by"` // telegram_id of user who linked
	LinkedAt    time.Time `json:"linked_at"`
	IsActive    bool      `json:"is_active"`
	Description *string   `json:"description,omitempty"`
	SlotNumber  int       `json:"slot_number"`
	CreatedAt   time.Time `json:"created_at"`
}

// NewLinkedClan creates a new LinkedClan instance
func NewLinkedClan(clanTag, clanName string, linkedBy int64) *LinkedClan {
	now := time.Now()
	return &LinkedClan{
		ID:         0, // Set by database
		TelegramID: linkedBy,
		ClanTag:    clanTag,
		ClanName:   clanName,
		LinkedBy:   linkedBy,
		LinkedAt:   now,
		IsActive:   true,
		SlotNumber: 0,
		CreatedAt:  now,
	}
}
