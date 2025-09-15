"""
Пользовательские состояния для бота Clash of Clans.
"""
from enum import Enum


class UserState(Enum):
    """
    Перечисление состояний пользователя в боте.
    """
    AWAITING_PLAYER_TAG_TO_LINK = "awaiting_player_tag_to_link"
    AWAITING_PLAYER_TAG_TO_SEARCH = "awaiting_player_tag_to_search"
    AWAITING_CLAN_TAG_TO_SEARCH = "awaiting_clan_tag_to_search"