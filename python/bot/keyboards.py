"""
Константы клавиатур и кнопок для бота Clash of Clans.
"""


class Keyboards:
    """
    Константы для кнопок и callback-данных.
    """
    
    # Константы для кнопок
    PROFILE_BTN = "👤 Профиль"
    CLAN_BTN = "🛡 Клан"
    LINK_ACC_BTN = "🔗 Привязать аккаунт"
    SEARCH_PROFILE_BTN = "🔍 Найти профиль по тегу"
    MY_CLAN_BTN = "🛡 Мой клан (из профиля)"
    SEARCH_CLAN_BTN = "🔍 Найти клан по тегу"
    BACK_BTN = "⬅️ Назад в главное меню"
    MY_PROFILE_PREFIX = "👤 Мой профиль"
    CLAN_MEMBERS_BTN = "👥 Список участников"
    CLAN_WARLOG_BTN = "⚔️ Последние войны"
    BACK_TO_CLAN_MENU_BTN = "⬅️ Назад в меню кланов"
    CLAN_CURRENT_CWL_BTN = "⚔️ Текущее ЛВК"
    CLAN_CWL_BONUS_BTN = "🏆 Бонусы ЛВК"
    NOTIFICATIONS_BTN = "🔔 Уведомления о КВ"
    CLAN_CURRENT_WAR_BTN = "⚔️ Текущая КВ"

    # Константы для callback-данных
    MEMBERS_CALLBACK = "members"
    WAR_LIST_CALLBACK = "warlist"
    WAR_INFO_CALLBACK = "warinfo"
    PROFILE_CALLBACK = "profile"
    NOTIFY_TOGGLE_CALLBACK = "notify_toggle"
    CWL_BONUS_CALLBACK = "cwlbonus"
    MEMBERS_SORT_CALLBACK = "members_sort"
    MEMBERS_VIEW_CALLBACK = "members_view"