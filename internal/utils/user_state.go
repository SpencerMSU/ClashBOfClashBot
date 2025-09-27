package utils

// UserState represents the current state of user interaction
type UserState string

// All user states - exact copy from Python user_state.py
const (
	AwaitingPlayerTagToLink      UserState = "AWAITING_PLAYER_TAG_TO_LINK"
	AwaitingPlayerTagToSearch    UserState = "AWAITING_PLAYER_TAG_TO_SEARCH"
	AwaitingClanTagToSearch      UserState = "AWAITING_CLAN_TAG_TO_SEARCH"
	AwaitingClanTagToLink        UserState = "AWAITING_CLAN_TAG_TO_LINK"
	AwaitingNotificationTime     UserState = "AWAITING_NOTIFICATION_TIME"
	AwaitingPlayerTagToAddProfile UserState = "AWAITING_PLAYER_TAG_TO_ADD_PROFILE"
)

// String returns the string representation of the UserState
func (us UserState) String() string {
	return string(us)
}

// IsValid checks if the UserState is valid
func (us UserState) IsValid() bool {
	switch us {
	case AwaitingPlayerTagToLink,
		AwaitingPlayerTagToSearch,
		AwaitingClanTagToSearch,
		AwaitingClanTagToLink,
		AwaitingNotificationTime,
		AwaitingPlayerTagToAddProfile:
		return true
	default:
		return false
	}
}