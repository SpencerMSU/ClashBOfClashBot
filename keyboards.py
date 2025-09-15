"""
Клавиатуры и кнопки для бота - аналог Java Keyboards
"""
from typing import List, Optional
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
    SUBSCRIPTION_PERIOD_CALLBACK = "sub_period"
    SUBSCRIPTION_PAY_CALLBACK = "sub_pay"
    
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
    def subscription_periods() -> InlineKeyboardMarkup:
        """Клавиатура выбора периода премиум подписки"""
        keyboard = [
            [InlineKeyboardButton("💎 1 месяц - 299₽", 
                                callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:1month")],
            [InlineKeyboardButton("💎 3 месяца - 799₽", 
                                callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:3months")],
            [InlineKeyboardButton("💎 6 месяцев - 1499₽", 
                                callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:6months")],
            [InlineKeyboardButton("💎 1 год - 2799₽", 
                                callback_data=f"{Keyboards.SUBSCRIPTION_PERIOD_CALLBACK}:1year")]
        ]
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
    def subscription_status() -> InlineKeyboardMarkup:
        """Клавиатура управления премиум подпиской"""
        keyboard = [
            [InlineKeyboardButton("💎 Продлить премиум", 
                                callback_data=Keyboards.SUBSCRIPTION_CALLBACK)],
            [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
        ]
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