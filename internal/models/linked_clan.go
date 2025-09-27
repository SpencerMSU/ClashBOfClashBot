package models

import (
	"time"

	"gorm.io/gorm"
)

// LinkedClan represents a clan linked to a user - exact copy from Python models/linked_clan.py
type LinkedClan struct {
	ID          uint           `gorm:"primaryKey" json:"id"`
	TelegramID  int64          `gorm:"not null;index" json:"telegram_id"`
	ClanTag     string         `gorm:"size:50;not null" json:"clan_tag"`
	ClanName    string         `gorm:"size:255" json:"clan_name"`
	ClanLevel   int            `gorm:"not null;default:0" json:"clan_level"`
	MemberCount int            `gorm:"not null;default:0" json:"member_count"`
	IsActive    bool           `gorm:"not null;default:true" json:"is_active"`
	IsPrimary   bool           `gorm:"not null;default:false" json:"is_primary"`
	LinkedAt    time.Time      `gorm:"not null" json:"linked_at"`
	LastUpdated time.Time      `json:"last_updated"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	DeletedAt   gorm.DeletedAt `gorm:"index" json:"deleted_at"`
}

// TableName returns the table name for the LinkedClan model
func (LinkedClan) TableName() string {
	return "linked_clans"
}

// BeforeCreate hook to set creation timestamp
func (lc *LinkedClan) BeforeCreate(tx *gorm.DB) error {
	now := time.Now()
	if lc.CreatedAt.IsZero() {
		lc.CreatedAt = now
	}
	if lc.LinkedAt.IsZero() {
		lc.LinkedAt = now
	}
	if lc.LastUpdated.IsZero() {
		lc.LastUpdated = now
	}
	return nil
}

// BeforeUpdate hook to set update timestamp
func (lc *LinkedClan) BeforeUpdate(tx *gorm.DB) error {
	lc.UpdatedAt = time.Now()
	lc.LastUpdated = time.Now()
	return nil
}

// Activate sets the clan as active
func (lc *LinkedClan) Activate() {
	lc.IsActive = true
}

// Deactivate sets the clan as inactive
func (lc *LinkedClan) Deactivate() {
	lc.IsActive = false
}

// SetAsPrimary sets this clan as the primary clan
func (lc *LinkedClan) SetAsPrimary() {
	lc.IsPrimary = true
}

// UnsetAsPrimary removes the primary status from this clan
func (lc *LinkedClan) UnsetAsPrimary() {
	lc.IsPrimary = false
}

// UpdateClanInfo updates the clan information
func (lc *LinkedClan) UpdateClanInfo(name string, level int, memberCount int) {
	lc.ClanName = name
	lc.ClanLevel = level
	lc.MemberCount = memberCount
	lc.LastUpdated = time.Now()
}

// IsValidClanTag checks if the clan tag is valid format
func (lc *LinkedClan) IsValidClanTag() bool {
	if len(lc.ClanTag) < 3 {
		return false
	}
	// Clan tags start with # in Clash of Clans
	if lc.ClanTag[0] != '#' {
		return false
	}
	return true
}

// GetDisplayName returns the clan display name with tag
func (lc *LinkedClan) GetDisplayName() string {
	if lc.ClanName != "" {
		return lc.ClanName + " (" + lc.ClanTag + ")"
	}
	return lc.ClanTag
}

// GetFormattedLinkedTime returns formatted linked time
func (lc *LinkedClan) GetFormattedLinkedTime() string {
	return lc.LinkedAt.Format("2006-01-02 15:04:05")
}

// GetFormattedLastUpdated returns formatted last updated time
func (lc *LinkedClan) GetFormattedLastUpdated() string {
	return lc.LastUpdated.Format("2006-01-02 15:04:05")
}

// DaysSinceLinked returns the number of days since the clan was linked
func (lc *LinkedClan) DaysSinceLinked() int {
	duration := time.Since(lc.LinkedAt)
	return int(duration.Hours() / 24)
}

// IsRecentlyLinked checks if the clan was linked within the last 7 days
func (lc *LinkedClan) IsRecentlyLinked() bool {
	return lc.DaysSinceLinked() <= 7
}