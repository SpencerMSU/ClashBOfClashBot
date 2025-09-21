"""
Клавиатуры и кнопки для бота - аналог Java Keyboards
"""
from typing import List, Optional, Dict, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, date


class Keyboards:
    """Класс для создания клавиатур бота"""
    
    # Константы для кнопок
    PROFILE_BTN = "👤 Профиль"
    CLAN_BTN = "🛡 Клан"
    LINK_ACC_BTN = "🔗 Привязать аккаунт"
    SEARCH_PROFILE_BTN = "🔍 Найти профиль по тегу"
    MY_CLAN_BTN = "🛡 Мой клан (из профиля)"
    SEARCH_CLAN_BTN = "🔍 Найти клан по тегу"
    BACK_BTN = "⬅️ Назад в главное меню"
    MY_PROFILE_PREFIX = "👤 Мой профиль"
    PROFILE_MANAGER_BTN = "👥 Менеджер профилей"
    CLAN_MEMBERS_BTN = "👥 Список участников"
    CLAN_WARLOG_BTN = "⚔️ Последние войны"
    BACK_TO_CLAN_MENU_BTN = "⬅️ Назад в меню кланов"
    CLAN_CURRENT_CWL_BTN = "⚔️ Текущее ЛВК"
    CLAN_CWL_BONUS_BTN = "🏆 Бонусы ЛВК"
    NOTIFICATIONS_BTN = "🔔 Уведомления"
    CLAN_CURRENT_WAR_BTN = "⚔️ Текущая КВ"
    SUBSCRIPTION_BTN = "💎 Премиум подписка"
    LINKED_CLANS_BTN = "🔗 Привязанные кланы"
    COMMUNITY_CENTER_BTN = "🏛️ Центр сообщества"
    ACHIEVEMENTS_BTN = "🏆 Достижения"
    
    # Константы для callback-данных
    MEMBERS_CALLBACK = "members"
    WAR_LIST_CALLBACK = "warlist"
    WAR_INFO_CALLBACK = "warinfo"
    PROFILE_CALLBACK = "profile"
    NOTIFY_TOGGLE_CALLBACK = "notify_toggle"
    CWL_BONUS_CALLBACK = "cwlbonus"
    MEMBERS_SORT_CALLBACK = "members_sort"
    MEMBERS_VIEW_CALLBACK = "members_view"
    SUBSCRIPTION_CALLBACK = "subscription"
    SUBSCRIPTION_EXTEND_CALLBACK = "subscription_extend"
    SUBSCRIPTION_TYPE_CALLBACK = "sub_type"
    SUBSCRIPTION_PERIOD_CALLBACK = "sub_period"
    SUBSCRIPTION_PAY_CALLBACK = "sub_pay"
    PREMIUM_MENU_CALLBACK = "premium_menu"
    NOTIFY_ADVANCED_CALLBACK = "notify_advanced"
    NOTIFY_CUSTOM_CALLBACK = "notify_custom"
    BUILDING_TRACKER_CALLBACK = "building_tracker"
    BUILDING_TOGGLE_CALLBACK = "building_toggle"
    PROFILE_MANAGER_CALLBACK = "profile_manager"
    PROFILE_SELECT_CALLBACK = "profile_select"
    PROFILE_DELETE_CALLBACK = "profile_delete"
    PROFILE_DELETE_CONFIRM_CALLBACK = "profile_delete_confirm"
    PROFILE_ADD_CALLBACK = "profile_add"
    LINKED_CLANS_CALLBACK = "linked_clans"
    LINKED_CLAN_SELECT_CALLBACK = "linked_clan_select"
    LINKED_CLAN_ADD_CALLBACK = "linked_clan_add"
    LINKED_CLAN_DELETE_CALLBACK = "linked_clan_delete"
    COMMUNITY_CENTER_CALLBACK = "community_center"
    BUILDING_COSTS_CALLBACK = "building_costs"
    BUILDING_CATEGORY_CALLBACK = "building_category"
    BUILDING_DETAIL_CALLBACK = "building_detail"
    BASE_LAYOUTS_CALLBACK = "base_layouts"
    BASE_LAYOUTS_TH_CALLBACK = "base_layouts_th"
    ACHIEVEMENTS_CALLBACK = "achievements"
    ACHIEVEMENTS_SORT_CALLBACK = "achievements_sort"
    ACHIEVEMENTS_PAGE_CALLBACK = "achievements_page"
    
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Главное меню бота"""
        keyboard = [
            [KeyboardButton(Keyboards.PROFILE_BTN), KeyboardButton(Keyboards.CLAN_BTN)],
            [KeyboardButton(Keyboards.NOTIFICATIONS_BTN), KeyboardButton(Keyboards.COMMUNITY_CENTER_BTN)]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def profile_menu(player_name: Optional[str] = None, has_premium: bool = False, 
                    profile_count: int = 0) -> ReplyKeyboardMarkup:
        """Меню профиля"""
        keyboard = []
        
        if has_premium and profile_count > 0:
            # Для премиум пользователей с профилями показываем менеджер профилей
            keyboard.append([KeyboardButton(Keyboards.PROFILE_MANAGER_BTN)])
        elif player_name:
            # Для обычных пользователей или премиум с одним профилем
            keyboard.append([KeyboardButton(f"{Keyboards.MY_PROFILE_PREFIX} ({player_name})")])
        else:
            keyboard.append([KeyboardButton(Keyboards.LINK_ACC_BTN)])
        
        # Всегда добавляем кнопку подписки, чтобы она была видна всем пользователям
        keyboard.append([KeyboardButton(Keyboards.SUBSCRIPTION_BTN)])
        
        keyboard.extend([
            [KeyboardButton(Keyboards.SEARCH_PROFILE_BTN)],
            [KeyboardButton(Keyboards.MY_CLAN_BTN)] if (player_name or (has_premium and profile_count > 0)) else [],
            [KeyboardButton(Keyboards.BACK_BTN)]
        ])
        
        # Удаляем пустые списки
        keyboard = [row for row in keyboard if row]
        
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def clan_menu() -> ReplyKeyboardMarkup:
        """Меню клана"""
        keyboard = [
            [KeyboardButton(Keyboards.SEARCH_CLAN_BTN)],
            [KeyboardButton(Keyboards.LINKED_CLANS_BTN)],
            [KeyboardButton(Keyboards.BACK_BTN)]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def clan_inspection_menu() -> InlineKeyboardMarkup:
        """Меню для просмотра клана"""
        keyboard = [
            [InlineKeyboardButton("👥 Участники", callback_data=Keyboards.MEMBERS_CALLBACK)],
            [InlineKeyboardButton("⚔️ История войн", callback_data=Keyboards.WAR_LIST_CALLBACK)],
            [InlineKeyboardButton("⚔️ Текущая война", callback_data="current_war")],
            [InlineKeyboardButton("🏆 ЛВК", callback_data="cwl_info")],
            [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def members_pagination(clan_tag: str, current_page: int, total_pages: int, 
                          sort_type: str = "role", view_type: str = "compact") -> InlineKeyboardMarkup:
        """Пагинация для списка участников"""
        keyboard = []
        
        # Сортировка и вид
        sort_buttons = [
            InlineKeyboardButton("🎖 По роли", 
                               callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:role:{view_type}:{current_page}"),
            InlineKeyboardButton("🏆 По трофеям", 
                               callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:trophies:{view_type}:{current_page}")
        ]
        keyboard.append(sort_buttons)
        
        view_buttons = [
            InlineKeyboardButton("📋 Компактно", 
                               callback_data=f"{Keyboards.MEMBERS_VIEW_CALLBACK}:{clan_tag}:{sort_type}:compact:{current_page}"),
            InlineKeyboardButton("📄 Подробно", 
                               callback_data=f"{Keyboards.MEMBERS_VIEW_CALLBACK}:{clan_tag}:{sort_type}:detailed:{current_page}")
        ]
        keyboard.append(view_buttons)
        
        # Навигация
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️", 
                                                   callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:{sort_type}:{view_type}:{current_page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️", 
                                                   callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:{sort_type}:{view_type}:{current_page+1}"))
        
        keyboard.append(nav_buttons)
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def members_with_profiles(clan_tag: str, current_page: int, total_pages: int, 
                             sort_type: str = "role", view_type: str = "compact", 
                             members: List[Dict] = None) -> InlineKeyboardMarkup:
        """Пагинация для списка участников с кликабельными профилями"""
        keyboard = []
        
        # Добавляем кнопки для отдельных игроков (по 2 в ряд)
        if members:
            for i in range(0, len(members), 2):
                row = []
                for j in range(2):
                    if i + j < len(members):
                        member = members[i + j]
                        name = member.get('name', 'Неизвестно')
                        tag = member.get('tag', '')
                        # Ограничиваем длину имени для кнопки
                        display_name = name[:15] + "..." if len(name) > 15 else name
                        row.append(InlineKeyboardButton(f"👤 {display_name}", 
                                                       callback_data=f"{Keyboards.PROFILE_CALLBACK}:{tag}"))
                keyboard.append(row)
        
        # Сортировка и вид
        sort_buttons = [
            InlineKeyboardButton("🎖 По роли", 
                               callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:role:{view_type}:{current_page}"),
            InlineKeyboardButton("🏆 По трофеям", 
                               callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:trophies:{view_type}:{current_page}")
        ]
        keyboard.append(sort_buttons)
        
        view_buttons = [
            InlineKeyboardButton("📋 Компактно", 
                               callback_data=f"{Keyboards.MEMBERS_VIEW_CALLBACK}:{clan_tag}:{sort_type}:compact:{current_page}"),
            InlineKeyboardButton("📄 Подробно", 
                               callback_data=f"{Keyboards.MEMBERS_VIEW_CALLBACK}:{clan_tag}:{sort_type}:detailed:{current_page}")
        ]
        keyboard.append(view_buttons)
        
        # Навигация
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️", 
                                                   callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:{sort_type}:{view_type}:{current_page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️", 
                                                   callback_data=f"{Keyboards.MEMBERS_SORT_CALLBACK}:{clan_tag}:{sort_type}:{view_type}:{current_page+1}"))
        
        keyboard.append(nav_buttons)
        
        # Add back button
        keyboard.append([InlineKeyboardButton("⬅️ К информации о клане", callback_data="clan_info")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def war_list_pagination(clan_tag: str, current_page: int, total_pages: int,
                           sort_order: str = "recent") -> InlineKeyboardMarkup:
        """Пагинация для списка войн"""
        keyboard = []
        
        # Сортировка
        sort_buttons = [
            InlineKeyboardButton("📅 Недавние", 
                               callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:recent:{current_page}"),
            InlineKeyboardButton("🏆 Победы", 
                               callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:wins:{current_page}"),
            InlineKeyboardButton("❌ Поражения", 
                               callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:losses:{current_page}")
        ]
        keyboard.append(sort_buttons)
        
        # Навигация
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️", 
                                                   callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:{sort_order}:{current_page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️", 
                                                   callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:{sort_order}:{current_page+1}"))
        
        keyboard.append(nav_buttons)
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def war_list_with_details(clan_tag: str, current_page: int, total_pages: int,
                             sort_order: str = "recent", wars: List[Dict] = None) -> InlineKeyboardMarkup:
        """Пагинация для списка войн с кликабельными деталями"""
        keyboard = []
        
        # Добавляем кнопки для отдельных войн
        if wars:
            for war in wars:
                opponent_name = war.get('opponent_name', 'Неизвестно')
                result = war.get('result', 'tie')
                result_emoji = {"win": "🏆", "lose": "❌", "tie": "🤝"}.get(result, "❓")
                is_cwl = war.get('is_cwl_war', False)
                war_type = "ЛВК" if is_cwl else "КВ"
                
                # Ограничиваем длину имени противника для кнопки
                display_name = opponent_name[:20] + "..." if len(opponent_name) > 20 else opponent_name
                war_end_time = war.get('end_time', '')
                
                keyboard.append([
                    InlineKeyboardButton(f"{result_emoji} {war_type} vs {display_name}", 
                                       callback_data=f"{Keyboards.WAR_INFO_CALLBACK}:{clan_tag}:{war_end_time}")
                ])
        
        # Сортировка
        sort_buttons = [
            InlineKeyboardButton("📅 Недавние", 
                               callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:recent:{current_page}"),
            InlineKeyboardButton("🏆 Победы", 
                               callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:wins:{current_page}"),
            InlineKeyboardButton("❌ Поражения", 
                               callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:losses:{current_page}")
        ]
        keyboard.append(sort_buttons)
        
        # Навигация
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️", 
                                                   callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:{sort_order}:{current_page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️", 
                                                   callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:{sort_order}:{current_page+1}"))
        
        keyboard.append(nav_buttons)
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def war_details_menu(clan_tag: str, war_end_time: str) -> InlineKeyboardMarkup:
        """Меню для детальной информации о войне"""
        keyboard = [
            [InlineKeyboardButton("📊 Статистика атак", 
                                callback_data=f"war_attacks:{clan_tag}:{war_end_time}")],
            [InlineKeyboardButton("🚫 Нарушения", 
                                callback_data=f"war_violations:{clan_tag}:{war_end_time}")],
            [InlineKeyboardButton("⬅️ К списку войн", 
                                callback_data=f"{Keyboards.WAR_LIST_CALLBACK}:{clan_tag}:recent:1")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def notification_toggle() -> InlineKeyboardMarkup:
        """Кнопка переключения уведомлений"""
        keyboard = [
            [InlineKeyboardButton("🔔 Переключить уведомления", 
                                callback_data=Keyboards.NOTIFY_TOGGLE_CALLBACK)]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def cwl_bonus_menu() -> InlineKeyboardMarkup:
        """Меню бонусов ЛВК"""
        keyboard = []
        
        # Последние 3 месяца
        current_date = date.today()
        for i in range(3):
            month_date = date(current_date.year, current_date.month - i, 1) if current_date.month - i > 0 else date(current_date.year - 1, 12 + current_date.month - i, 1)
            month_str = month_date.strftime("%Y-%m")
            month_name = month_date.strftime("%B %Y")
            
            keyboard.append([
                InlineKeyboardButton(f"🏆 {month_name}", 
                                   callback_data=f"{Keyboards.CWL_BONUS_CALLBACK}:{month_str}")
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Кнопка возврата в главное меню"""
        keyboard = [
            [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def subscription_types() -> InlineKeyboardMarkup:
        """Клавиатура выбора типа подписки"""
        keyboard = [
            [InlineKeyboardButton("💎 Премиум", 
                                callback_data=f"{Keyboards.SUBSCRIPTION_TYPE_CALLBACK}:premium")],
            [InlineKeyboardButton("👑 ПРО ПЛЮС", 
                                callback_data=f"{Keyboards.SUBSCRIPTION_TYPE_CALLBACK}:proplus")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def subscription_periods(subscription_type: str) -> InlineKeyboardMarkup:
        """Клавиатура выбора периода подписки"""
        if subscription_type == "premium":
            keyboard = [
                [InlineKeyboardButton("💎 1 месяц", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:premium_1month"),
                 InlineKeyboardButton("49₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:premium_1month")],
                [InlineKeyboardButton("💎 3 месяца", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:premium_3months"),
                 InlineKeyboardButton("119₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:premium_3months")],
                [InlineKeyboardButton("💎 6 месяцев", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:premium_6months"),
                 InlineKeyboardButton("199₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:premium_6months")],
                [InlineKeyboardButton("💎 1 год", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:premium_1year"),
                 InlineKeyboardButton("349₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:premium_1year")]
            ]
        else:  # proplus
            keyboard = [
                [InlineKeyboardButton("👑 1 месяц", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:proplus_1month"),
                 InlineKeyboardButton("99₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:proplus_1month")],
                [InlineKeyboardButton("👑 3 месяца", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:proplus_3months"),
                 InlineKeyboardButton("249₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:proplus_3months")],
                [InlineKeyboardButton("👑 6 месяцев", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:proplus_6months"),
                 InlineKeyboardButton("449₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:proplus_6months")],
                [InlineKeyboardButton("👑 1 год", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:proplus_1year"),
                 InlineKeyboardButton("799₽", 
                                    callback_data=f"{Keyboards.SUBSCRIPTION_PAY_CALLBACK}:proplus_1year")]
            ]
        
        keyboard.append([InlineKeyboardButton("⬅️ Назад к типам", 
                                            callback_data=f"{Keyboards.SUBSCRIPTION_CALLBACK}")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def subscription_payment(payment_url: str) -> InlineKeyboardMarkup:
        """Клавиатура оплаты подписки"""
        keyboard = [
            [InlineKeyboardButton("💳 Оплатить", url=payment_url)],
            [InlineKeyboardButton("❌ Отменить", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def subscription_status(has_subscription: bool = False) -> InlineKeyboardMarkup:
        """Клавиатура управления премиум подпиской"""
        keyboard = []
        if has_subscription:
            keyboard.append([InlineKeyboardButton("💎 Продлить подписку", 
                                                callback_data=Keyboards.SUBSCRIPTION_EXTEND_CALLBACK)])
            keyboard.append([InlineKeyboardButton("🔔 Уведомления", 
                                                callback_data=Keyboards.PREMIUM_MENU_CALLBACK)])
        else:
            keyboard.append([InlineKeyboardButton("💎 Оформить подписку", 
                                                callback_data=Keyboards.SUBSCRIPTION_CALLBACK)])
        
        keyboard.append([InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def premium_menu() -> InlineKeyboardMarkup:
        """Меню для премиум подписчиков"""
        keyboard = [
            [InlineKeyboardButton("🔔 Настройка уведомлений", 
                                callback_data=Keyboards.NOTIFY_ADVANCED_CALLBACK)],
            [InlineKeyboardButton("🏗️ Отслеживание улучшений", 
                                callback_data=Keyboards.BUILDING_TRACKER_CALLBACK)],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def building_tracker_menu(is_active: bool = False) -> InlineKeyboardMarkup:
        """Меню управления отслеживанием улучшений зданий"""
        keyboard = []
        
        if is_active:
            keyboard.append([InlineKeyboardButton("🔴 Отключить отслеживание", 
                                                callback_data=Keyboards.BUILDING_TOGGLE_CALLBACK)])
            keyboard.append([InlineKeyboardButton("ℹ️ Статус: Активно", callback_data="noop")])
        else:
            keyboard.append([InlineKeyboardButton("🟢 Активировать отслеживание", 
                                                callback_data=Keyboards.BUILDING_TOGGLE_CALLBACK)])
            keyboard.append([InlineKeyboardButton("ℹ️ Статус: Неактивно", callback_data="noop")])
        
        keyboard.append([InlineKeyboardButton("⬅️ Назад к премиум меню", 
                                            callback_data=Keyboards.PREMIUM_MENU_CALLBACK)])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def notification_menu(is_premium: bool = False) -> InlineKeyboardMarkup:
        """Меню уведомлений"""
        keyboard = [
            [InlineKeyboardButton("🔔 Включить уведомления за 1 час до КВ", 
                                callback_data=Keyboards.NOTIFY_TOGGLE_CALLBACK)]
        ]
        
        if is_premium:
            keyboard.append([InlineKeyboardButton("⚙️ Настройка доп. уведомлений", 
                                                callback_data=Keyboards.NOTIFY_ADVANCED_CALLBACK)])
            keyboard.append([InlineKeyboardButton("🏗️ Отслеживание улучшений зданий", 
                                                callback_data=Keyboards.BUILDING_TRACKER_CALLBACK)])
        
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def notification_advanced_menu() -> ReplyKeyboardMarkup:
        """Меню расширенных настроек уведомлений для премиум пользователей"""
        keyboard = [
            [KeyboardButton("🔔 Уведомление 1 (Нажмите для настройки)")],
            [KeyboardButton("🔔 Уведомление 2 (Нажмите для настройки)")],
            [KeyboardButton("🔔 Уведомление 3 (Нажмите для настройки)")],
            [KeyboardButton("✅ Включить все уведомления")],
            [KeyboardButton("⬅️ Назад в главное меню")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def profile_manager_menu(profiles: List[Dict[str, Any]], max_profiles: int) -> InlineKeyboardMarkup:
        """Меню менеджера профилей для премиум пользователей"""
        keyboard = []
        
        # Добавляем кнопки для каждого профиля
        for i, profile in enumerate(profiles):
            profile_name = profile.get('profile_name') or f"Профиль {i+1}"
            player_name = profile.get('player_name', 'Неизвестно')
            text = f"👤 {profile_name} ({player_name})"
            if profile.get('is_primary'):
                text = f"⭐ {text}"
            
            keyboard.append([InlineKeyboardButton(text, 
                                                callback_data=f"{Keyboards.PROFILE_SELECT_CALLBACK}:{profile['player_tag']}")])
        
        # Кнопка добавления нового профиля (если не достигнут лимит)
        if len(profiles) < max_profiles:
            keyboard.append([InlineKeyboardButton("➕ Добавить профиль", 
                                                callback_data=Keyboards.PROFILE_ADD_CALLBACK)])
        
        # Кнопка удаления профиля (если есть профили)
        if profiles:
            keyboard.append([InlineKeyboardButton("🗑️ Удалить профиль", 
                                                callback_data=Keyboards.PROFILE_DELETE_CALLBACK)])
        
        keyboard.append([InlineKeyboardButton("⬅️ Назад в меню профиля", callback_data="profile_menu")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def profile_delete_menu(profiles: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Меню выбора профиля для удаления"""
        keyboard = []
        
        for i, profile in enumerate(profiles):
            profile_name = profile.get('profile_name') or f"Профиль {i+1}"
            player_name = profile.get('player_name', 'Неизвестно')
            text = f"🗑️ {profile_name} ({player_name})"
            
            keyboard.append([InlineKeyboardButton(text, 
                                                callback_data=f"{Keyboards.PROFILE_DELETE_CONFIRM_CALLBACK}:{profile['player_tag']}")])
        
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data=Keyboards.PROFILE_MANAGER_CALLBACK)])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod 
    def get_subscription_max_profiles(subscription_type: str) -> int:
        """Получение максимального количества профилей для типа подписки"""
        if subscription_type.startswith("premium"):
            return 3
        elif subscription_type.startswith("proplus") or subscription_type.startswith("pro"):
            return 5
        return 1  # Для обычных пользователей только 1 профиль

    @staticmethod
    def linked_clans_menu(linked_clans: List[Dict[str, Any]], max_clans: int) -> InlineKeyboardMarkup:
        """Меню привязанных кланов"""
        keyboard = []
        
        # Добавляем кнопки для каждого привязанного клана
        for clan in linked_clans:
            clan_name = clan.get('clan_name', 'Неизвестный клан')
            slot_number = clan.get('slot_number', 1)
            keyboard.append([
                InlineKeyboardButton(
                    f"🛡 {clan_name}", 
                    callback_data=f"{Keyboards.LINKED_CLAN_SELECT_CALLBACK}:{clan['clan_tag']}"
                ),
                InlineKeyboardButton(
                    f"🗑️ Удалить", 
                    callback_data=f"{Keyboards.LINKED_CLAN_DELETE_CALLBACK}:{slot_number}"
                )
            ])
        
        # Добавляем пустые слоты для привязки новых кланов
        current_count = len(linked_clans)
        for slot in range(current_count + 1, max_clans + 1):
            keyboard.append([
                InlineKeyboardButton(
                    f"➕ Слот {slot} (пустой)", 
                    callback_data=f"{Keyboards.LINKED_CLAN_ADD_CALLBACK}:{slot}"
                )
            ])
        
        # Кнопка возврата в главное меню
        keyboard.append([
            InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)


        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def community_center_menu() -> InlineKeyboardMarkup:
        """Меню центра сообщества"""
        keyboard = [
            [InlineKeyboardButton("🏗️ Стоимости строений", 
                                callback_data=Keyboards.BUILDING_COSTS_CALLBACK)],
            [InlineKeyboardButton("🏰 Расстановки баз", 
                                callback_data=Keyboards.BASE_LAYOUTS_CALLBACK)],
            [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def building_costs_menu() -> InlineKeyboardMarkup:
        """Меню выбора категории зданий"""
        keyboard = [
            [InlineKeyboardButton("🏰 Оборона", callback_data=f"{Keyboards.BUILDING_CATEGORY_CALLBACK}:defense")],
            [InlineKeyboardButton("⚔️ Армия", callback_data=f"{Keyboards.BUILDING_CATEGORY_CALLBACK}:army")],
            [InlineKeyboardButton("💎 Ресурсы", callback_data=f"{Keyboards.BUILDING_CATEGORY_CALLBACK}:resources")],
            [InlineKeyboardButton("👑 Герои", callback_data=f"{Keyboards.BUILDING_CATEGORY_CALLBACK}:heroes")],
            [InlineKeyboardButton("🔨 Деревня строителя", callback_data=f"{Keyboards.BUILDING_CATEGORY_CALLBACK}:builder")],
            [InlineKeyboardButton("⬅️ Центр сообщества", callback_data=Keyboards.COMMUNITY_CENTER_CALLBACK)]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def building_category_menu(category: str) -> InlineKeyboardMarkup:
        """Меню выбора конкретного здания в категории"""
        keyboard = []
        
        if category == "defense":
            buildings = [
                ("🏹 Башня лучниц", "archer_tower"),
                ("💣 Пушка", "cannon"),
                ("🏰 Мортира", "mortar"),
                ("✈️ Воздушная защита", "air_defense"),
                ("🧙 Башня магов", "wizard_tower"),
                ("💨 Воздушная метла", "air_sweeper"),
                ("⚡ Скрытая тесла", "hidden_tesla"),
                ("💥 Башня-бомба", "bomb_tower"),
                ("🏹 Адский лук", "x_bow"),
                ("🔥 Башня ада", "inferno_tower"),
                ("🦅 Орлиная артиллерия", "eagle_artillery"),
                ("💫 Разброс", "scattershot"),
                ("🧱 Стены", "walls")
            ]
        elif category == "army":
            buildings = [
                ("🏺 Казарма", "army_camp"),
                ("⚔️ Учебные казармы", "barracks"),
                ("🔬 Лаборатория", "laboratory"),
                ("🪄 Фабрика заклинаний", "spell_factory"),
                ("🏰 Замок клана", "clan_castle"),
                ("🏺 Тёмные казармы", "dark_barracks"),
                ("🌟 Фабрика тёмных заклинаний", "dark_spell_factory")
            ]
        elif category == "resources":
            buildings = [
                ("🥇 Золотая шахта", "gold_mine"),
                ("💜 Накопитель эликсира", "elixir_collector"),
                ("⚫ Бур тёмного эликсира", "dark_elixir_drill"),
                ("🏛️ Хранилище золота", "gold_storage"),
                ("🏛️ Хранилище эликсира", "elixir_storage"),
                ("🏛️ Хранилище тёмного эликсира", "dark_elixir_storage")
            ]
        elif category == "heroes":
            buildings = [
                ("👑 Король варваров", "barbarian_king"),
                ("👸 Королева лучниц", "archer_queen"),
                ("🧙‍♂️ Великий хранитель", "grand_warden"),
                ("⚔️ Королевский чемпион", "royal_champion")
            ]
        elif category == "builder":
            buildings = [
                ("🏗️ Зал строителя", "builder_hall"),
                ("⚔️ Казармы БД", "builder_barracks"),
                ("🏹 Башня лучниц БД", "builder_archer_tower"),
                ("💣 Пушка БД", "builder_cannon"),
                ("🔥 Печь БД", "builder_firecrackers"),
                ("⚡ Тесла БД", "builder_tesla"),
                ("💣 Гигантская пушка БД", "giant_cannon"),
                ("🏹 Мега тесла БД", "mega_tesla")
            ]
        else:
            buildings = []
        
        # Добавляем кнопки для каждого здания (по 2 в ряд)
        for i in range(0, len(buildings), 2):
            row = []
            for j in range(2):
                if i + j < len(buildings):
                    name, building_id = buildings[i + j]
                    row.append(InlineKeyboardButton(name, 
                                                  callback_data=f"{Keyboards.BUILDING_DETAIL_CALLBACK}:{building_id}"))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("⬅️ Категории", callback_data=Keyboards.BUILDING_COSTS_CALLBACK)])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def base_layouts_menu() -> InlineKeyboardMarkup:
        """Меню выбора уровня ТХ для расстановок баз"""
        keyboard = []
        
        # Создаем кнопки для ТХ от 1 до 16 (по 4 в ряд)
        for i in range(1, 17, 4):
            row = []
            for j in range(4):
                if i + j <= 16:
                    th_level = i + j
                    row.append(InlineKeyboardButton(f"ТХ {th_level}", 
                                                  callback_data=f"{Keyboards.BASE_LAYOUTS_TH_CALLBACK}:{th_level}"))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("⬅️ Центр сообщества", callback_data=Keyboards.COMMUNITY_CENTER_CALLBACK)])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def achievements_menu(player_tag: str, page: int = 1, sort_type: str = "progress", total_pages: int = 1) -> InlineKeyboardMarkup:
        """Меню достижений с пагинацией и сортировкой"""
        keyboard = []
        
        # Кнопки сортировки
        sort_buttons = []
        if sort_type != "progress":
            sort_buttons.append(InlineKeyboardButton("📈 По прогрессу", 
                                                   callback_data=f"{Keyboards.ACHIEVEMENTS_SORT_CALLBACK}:{player_tag}:progress:1"))
        if sort_type != "profitability":
            sort_buttons.append(InlineKeyboardButton("💰 По прибыли", 
                                                   callback_data=f"{Keyboards.ACHIEVEMENTS_SORT_CALLBACK}:{player_tag}:profitability:1"))
        
        if sort_buttons:
            # Разбиваем кнопки по 2 в ряд, если их больше одной
            for i in range(0, len(sort_buttons), 2):
                row = sort_buttons[i:i+2]
                keyboard.append(row)
        
        # Навигация по страницам
        nav_buttons = []
        
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️", 
                                                   callback_data=f"{Keyboards.ACHIEVEMENTS_PAGE_CALLBACK}:{player_tag}:{sort_type}:{page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"))
        
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️", 
                                                   callback_data=f"{Keyboards.ACHIEVEMENTS_PAGE_CALLBACK}:{player_tag}:{sort_type}:{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Кнопка возврата к профилю
        keyboard.append([InlineKeyboardButton("⬅️ Назад к профилю", 
                                            callback_data=f"{Keyboards.PROFILE_CALLBACK}:{player_tag}")])
        
        return InlineKeyboardMarkup(keyboard)


# Перечисления для сортировки
class WarSort:
    """Типы сортировки войн"""
    RECENT = "recent"
    WINS = "wins"
    LOSSES = "losses"
    CWL_ONLY = "cwl_only"


class MemberSort:
    """Типы сортировки участников"""
    ROLE = "role"
    TROPHIES = "trophies"
    DONATIONS = "donations"
    NAME = "name"


class MemberView:
    """Типы отображения участников"""
    COMPACT = "compact"
    DETAILED = "detailed"