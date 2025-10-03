package utils

// UserState represents the state of a user in a conversation flow
type UserState string

const (
	// AwaitingPlayerTagToLink - waiting for player tag to link to account
	AwaitingPlayerTagToLink UserState = "awaiting_player_tag_to_link"
	
	// AwaitingPlayerTagToSearch - waiting for player tag to search
	AwaitingPlayerTagToSearch UserState = "awaiting_player_tag_to_search"
	
	// AwaitingClanTagToSearch - waiting for clan tag to search
	AwaitingClanTagToSearch UserState = "awaiting_clan_tag_to_search"
	
	// AwaitingClanTagToLink - waiting for clan tag to link
	AwaitingClanTagToLink UserState = "awaiting_clan_tag_to_link"
	
	// AwaitingNotificationTime - waiting for notification time input
	AwaitingNotificationTime UserState = "awaiting_notification_time"
	
	// AwaitingPlayerTagToAddProfile - waiting for player tag to add a new profile
	AwaitingPlayerTagToAddProfile UserState = "awaiting_player_tag_to_add_profile"
	
	// AwaitingClanTagForWarScan - waiting for clan tag for war scan request
	AwaitingClanTagForWarScan UserState = "awaiting_clan_tag_for_war_scan"
)

// String returns the string representation of the UserState
func (s UserState) String() string {
	return string(s)
}
