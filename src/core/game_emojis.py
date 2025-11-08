"""Игровые иконки и эмодзи, использующиеся в сообщениях бота."""
from typing import Dict


COC_EMOJIS: Dict[str, str] = {
    "community": "🏯",
    "section": "📘",
    "building_costs": "⚒️",
    "base_layouts": "🛡️",
    "leagues": "🏆",
    "defense_category": "🛡️",
    "army_category": "⚔️",
    "resource_category": "🪙",
    "heroes_category": "👑",
    "builder_category": "🛠️",
    "gold": "🪙",
    "elixir": "🔮",
    "dark_elixir": "⚫️",
    "info": "📘",
    "tip": "💬",
    "bullet": "◆",
    "back": "⬅️",
    "under_construction": "🚧",
    "new": "✨",
    "trophy_league": "🏆",
    "war_league": "🛡️",
    "builder_league": "⚙️",
    "capital_league": "🏰",
    "stat": "📊",
    "note": "📝",
    "star": "✦",
}


_LEAGUE_ICON_KEYWORDS = {
    "bronze": "🟤",
    "silver": "⚪️",
    "gold": "🪙",
    "crystal": "🔷",
    "master": "🟥",
    "champion": "🏵️",
    "titan": "🛡️",
    "legend": "🏆",
    "mythic": "💠",
    "diamond": "🔹",
    "ruby": "🔴",
    "emerald": "🟢",
    "platinum": "⚪️",
    "titanium": "⚙️",
    "steel": "⬜️",
    "iron": "⬛️",
    "brass": "🟡",
    "copper": "🟠",
    "stone": "🪨",
    "wood": "🪵",
    "capital": "🏰",
}


def get_league_icon(league_name: str, fallback_key: str = "leagues") -> str:
    """Возвращает иконку для указанной лиги."""
    name_lower = league_name.lower()
    for keyword, icon in _LEAGUE_ICON_KEYWORDS.items():
        if keyword in name_lower:
            return icon
    return COC_EMOJIS.get(fallback_key, COC_EMOJIS["leagues"])
