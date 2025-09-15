"""
Клавиатуры и кнопки для бота - аналог Java Keyboards
"""
from typing import List, Optional, Dict
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
    CLAN_MEMBERS_BTN = "👥 Список участников"
    CLAN_WARLOG_BTN = "⚔️ Последние войны"
    BACK_TO_CLAN_MENU_BTN = "⬅️ Назад в меню кланов"
    CLAN_CURRENT_CWL_BTN = "⚔️ Текущее ЛВК"
    CLAN_CWL_BONUS_BTN = "🏆 Бонусы ЛВК"
    NOTIFICATIONS_BTN = "🔔 Уведомления о КВ"
    CLAN_CURRENT_WAR_BTN = "⚔️ Текущая КВ"
    SUBSCRIPTION_BTN = "💎 Премиум подписка"
    
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
    SUBSCRIPTION_TYPE_CALLBACK = "sub_type"
    SUBSCRIPTION_PERIOD_CALLBACK = "sub_period"
    SUBSCRIPTION_PAY_CALLBACK = "sub_pay"
    PREMIUM_MENU_CALLBACK = "premium_menu"
    NOTIFY_ADVANCED_CALLBACK = "notify_advanced"
    NOTIFY_CUSTOM_CALLBACK = "notify_custom"
    
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Главное меню бота"""
        keyboard = [
            [KeyboardButton(Keyboards.PROFILE_BTN), KeyboardButton(Keyboards.CLAN_BTN)],
            [KeyboardButton(Keyboards.NOTIFICATIONS_BTN)]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def profile_menu(player_name: Optional[str] = None) -> ReplyKeyboardMarkup:
        """Меню профиля"""
        keyboard = []
        
        if player_name:
            keyboard.append([KeyboardButton(f"{Keyboards.MY_PROFILE_PREFIX} ({player_name})")])
        else:
            keyboard.append([KeyboardButton(Keyboards.LINK_ACC_BTN)])
        
        # Всегда добавляем кнопку подписки, чтобы она была видна всем пользователям
        keyboard.append([KeyboardButton(Keyboards.SUBSCRIPTION_BTN)])
        
        keyboard.extend([
            [KeyboardButton(Keyboards.SEARCH_PROFILE_BTN)],
            [KeyboardButton(Keyboards.MY_CLAN_BTN)] if player_name else [],
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
            [InlineKeyboardButton("🏆 ЛВК", callback_data="cwl_info")]
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
                                                callback_data=Keyboards.SUBSCRIPTION_CALLBACK)])
            keyboard.append([InlineKeyboardButton("👑 Меню премиум", 
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
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
        ]
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