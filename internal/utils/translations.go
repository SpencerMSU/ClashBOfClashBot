package utils

// TranslationManager управляет переводами для бота
type TranslationManager struct {
	supportedLanguages map[string]bool
	defaultLanguage    string
	translations       map[string]map[string]interface{}
}

// NewTranslationManager создает новый менеджер переводов
func NewTranslationManager() *TranslationManager {
	tm := &TranslationManager{
		supportedLanguages: map[string]bool{"ru": true, "en": true},
		defaultLanguage:    "ru",
		translations:       make(map[string]map[string]interface{}),
	}

	// Инициализируем переводы
	tm.initTranslations()
	return tm
}

func (tm *TranslationManager) initTranslations() {
	// Русский язык
	tm.translations["ru"] = map[string]interface{}{
		// CWL Messages
		"cwl_not_participating": "❌ Клан не участвует в текущем сезоне ЛВК.",
		"cwl_back_to_clan":      "⬅️ Назад к клану",

		// Analyzer Messages
		"analyzer_coming_soon":    "🤖 <b>Анализатор войн</b>\n\n🚧 <b>В разработке</b>\n\nАнализатор находится в стадии разработки.\nКогда-то он будет, но не сейчас.\n\nСледите за обновлениями!",
		"analyzer_refresh_error": "🤖 <b>Анализатор войн</b>\n\n🚧 Функция временно недоступна.\nПопробуйте позже.",

		// Common Error Messages
		"generic_error":      "❌ Произошла ошибка. Попробуйте позже.",
		"loading_error":      "❌ Произошла ошибка при загрузке данных.",
		"player_not_found":   "❌ Игрок не найден.",
		"clan_not_found":     "❌ Клан не найден.",

		// Button Text
		"back_to_main_menu": "⬅️ Главное меню",
		"back_to_clan":      "⬅️ Назад к клану",

		// Achievement Names (Russian translations)
		"achievement_names": map[string]string{
			"Bigger Coffers":            "Большие Сундуки",
			"Get those Goblins!":        "Поймай Гоблинов!",
			"Bigger & Better":           "Больше и Лучше",
			"Nice and Tidy":             "Чисто и Аккуратно",
			"Release the Beasts":        "Выпусти Зверей",
			"Gold Grab":                 "Захват Золота",
			"Elixir Escapade":           "Эликсирное Приключение",
			"Sweet Victory!":            "Сладкая Победа!",
			"Empire Builder":            "Строитель Империи",
			"Wall Buster":               "Разрушитель Стен",
			"Humiliator":                "Унизитель",
			"Union Buster":              "Разрушитель Союзов",
			"Conqueror":                 "Завоеватель",
			"Unbreakable":               "Несокрушимый",
			"Friend in Need":            "Друг в Беде",
			"Mortar Mauler":             "Сокрушитель Мортир",
			"Heroic Heist":              "Героическое Ограбление",
			"League All-Star":           "Звезда Лиги",
			"X-Bow Exterminator":        "Истребитель Адских Луков",
			"Firefighter":               "Пожарный",
			"War Hero":                  "Герой Войны",
			"Treasurer":                 "Казначей",
			"Anti-Artillery":            "Противоартиллерийский",
			"Sharing is caring":         "Делиться значит заботиться",
			"Keep your account safe!":   "Сохрани свой аккаунт в безопасности!",
			"Master Engineering":        "Мастер Инженерии",
			"Next Generation Model":     "Модель Нового Поколения",
			"Un-Build It":               "Разстрой Это",
			"Champion Builder":          "Чемпион Строитель",
			"High Gear":                 "Высокая Передача",
			"Hidden Treasures":          "Скрытые Сокровища",
			"Games Champion":            "Чемпион Игр",
			"Dragon Slayer":             "Убийца Драконов",
			"War League Legend":         "Легенда Лиги Войн",
			"Keep your account safe":    "Сохрани свой аккаунт в безопасности",
			"Well Seasoned":             "Хорошо Приправленный",
			"Shattered and Scattered":   "Разбитый и Рассеянный",
			"Not So Easy This Time":     "На Этот Раз Не Так Просто",
			"Bust This!":                "Разруши Это!",
			"Superb Work":               "Превосходная Работа",
			"Siege Sharer":              "Дележка Осадных Машин",
			"Aggressive Artillery":      "Агрессивная Артиллерия",
			"Counterspell":              "Контрзаклинание",
			"Monolith Masher":           "Сокрушитель Монолитов",
			"Ungrateful Child":          "Неблагодарное Дитя",
		},

		// Achievement Descriptions (Russian)
		"achievement_descriptions": map[string]string{
			"Bigger Coffers":            "Улучшите хранилища золота",
			"Get those Goblins!":        "Победите гоблинов в одиночных миссиях",
			"Bigger & Better":           "Улучшайте ратушу",
			"Nice and Tidy":             "Уберите препятствия с базы",
			"Release the Beasts":        "Разблокируйте войска",
			"Gold Grab":                 "Украдите золото в мультиплеерных боях",
			"Elixir Escapade":           "Украдите эликсир в мультиплеерных боях",
			"Sweet Victory!":            "Побеждайте в мультиплеерных боях",
			"Empire Builder":            "Выигрывайте трофеи в мультиплеерных боях",
			"Wall Buster":               "Улучшайте стены",
			"Humiliator":                "Побеждайте игроков с более высокой ратушей",
			"Union Buster":              "Уничтожайте замки кланов в боях",
			"Conqueror":                 "Выигрывайте атаки в клановых войнах",
			"Unbreakable":               "Успешно защищайтесь в клановых войнах",
			"Friend in Need":            "Донатьте войска членам клана",
			"Mortar Mauler":             "Уничтожайте мортиры в боях",
			"Heroic Heist":              "Украдите темный эликсир в боях",
			"League All-Star":           "Выигрывайте звезды в войнах",
			"X-Bow Exterminator":        "Уничтожайте адские луки в боях",
			"Firefighter":               "Уничтожайте башни ада в боях",
			"War Hero":                  "Выигрывайте звезды в клановых войнах",
			"Treasurer":                 "Донатьте войска в клановых войнах",
			"Anti-Artillery":            "Уничтожайте орлиные артиллерии в боях",
			"Sharing is caring":         "Донатьте заклинания членам клана",
			"Keep your account safe!":   "Защитите свой аккаунт (Supercell ID)",
			"Master Engineering":        "Улучшайте зал строителя",
			"Next Generation Model":     "Улучшайте боевую машину",
			"Un-Build It":               "Уничтожайте залы строителя в боях",
			"Champion Builder":          "Достигайте высоких трофеев в деревне строителя",
			"High Gear":                 "Прокачивайте боевую машину на максимум",
			"Hidden Treasures":          "Разрушайте здания в деревне строителя",
			"Games Champion":            "Выигрывайте звезды в клановых играх",
			"Dragon Slayer":             "Уничтожайте осадные машины в боях",
			"War League Legend":         "Выигрывайте звезды в лиге войн кланов",
			"Keep your account safe":    "Защитите свой аккаунт (Supercell ID)",
			"Well Seasoned":             "Участвуйте в сезонах клановых игр",
			"Shattered and Scattered":   "Уничтожайте разбросы в боях",
			"Not So Easy This Time":     "Уничтожайте гига-тесла в боях",
			"Bust This!":                "Уничтожайте гига-ад в боях",
			"Superb Work":               "Улучшайте зал строителя до максимума",
			"Siege Sharer":              "Донатьте осадные машины в войнах",
			"Aggressive Artillery":      "Уничтожайте осадные казармы в боях",
			"Counterspell":              "Уничтожайте фабрики заклинаний в боях",
			"Monolith Masher":           "Уничтожайте монолиты в боях",
			"Ungrateful Child":          "Уничтожайте статуи в боях",
		},
	}

	// Английский язык
	tm.translations["en"] = map[string]interface{}{
		// CWL Messages
		"cwl_not_participating": "❌ Clan is not participating in the current CWL season.",
		"cwl_back_to_clan":      "⬅️ Back to clan",

		// Analyzer Messages
		"analyzer_coming_soon":    "🤖 <b>War Analyzer</b>\n\n🚧 <b>Under Development</b>\n\nThe analyzer is under development.\nSomeday it will be, but not now.\n\nStay tuned for updates!",
		"analyzer_refresh_error": "🤖 <b>War Analyzer</b>\n\n🚧 Feature temporarily unavailable.\nTry again later.",

		// Common Error Messages
		"generic_error":      "❌ An error occurred. Please try again later.",
		"loading_error":      "❌ Error loading data.",
		"player_not_found":   "❌ Player not found.",
		"clan_not_found":     "❌ Clan not found.",

		// Button Text
		"back_to_main_menu": "⬅️ Main Menu",
		"back_to_clan":      "⬅️ Back to clan",

		// Achievement Names (English - original names stay as is)
		"achievement_names": map[string]string{},
	}
}

// GetUserLanguage определяет язык пользователя из языкового кода
func (tm *TranslationManager) GetUserLanguage(languageCode string) string {
	if languageCode == "" {
		return tm.defaultLanguage
	}

	// Берем первые 2 символа для языкового кода
	lang := languageCode
	if len(lang) > 2 {
		lang = lang[:2]
	}

	if tm.supportedLanguages[lang] {
		return lang
	}

	return tm.defaultLanguage
}

// GetText получает переведенный текст для пользователя
func (tm *TranslationManager) GetText(languageCode, key, defaultValue string) string {
	userLang := tm.GetUserLanguage(languageCode)

	// Пытаемся получить текст для языка пользователя
	if langTranslations, ok := tm.translations[userLang]; ok {
		if text, ok := langTranslations[key]; ok {
			if str, ok := text.(string); ok {
				return str
			}
		}
	}

	// Fallback to default language
	if defLangTranslations, ok := tm.translations[tm.defaultLanguage]; ok {
		if text, ok := defLangTranslations[key]; ok {
			if str, ok := text.(string); ok {
				return str
			}
		}
	}

	// Если ничего не найдено, возвращаем значение по умолчанию или ключ
	if defaultValue != "" {
		return defaultValue
	}
	return key
}

// GetAchievementName получает переведенное название достижения
func (tm *TranslationManager) GetAchievementName(languageCode, originalName string) string {
	userLang := tm.GetUserLanguage(languageCode)

	if langTranslations, ok := tm.translations[userLang]; ok {
		if achievementNames, ok := langTranslations["achievement_names"]; ok {
			if namesMap, ok := achievementNames.(map[string]string); ok {
				if name, ok := namesMap[originalName]; ok {
					return name
				}
			}
		}
	}

	return originalName
}

// GetAchievementDescription получает описание достижения (что делать для прогресса)
func (tm *TranslationManager) GetAchievementDescription(languageCode, originalName string) string {
	userLang := tm.GetUserLanguage(languageCode)

	if langTranslations, ok := tm.translations[userLang]; ok {
		if achievementDescriptions, ok := langTranslations["achievement_descriptions"]; ok {
			if descriptionsMap, ok := achievementDescriptions.(map[string]string); ok {
				if description, ok := descriptionsMap[originalName]; ok {
					return description
				}
			}
		}
	}

	return ""
}

// Глобальный экземпляр менеджера переводов
var GlobalTranslationManager = NewTranslationManager()
