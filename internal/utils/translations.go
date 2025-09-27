package utils

// TranslationManager manages translations for the bot - exact copy from Python translations.py
type TranslationManager struct {
	supportedLanguages []string
	defaultLanguage    string
	translations       map[string]map[string]string
}

// NewTranslationManager creates a new translation manager
func NewTranslationManager() *TranslationManager {
	tm := &TranslationManager{
		supportedLanguages: []string{"ru", "en"},
		defaultLanguage:    "ru",
		translations:       make(map[string]map[string]string),
	}
	
	tm.initTranslations()
	return tm
}

// initTranslations initializes all translations - exact copy from Python __init__
func (tm *TranslationManager) initTranslations() {
	// Russian translations
	tm.translations["ru"] = map[string]string{
		// CWL Messages
		"cwl_not_participating":         "❌ Клан не участвует в текущем сезоне ЛВК.",
		"cwl_back_to_clan":             "⬅️ Назад к клану",
		
		// Analyzer Messages
		"analyzer_coming_soon":          "🤖 <b>Анализатор войн</b>\\n\\n🚧 <b>В разработке</b>\\n\\nАнализатор находится в стадии разработки.\\nКогда-то он будет, но не сейчас.\\n\\nСледите за обновлениями!",
		
		// General Error Messages
		"error_occurred":               "❌ Произошла ошибка. Попробуйте позже.",
		"invalid_tag":                  "❌ Неверный формат тега. Пример: #ABC123DEF",
		"player_not_found":             "❌ Игрок не найден. Проверьте правильность тега.",
		"clan_not_found":               "❌ Клан не найден. Проверьте правильность тега.",
		"no_data_available":            "📭 Нет данных для отображения.",
		
		// Button Texts
		"back":                         "⬅️ Назад",
		"cancel":                       "❌ Отмена",
		"confirm":                      "✅ Подтвердить",
		"menu":                         "📱 Меню",
		"refresh":                      "🔄 Обновить",
		"settings":                     "⚙️ Настройки",
		
		// Subscription Messages
		"subscription_required":        "💎 Эта функция доступна только для премиум пользователей.",
		"subscription_expired":         "⏰ Ваша подписка истекла. Продлите для доступа к премиум функциям.",
		"subscription_active":          "✅ У вас активная подписка до {date}",
		
		// Profile Messages
		"profile_linked":               "✅ Профиль игрока привязан успешно!",
		"profile_already_linked":       "⚠️ Этот профиль уже привязан к вашему аккаунту.",
		"profile_limit_reached":        "❌ Достигнут лимит профилей для вашего типа подписки.",
		"primary_profile_set":          "✅ Основной профиль установлен.",
		
		// War Messages
		"war_not_found":               "❌ Война не найдена или клан не участвует в войне.",
		"war_in_preparation":          "⏳ Война на стадии подготовки.",
		"war_ended":                   "🏁 Война завершена.",
		"no_attacks":                  "⚔️ Атак еще не было.",
		
		// Building Tracker Messages
		"building_tracker_enabled":    "✅ Отслеживание улучшений зданий включено.",
		"building_tracker_disabled":   "❌ Отслеживание улучшений зданий отключено.",
		"building_upgrade_detected":   "🔨 Обнаружено улучшение здания: {building} до уровня {level}",
		
		// Achievement translations - exact copy from Python
		"Friend in Need":               "Друг в Беде",
		"Mortar Mauler":               "Сокрушитель Мортир", 
		"Heroic Heist":                "Героическое Ограбление",
		"League All-Star":             "Звезда Лиги",
		"X-Bow Exterminator":          "Истребитель Адских Луков",
		"Firefighter":                 "Пожарный",
		"War Hero":                    "Герой Войны",
		"Treasurer":                   "Казначей",
		"Anti-Artillery":              "Противоартиллерийский",
		"Sharing is caring":           "Делиться значит заботиться",
		"Keep your village safe":      "Сохраните свою деревню в безопасности",
		"Master Engineering":          "Мастер Техники",
		"Next Generation Model":       "Модель Нового Поколения",
		"Un-Build It":                 "Разрушить Это",
		"Champion Builder":            "Чемпион Строитель",
		"High Gear":                   "Высокая Скорость",
		"Hidden Treasures":            "Скрытые Сокровища",
		"Games Champion":              "Чемпион Игр",
		"Dragon Slayer":               "Убийца Драконов",
		"War League Legend":           "Легенда Лиги Войн",
		"Bigger Coffers":              "Большие Сундуки",
		"Get those Goblins!":          "Поймай Гоблинов!",
		"Bigger & Better":             "Больше и Лучше",
		"Nice and Tidy":               "Чисто и Аккуратно",
		"Release the Beasts":          "Выпусти Зверей",
		"Gold Grab":                   "Захват Золота",
		"Elixir Escapade":             "Эликсирное Приключение",
		"Sweet Victory!":              "Сладкая Победа!",
		"Empire Builder":              "Строитель Империи",
		"Wall Buster":                 "Разрушитель Стен",
		"Humiliator":                  "Унизитель",
		"Union Buster":                "Разрушитель Союзов",
		"Conqueror":                   "Завоеватель",
		"Unbreakable":                 "Несокрушимый",
	}
	
	// English translations
	tm.translations["en"] = map[string]string{
		// CWL Messages
		"cwl_not_participating":         "❌ Clan is not participating in current CWL season.",
		"cwl_back_to_clan":             "⬅️ Back to clan",
		
		// Analyzer Messages
		"analyzer_coming_soon":          "🤖 <b>War Analyzer</b>\\n\\n🚧 <b>Under Development</b>\\n\\nThe analyzer is currently under development.\\nIt will be available someday, but not now.\\n\\nStay tuned for updates!",
		
		// General Error Messages
		"error_occurred":               "❌ An error occurred. Please try again later.",
		"invalid_tag":                  "❌ Invalid tag format. Example: #ABC123DEF",
		"player_not_found":             "❌ Player not found. Check the tag is correct.",
		"clan_not_found":               "❌ Clan not found. Check the tag is correct.",
		"no_data_available":            "📭 No data available to display.",
		
		// Button Texts
		"back":                         "⬅️ Back",
		"cancel":                       "❌ Cancel",
		"confirm":                      "✅ Confirm",
		"menu":                         "📱 Menu",
		"refresh":                      "🔄 Refresh",
		"settings":                     "⚙️ Settings",
		
		// Subscription Messages
		"subscription_required":        "💎 This feature is available only for premium users.",
		"subscription_expired":         "⏰ Your subscription has expired. Renew for premium features access.",
		"subscription_active":          "✅ You have active subscription until {date}",
		
		// Profile Messages
		"profile_linked":               "✅ Player profile linked successfully!",
		"profile_already_linked":       "⚠️ This profile is already linked to your account.",
		"profile_limit_reached":        "❌ Profile limit reached for your subscription type.",
		"primary_profile_set":          "✅ Primary profile has been set.",
		
		// War Messages
		"war_not_found":               "❌ War not found or clan is not in war.",
		"war_in_preparation":          "⏳ War is in preparation phase.",
		"war_ended":                   "🏁 War has ended.",
		"no_attacks":                  "⚔️ No attacks yet.",
		
		// Building Tracker Messages
		"building_tracker_enabled":    "✅ Building upgrade tracking enabled.",
		"building_tracker_disabled":   "❌ Building upgrade tracking disabled.",
		"building_upgrade_detected":   "🔨 Building upgrade detected: {building} to level {level}",
		
		// Achievement translations remain in English (original names)
		"Friend in Need":               "Friend in Need",
		"Mortar Mauler":               "Mortar Mauler",
		"Heroic Heist":                "Heroic Heist",
		"League All-Star":             "League All-Star",
		"X-Bow Exterminator":          "X-Bow Exterminator",
		"Firefighter":                 "Firefighter",
		"War Hero":                    "War Hero",
		"Treasurer":                   "Treasurer",
		"Anti-Artillery":              "Anti-Artillery",
		"Sharing is caring":           "Sharing is caring",
		"Keep your village safe":      "Keep your village safe",
		"Master Engineering":          "Master Engineering",
		"Next Generation Model":       "Next Generation Model",
		"Un-Build It":                 "Un-Build It",
		"Champion Builder":            "Champion Builder",
		"High Gear":                   "High Gear",
		"Hidden Treasures":            "Hidden Treasures",
		"Games Champion":              "Games Champion",
		"Dragon Slayer":               "Dragon Slayer",
		"War League Legend":           "War League Legend",
		"Bigger Coffers":              "Bigger Coffers",
		"Get those Goblins!":          "Get those Goblins!",
		"Bigger & Better":             "Bigger & Better",
		"Nice and Tidy":               "Nice and Tidy",
		"Release the Beasts":          "Release the Beasts",
		"Gold Grab":                   "Gold Grab",
		"Elixir Escapade":             "Elixir Escapade",
		"Sweet Victory!":              "Sweet Victory!",
		"Empire Builder":              "Empire Builder",
		"Wall Buster":                 "Wall Buster",
		"Humiliator":                  "Humiliator",
		"Union Buster":                "Union Buster",
		"Conqueror":                   "Conqueror",
		"Unbreakable":                 "Unbreakable",
	}
}

// GetText returns translated text - exact copy from Python get_text()
func (tm *TranslationManager) GetText(key string, language string) string {
	// Use default language if language not supported
	if !tm.isLanguageSupported(language) {
		language = tm.defaultLanguage
	}
	
	// Get translation
	if langTranslations, exists := tm.translations[language]; exists {
		if translation, exists := langTranslations[key]; exists {
			return translation
		}
	}
	
	// Fallback to default language
	if language != tm.defaultLanguage {
		if defaultTranslations, exists := tm.translations[tm.defaultLanguage]; exists {
			if translation, exists := defaultTranslations[key]; exists {
				return translation
			}
		}
	}
	
	// Return key if no translation found
	return key
}

// GetUserLanguage determines user language from language code - exact copy from Python
func (tm *TranslationManager) GetUserLanguage(languageCode string) string {
	if languageCode == "" {
		return tm.defaultLanguage
	}
	
	// Extract language from language code (e.g., "en-US" -> "en")
	if len(languageCode) >= 2 {
		lang := languageCode[:2]
		if tm.isLanguageSupported(lang) {
			return lang
		}
	}
	
	return tm.defaultLanguage
}

// isLanguageSupported checks if language is supported
func (tm *TranslationManager) isLanguageSupported(language string) bool {
	for _, supported := range tm.supportedLanguages {
		if supported == language {
			return true
		}
	}
	return false
}

// GetSupportedLanguages returns list of supported languages
func (tm *TranslationManager) GetSupportedLanguages() []string {
	return tm.supportedLanguages
}

// GetDefaultLanguage returns default language
func (tm *TranslationManager) GetDefaultLanguage() string {
	return tm.defaultLanguage
}

// TranslateAchievement translates achievement name - exact copy from Python
func (tm *TranslationManager) TranslateAchievement(achievementName string, language string) string {
	return tm.GetText(achievementName, language)
}

// AddTranslation adds a new translation key
func (tm *TranslationManager) AddTranslation(key, language, translation string) {
	if tm.translations[language] == nil {
		tm.translations[language] = make(map[string]string)
	}
	tm.translations[language][key] = translation
}

// HasTranslation checks if translation exists
func (tm *TranslationManager) HasTranslation(key, language string) bool {
	if langTranslations, exists := tm.translations[language]; exists {
		_, exists := langTranslations[key]
		return exists
	}
	return false
}

// Global translation manager instance
var GlobalTranslationManager = NewTranslationManager()