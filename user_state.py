"""
Состояния пользователя - аналог Java UserState
"""
from enum import Enum


class UserState(Enum):
    """Состояния пользователя для диалогов"""
    AWAITING_PLAYER_TAG_TO_LINK = "awaiting_player_tag_to_link"
    AWAITING_PLAYER_TAG_TO_SEARCH = "awaiting_player_tag_to_search"
    AWAITING_CLAN_TAG_TO_SEARCH = "awaiting_clan_tag_to_search"
    AWAITING_CLAN_TAG_TO_LINK = "awaiting_clan_tag_to_link"
    AWAITING_NOTIFICATION_TIME = "awaiting_notification_time"
    AWAITING_PLAYER_TAG_TO_ADD_PROFILE = "awaiting_player_tag_to_add_profile"