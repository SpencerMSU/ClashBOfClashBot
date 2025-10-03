package bot

import (
	"fmt"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

// Button text constants
const (
	ProfileBtn              = "👤 Профиль"
	ClanBtn                 = "🛡 Клан"
	LinkAccBtn              = "🔗 Привязать аккаунт"
	SearchProfileBtn        = "🔍 Найти профиль по тегу"
	MyClanBtn               = "🛡 Мой клан (из профиля)"
	SearchClanBtn           = "🔍 Найти клан по тегу"
	BackBtn                 = "⬅️ Назад в главное меню"
	MyProfilePrefix         = "👤 Мой профиль"
	ProfileManagerBtn       = "👥 Менеджер профилей"
	ClanMembersBtn          = "👥 Список участников"
	ClanWarlogBtn           = "⚔️ Последние войны"
	BackToClanMenuBtn       = "⬅️ Назад в меню кланов"
	ClanCurrentCWLBtn       = "⚔️ Текущее ЛВК"
	ClanCWLBonusBtn         = "🏆 Бонусы ЛВК"
	NotificationsBtn        = "🔔 Уведомления"
	ClanCurrentWarBtn       = "⚔️ Текущая КВ"
	SubscriptionBtn         = "💎 Премиум подписка"
	LinkedClansBtn          = "🔗 Привязанные кланы"
	CommunityCenterBtn      = "🏛️ Центр сообщества"
	AchievementsBtn         = "🏆 Достижения"
	AnalyzerBtn             = "🤖 Анализатор"
	RequestWarScanBtn       = "📊 Нет данных о войнах? Запросить!"
)

// Callback data constants
const (
	MembersCallback                 = "members"
	WarListCallback                 = "warlist"
	WarInfoCallback                 = "warinfo"
	ProfileCallback                 = "profile"
	NotifyToggleCallback            = "notify_toggle"
	CWLBonusCallback                = "cwlbonus"
	MembersSortCallback             = "members_sort"
	MembersViewCallback             = "members_view"
	SubscriptionCallback            = "subscription"
	SubscriptionExtendCallback      = "subscription_extend"
	SubscriptionTypeCallback        = "sub_type"
	SubscriptionPeriodCallback      = "sub_period"
	SubscriptionPayCallback         = "sub_pay"
	PremiumMenuCallback             = "premium_menu"
	NotifyAdvancedCallback          = "notify_advanced"
	NotifyCustomCallback            = "notify_custom"
	BuildingTrackerCallback         = "building_tracker"
	BuildingToggleCallback          = "building_toggle"
	ProfileManagerCallback          = "profile_manager"
	ProfileSelectCallback           = "profile_select"
	ProfileDeleteCallback           = "profile_delete"
	ProfileDeleteConfirmCallback    = "profile_delete_confirm"
	ProfileAddCallback              = "profile_add"
	LinkedClansCallback             = "linked_clans"
	LinkedClanSelectCallback        = "linked_clan_select"
	LinkedClanAddCallback           = "linked_clan_add"
	LinkedClanDeleteCallback        = "linked_clan_delete"
	CommunityCenterCallback         = "community_center"
	BuildingCostsCallback           = "building_costs"
	BuildingCategoryCallback        = "building_category"
	BuildingDetailCallback          = "building_detail"
	BaseLayoutsCallback             = "base_layouts"
	BaseLayoutsTHCallback           = "base_layouts_th"
	AchievementsCallback            = "achievements"
	AchievementsSortCallback        = "achievements_sort"
	AchievementsPageCallback        = "achievements_page"
	CWLBonusDistributionCallback    = "cwl_bonus_distribution"
	WarScanRequestCallback          = "war_scan_request"
)

// MainMenu returns the main menu keyboard
func MainMenu() tgbotapi.ReplyKeyboardMarkup {
	keyboard := [][]tgbotapi.KeyboardButton{
		{
			tgbotapi.NewKeyboardButton(ProfileBtn),
			tgbotapi.NewKeyboardButton(ClanBtn),
		},
		{
			tgbotapi.NewKeyboardButton(NotificationsBtn),
			tgbotapi.NewKeyboardButton(CommunityCenterBtn),
		},
		{
			tgbotapi.NewKeyboardButton(AnalyzerBtn),
		},
	}
	return tgbotapi.NewReplyKeyboard(keyboard...)
}

// ProfileMenu returns the profile menu keyboard
func ProfileMenu(playerName *string, hasPremium bool, profileCount int) tgbotapi.ReplyKeyboardMarkup {
	keyboard := [][]tgbotapi.KeyboardButton{}
	
	if hasPremium && profileCount > 0 {
		// For premium users with profiles, show profile manager
		keyboard = append(keyboard, []tgbotapi.KeyboardButton{
			tgbotapi.NewKeyboardButton(ProfileManagerBtn),
		})
	} else if playerName != nil && *playerName != "" {
		// For regular users or premium with single profile
		keyboard = append(keyboard, []tgbotapi.KeyboardButton{
			tgbotapi.NewKeyboardButton(fmt.Sprintf("%s (%s)", MyProfilePrefix, *playerName)),
		})
	} else {
		keyboard = append(keyboard, []tgbotapi.KeyboardButton{
			tgbotapi.NewKeyboardButton(LinkAccBtn),
		})
	}
	
	// Always add subscription button
	keyboard = append(keyboard, []tgbotapi.KeyboardButton{
		tgbotapi.NewKeyboardButton(SubscriptionBtn),
	})
	
	keyboard = append(keyboard, []tgbotapi.KeyboardButton{
		tgbotapi.NewKeyboardButton(SearchProfileBtn),
	})
	
	if playerName != nil || (hasPremium && profileCount > 0) {
		keyboard = append(keyboard, []tgbotapi.KeyboardButton{
			tgbotapi.NewKeyboardButton(MyClanBtn),
		})
	}
	
	keyboard = append(keyboard, []tgbotapi.KeyboardButton{
		tgbotapi.NewKeyboardButton(BackBtn),
	})
	
	return tgbotapi.NewReplyKeyboard(keyboard...)
}

// ClanMenu returns the clan menu keyboard
func ClanMenu(playerName *string, hasPremium bool, profileCount int) tgbotapi.ReplyKeyboardMarkup {
	keyboard := [][]tgbotapi.KeyboardButton{
		{tgbotapi.NewKeyboardButton(SearchClanBtn)},
		{tgbotapi.NewKeyboardButton(LinkedClansBtn)},
		{tgbotapi.NewKeyboardButton(RequestWarScanBtn)},
	}
	
	// Add "My clan" button if user has linked account
	if playerName != nil || (hasPremium && profileCount > 0) {
		keyboard = append(keyboard, []tgbotapi.KeyboardButton{
			tgbotapi.NewKeyboardButton(MyClanBtn),
		})
	}
	
	keyboard = append(keyboard, []tgbotapi.KeyboardButton{
		tgbotapi.NewKeyboardButton(BackBtn),
	})
	
	return tgbotapi.NewReplyKeyboard(keyboard...)
}

// ClanInspectionMenu returns the clan inspection inline keyboard
func ClanInspectionMenu() tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{
		{tgbotapi.NewInlineKeyboardButtonData("👥 Участники", MembersCallback)},
		{tgbotapi.NewInlineKeyboardButtonData("⚔️ История войн", WarListCallback)},
		{tgbotapi.NewInlineKeyboardButtonData("⚔️ Текущая война", "current_war")},
		{tgbotapi.NewInlineKeyboardButtonData("🏆 ЛВК", "cwl_info")},
		{tgbotapi.NewInlineKeyboardButtonData("💎 Распределение бонусов ЛВК", CWLBonusDistributionCallback)},
		{tgbotapi.NewInlineKeyboardButtonData("⬅️ Главное меню", "main_menu")},
	}
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// MembersPagination returns the members pagination inline keyboard
func MembersPagination(clanTag string, currentPage, totalPages int, sortType, viewType string) tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{}
	
	// Sort buttons
	sortButtons := []tgbotapi.InlineKeyboardButton{
		tgbotapi.NewInlineKeyboardButtonData("🎖 По роли",
			fmt.Sprintf("%s:%s:role:%s:%d", MembersSortCallback, clanTag, viewType, currentPage)),
		tgbotapi.NewInlineKeyboardButtonData("🏆 По трофеям",
			fmt.Sprintf("%s:%s:trophies:%s:%d", MembersSortCallback, clanTag, viewType, currentPage)),
	}
	keyboard = append(keyboard, sortButtons)
	
	// View buttons
	viewButtons := []tgbotapi.InlineKeyboardButton{
		tgbotapi.NewInlineKeyboardButtonData("📋 Компактно",
			fmt.Sprintf("%s:%s:%s:compact:%d", MembersViewCallback, clanTag, sortType, currentPage)),
		tgbotapi.NewInlineKeyboardButtonData("📄 Подробно",
			fmt.Sprintf("%s:%s:%s:detailed:%d", MembersViewCallback, clanTag, sortType, currentPage)),
	}
	keyboard = append(keyboard, viewButtons)
	
	// Navigation buttons
	navButtons := []tgbotapi.InlineKeyboardButton{}
	if currentPage > 1 {
		navButtons = append(navButtons, tgbotapi.NewInlineKeyboardButtonData("⬅️",
			fmt.Sprintf("%s:%s:%s:%s:%d", MembersSortCallback, clanTag, sortType, viewType, currentPage-1)))
	}
	
	navButtons = append(navButtons, tgbotapi.NewInlineKeyboardButtonData(
		fmt.Sprintf("%d/%d", currentPage, totalPages), "noop"))
	
	if currentPage < totalPages {
		navButtons = append(navButtons, tgbotapi.NewInlineKeyboardButtonData("➡️",
			fmt.Sprintf("%s:%s:%s:%s:%d", MembersSortCallback, clanTag, sortType, viewType, currentPage+1)))
	}
	
	keyboard = append(keyboard, navButtons)
	
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// WarListPagination returns the war list pagination inline keyboard
func WarListPagination(clanTag string, currentPage, totalPages int, sortOrder string) tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{}
	
	// Sort buttons
	sortButtons := []tgbotapi.InlineKeyboardButton{
		tgbotapi.NewInlineKeyboardButtonData("📅 Недавние",
			fmt.Sprintf("%s:%s:recent:%d", WarListCallback, clanTag, currentPage)),
		tgbotapi.NewInlineKeyboardButtonData("🏆 Победы",
			fmt.Sprintf("%s:%s:wins:%d", WarListCallback, clanTag, currentPage)),
		tgbotapi.NewInlineKeyboardButtonData("❌ Поражения",
			fmt.Sprintf("%s:%s:losses:%d", WarListCallback, clanTag, currentPage)),
	}
	keyboard = append(keyboard, sortButtons)
	
	// Navigation buttons
	navButtons := []tgbotapi.InlineKeyboardButton{}
	if currentPage > 1 {
		navButtons = append(navButtons, tgbotapi.NewInlineKeyboardButtonData("⬅️",
			fmt.Sprintf("%s:%s:%s:%d", WarListCallback, clanTag, sortOrder, currentPage-1)))
	}
	
	navButtons = append(navButtons, tgbotapi.NewInlineKeyboardButtonData(
		fmt.Sprintf("%d/%d", currentPage, totalPages), "noop"))
	
	if currentPage < totalPages {
		navButtons = append(navButtons, tgbotapi.NewInlineKeyboardButtonData("➡️",
			fmt.Sprintf("%s:%s:%s:%d", WarListCallback, clanTag, sortOrder, currentPage+1)))
	}
	
	keyboard = append(keyboard, navButtons)
	
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// NotificationToggle returns the notification toggle inline keyboard
func NotificationToggle() tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{
		{tgbotapi.NewInlineKeyboardButtonData("🔔 Включить все уведомления", "enable_all_notifications")},
		{tgbotapi.NewInlineKeyboardButtonData("🔕 Отключить все уведомления", "disable_all_notifications")},
		{tgbotapi.NewInlineKeyboardButtonData("⬅️ Главное меню", "main_menu")},
	}
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// SubscriptionTypes returns the subscription types inline keyboard
func SubscriptionTypes() tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{
		{tgbotapi.NewInlineKeyboardButtonData("💎 Premium", fmt.Sprintf("%s:premium", SubscriptionTypeCallback))},
		{tgbotapi.NewInlineKeyboardButtonData("💎💎 Pro Plus", fmt.Sprintf("%s:pro_plus", SubscriptionTypeCallback))},
		{tgbotapi.NewInlineKeyboardButtonData("⬅️ Главное меню", "main_menu")},
	}
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// SubscriptionPeriods returns the subscription periods inline keyboard for a given type
func SubscriptionPeriods(subscriptionType string) tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{}
	
	if subscriptionType == "premium" {
		keyboard = append(keyboard,
			[]tgbotapi.InlineKeyboardButton{tgbotapi.NewInlineKeyboardButtonData("💎 7 дней - 50₽", 
				fmt.Sprintf("%s:premium_7", SubscriptionPeriodCallback))},
			[]tgbotapi.InlineKeyboardButton{tgbotapi.NewInlineKeyboardButtonData("💎 30 дней - 150₽", 
				fmt.Sprintf("%s:premium_30", SubscriptionPeriodCallback))},
			[]tgbotapi.InlineKeyboardButton{tgbotapi.NewInlineKeyboardButtonData("💎 90 дней - 350₽", 
				fmt.Sprintf("%s:premium_90", SubscriptionPeriodCallback))},
			[]tgbotapi.InlineKeyboardButton{tgbotapi.NewInlineKeyboardButtonData("💎 180 дней - 600₽", 
				fmt.Sprintf("%s:premium_180", SubscriptionPeriodCallback))},
		)
	} else if subscriptionType == "pro_plus" {
		keyboard = append(keyboard,
			[]tgbotapi.InlineKeyboardButton{tgbotapi.NewInlineKeyboardButtonData("💎💎 7 дней - 100₽", 
				fmt.Sprintf("%s:pro_plus_7", SubscriptionPeriodCallback))},
			[]tgbotapi.InlineKeyboardButton{tgbotapi.NewInlineKeyboardButtonData("💎💎 30 дней - 300₽", 
				fmt.Sprintf("%s:pro_plus_30", SubscriptionPeriodCallback))},
			[]tgbotapi.InlineKeyboardButton{tgbotapi.NewInlineKeyboardButtonData("💎💎 90 дней - 700₽", 
				fmt.Sprintf("%s:pro_plus_90", SubscriptionPeriodCallback))},
			[]tgbotapi.InlineKeyboardButton{tgbotapi.NewInlineKeyboardButtonData("💎💎 180 дней - 1200₽", 
				fmt.Sprintf("%s:pro_plus_180", SubscriptionPeriodCallback))},
		)
	}
	
	keyboard = append(keyboard, []tgbotapi.InlineKeyboardButton{
		tgbotapi.NewInlineKeyboardButtonData("⬅️ Назад", SubscriptionCallback),
	})
	
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// SubscriptionPayment returns the subscription payment inline keyboard
func SubscriptionPayment(paymentURL string) tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{
		{tgbotapi.NewInlineKeyboardButtonURL("💳 Оплатить", paymentURL)},
		{tgbotapi.NewInlineKeyboardButtonData("⬅️ Главное меню", "main_menu")},
	}
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// BackToMain returns a simple back to main menu keyboard
func BackToMain() tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{
		{tgbotapi.NewInlineKeyboardButtonData("⬅️ Главное меню", "main_menu")},
	}
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// CommunityCenterMenu returns the community center menu keyboard
func CommunityCenterMenu() tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{
		{tgbotapi.NewInlineKeyboardButtonData("🏗️ Стоимость зданий", BuildingCostsCallback)},
		{tgbotapi.NewInlineKeyboardButtonData("🗺️ Базы", BaseLayoutsCallback)},
		{tgbotapi.NewInlineKeyboardButtonData("⬅️ Главное меню", "main_menu")},
	}
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// BuildingCostsMenu returns the building costs menu keyboard
func BuildingCostsMenu() tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{
		{tgbotapi.NewInlineKeyboardButtonData("🏰 Защита", fmt.Sprintf("%s:defense", BuildingCategoryCallback))},
		{tgbotapi.NewInlineKeyboardButtonData("⚔️ Армия", fmt.Sprintf("%s:army", BuildingCategoryCallback))},
		{tgbotapi.NewInlineKeyboardButtonData("💰 Ресурсы", fmt.Sprintf("%s:resources", BuildingCategoryCallback))},
		{tgbotapi.NewInlineKeyboardButtonData("👑 Герои", fmt.Sprintf("%s:heroes", BuildingCategoryCallback))},
		{tgbotapi.NewInlineKeyboardButtonData("⬅️ Назад", CommunityCenterCallback)},
	}
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// PremiumMenu returns the premium features menu keyboard
func PremiumMenu() tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{
		{tgbotapi.NewInlineKeyboardButtonData("🏗️ Трекер зданий", BuildingTrackerCallback)},
		{tgbotapi.NewInlineKeyboardButtonData("🔔 Персональные уведомления", NotifyAdvancedCallback)},
		{tgbotapi.NewInlineKeyboardButtonData("⬅️ Главное меню", "main_menu")},
	}
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// BuildingTrackerMenu returns the building tracker menu keyboard
func BuildingTrackerMenu(isActive bool) tgbotapi.InlineKeyboardMarkup {
	keyboard := [][]tgbotapi.InlineKeyboardButton{}
	
	if isActive {
		keyboard = append(keyboard, []tgbotapi.InlineKeyboardButton{
			tgbotapi.NewInlineKeyboardButtonData("🔴 Отключить трекер", 
				fmt.Sprintf("%s:false", BuildingToggleCallback)),
		})
	} else {
		keyboard = append(keyboard, []tgbotapi.InlineKeyboardButton{
			tgbotapi.NewInlineKeyboardButtonData("🟢 Включить трекер", 
				fmt.Sprintf("%s:true", BuildingToggleCallback)),
		})
	}
	
	keyboard = append(keyboard, []tgbotapi.InlineKeyboardButton{
		tgbotapi.NewInlineKeyboardButtonData("⬅️ Назад", PremiumMenuCallback),
	})
	
	return tgbotapi.NewInlineKeyboardMarkup(keyboard...)
}

// GetSubscriptionMaxProfiles returns the max profiles for a subscription type
func GetSubscriptionMaxProfiles(subscriptionType string) int {
	if subscriptionType == "pro_plus_7" || subscriptionType == "pro_plus_30" || 
	   subscriptionType == "pro_plus_90" || subscriptionType == "pro_plus_180" {
		return 3
	}
	return 1
}
