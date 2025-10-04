package bot

import (
	"ClashBOfClashBot/config"
	"ClashBOfClashBot/internal/api"
	"ClashBOfClashBot/internal/database"
	"ClashBOfClashBot/internal/models"
	"ClashBOfClashBot/internal/services"
	"fmt"
	"log"
	"strings"
	"time"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

// MessageGenerator generates and formats messages for the bot
type MessageGenerator struct {
	db             *database.DatabaseService
	cocClient      *api.CocApiClient
	config         *config.Config
	paymentService *services.YooKassaService

	// Constants for formatting
	MembersPerPage int
	WarsPerPage    int

	// Role translations
	roleTranslations map[string]string
} // NewMessageGenerator creates a new message generator
func NewMessageGenerator(db *database.DatabaseService, cocClient *api.CocApiClient, cfg *config.Config) *MessageGenerator {
	// Create payment service
	paymentService := services.NewYooKassaService("", "", cfg.BotUsername)

	return &MessageGenerator{
		db:             db,
		cocClient:      cocClient,
		config:         cfg,
		paymentService: paymentService,
		MembersPerPage: 10,
		WarsPerPage:    10,
		roleTranslations: map[string]string{
			"leader":   "👑 Глава",
			"coLeader": "⚜️ Соруководитель",
			"admin":    "🔰 Старейшина",
			"member":   "👤 Участник",
		},
	}
}

// ========== Utility Methods ==========

// formatDateTime formats ISO datetime string to readable format in Moscow time
func (m *MessageGenerator) formatDateTime(isoDateTimeStr string) string {
	// Parse ISO datetime (format: 20250919T044950.000Z)
	t, err := time.Parse("20060102T150405.000Z", isoDateTimeStr)
	if err != nil {
		// Try alternative format without milliseconds
		t, err = time.Parse("20060102T150405Z", isoDateTimeStr)
		if err != nil {
			log.Printf("Error parsing datetime %s: %v", isoDateTimeStr, err)
			return isoDateTimeStr
		}
	}

	// Convert to Moscow time (UTC+3)
	moscowLocation := time.FixedZone("MSK", 3*60*60)
	moscowTime := t.In(moscowLocation)

	// Format to readable form: "19.09.2025 07:49"
	return moscowTime.Format("02.01.2006 15:04")
}

// escapeMarkdown escapes special characters for Markdown
func (m *MessageGenerator) escapeMarkdown(text string) string {
	replacer := strings.NewReplacer(
		"_", "\\_",
		"*", "\\*",
		"[", "\\[",
		"]", "\\]",
		"(", "\\(",
		")", "\\)",
		"~", "\\~",
		"`", "\\`",
		">", "\\>",
		"#", "\\#",
		"+", "\\+",
		"-", "\\-",
		"=", "\\=",
		"|", "\\|",
		"{", "\\{",
		"}", "\\}",
		".", "\\.",
		"!", "\\!",
	)
	return replacer.Replace(text)
}

// formatNumber formats a number with thousand separators
func (m *MessageGenerator) formatNumber(n int) string {
	if n < 1000 {
		return fmt.Sprintf("%d", n)
	}
	return strings.ReplaceAll(fmt.Sprintf("%d", n), "", "")
}

// ========== Profile and Player Methods ==========

// HandleProfileMenuRequest handles profile menu request
func (m *MessageGenerator) HandleProfileMenuRequest(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID

	// Check user subscription
	subscription, err := m.db.GetSubscription(chatID)
	hasPremium := err == nil && subscription != nil && subscription.IsActive && !subscription.IsExpired()

	var playerName *string
	profileCount := 0

	if hasPremium {
		// For premium users, check profiles
		profiles, err := m.db.GetUserProfiles(chatID)
		if err == nil {
			profileCount = len(profiles)
			if profileCount > 0 {
				// Get primary profile or first profile
				for _, profile := range profiles {
					if profile.IsPrimary {
						playerData, err := m.cocClient.GetPlayerInfo(profile.PlayerTag)
						if err == nil && playerData != nil {
							name := playerData["name"].(string)
							playerName = &name
						}
						break
					}
				}
			}
		}
	} else {
		// For regular users
		user, err := m.db.FindUser(chatID)
		if err == nil && user != nil {
			playerData, err := m.cocClient.GetPlayerInfo(user.PlayerTag)
			if err == nil && playerData != nil {
				name := playerData["name"].(string)
				playerName = &name
			}
		}
	}

	msg := tgbotapi.NewMessage(chatID, "Меню профиля:")
	msg.ReplyMarkup = ProfileMenu(playerName, hasPremium, profileCount)
	_, err = bot.Send(msg)
	return err
}

// HandleMyProfileRequest handles request to view own profile
func (m *MessageGenerator) HandleMyProfileRequest(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID

	user, err := m.db.FindUser(chatID)
	if err != nil || user == nil {
		msg := tgbotapi.NewMessage(chatID, "Вы не привязали свой аккаунт. Используйте кнопку \"🔗 Привязать аккаунт\".")
		msg.ReplyMarkup = ProfileMenu(nil, false, 0)
		_, err := bot.Send(msg)
		return err
	}

	return m.DisplayPlayerInfo(update, bot, user.PlayerTag, nil, nil, false)
}

// HandleLinkAccount handles account linking
func (m *MessageGenerator) HandleLinkAccount(update *tgbotapi.Update, bot *tgbotapi.BotAPI, playerTag string) error {
	chatID := update.Message.Chat.ID

	log.Printf("Attempting to link account for user %d with tag %s", chatID, playerTag)

	playerData, err := m.cocClient.GetPlayerInfo(playerTag)
	if err != nil {
		log.Printf("Error getting player info for tag %s: %v", playerTag, err)

		var errorMsg string
		if strings.Contains(err.Error(), "403") {
			errorMsg = "❌ Проблема с API ключом. Обратитесь к администратору."
		} else if strings.Contains(err.Error(), "404") {
			errorMsg = "❌ Игрок с таким тегом не найден. Проверьте правильность тега."
		} else {
			errorMsg = fmt.Sprintf("❌ Ошибка при поиске игрока: %v", err)
		}

		msg := tgbotapi.NewMessage(chatID, errorMsg)
		msg.ReplyMarkup = ProfileMenu(nil, false, 0)
		_, err := bot.Send(msg)
		return err
	}

	if playerData == nil {
		log.Printf("Player data is nil for tag %s", playerTag)
		msg := tgbotapi.NewMessage(chatID, "❌ Игрок с таким тегом не найден. Проверьте правильность тега.")
		msg.ReplyMarkup = ProfileMenu(nil, false, 0)
		_, err := bot.Send(msg)
		return err
	}

	user := &models.User{
		TelegramID: chatID,
		PlayerTag:  playerTag,
	}

	err = m.db.SaveUser(user)
	if err != nil {
		log.Printf("Error saving user %d with tag %s: %v", chatID, playerTag, err)
		msg := tgbotapi.NewMessage(chatID, "❌ Ошибка при привязке аккаунта. Попробуйте позже.")
		msg.ReplyMarkup = ProfileMenu(nil, false, 0)
		_, err := bot.Send(msg)
		return err
	}

	playerName := playerData["name"].(string)
	log.Printf("Successfully linked account for user %d: %s (%s)", chatID, playerName, playerTag)

	msg := tgbotapi.NewMessage(chatID, fmt.Sprintf(
		"✅ Аккаунт успешно привязан!\n"+
			"👤 Игрок: %s\n"+
			"🏷 Тег: %s",
		playerName, playerTag))
	msg.ReplyMarkup = ProfileMenu(&playerName, false, 0)
	_, err = bot.Send(msg)
	return err
}

// DisplayPlayerInfo displays player information
func (m *MessageGenerator) DisplayPlayerInfo(update *tgbotapi.Update, bot *tgbotapi.BotAPI,
	playerTag string, keyboard *tgbotapi.InlineKeyboardMarkup,
	backKeyboard *tgbotapi.InlineKeyboardMarkup, fromCallback bool) error {

	chatID := update.Message.Chat.ID

	// Show searching message
	searchMsg := tgbotapi.NewMessage(chatID, "🔍 Поиск игрока...")
	sentMsg, err := bot.Send(searchMsg)
	if err != nil {
		return err
	}

	log.Printf("Searching for player with tag: %s", playerTag)

	playerData, err := m.cocClient.GetPlayerInfo(playerTag)
	if err != nil {
		log.Printf("Error getting player info for tag %s: %v", playerTag, err)

		var errorMsg string
		if strings.Contains(err.Error(), "403") {
			errorMsg = "❌ Проблема с API ключом. Обратитесь к администратору."
		} else if strings.Contains(err.Error(), "404") {
			errorMsg = "❌ Игрок с таким тегом не найден.\nПроверьте правильность введенного тега."
		} else {
			errorMsg = fmt.Sprintf("❌ Ошибка при поиске игрока: %v", err)
		}

		editMsg := tgbotapi.NewEditMessageText(chatID, sentMsg.MessageID, errorMsg)
		bot.Send(editMsg)

		msg := tgbotapi.NewMessage(chatID, "Выберите действие:")
		msg.ReplyMarkup = MainMenu()
		bot.Send(msg)
		return nil
	}

	if playerData == nil {
		log.Printf("Player data is nil for tag %s", playerTag)
		editMsg := tgbotapi.NewEditMessageText(chatID, sentMsg.MessageID,
			"❌ Игрок с таким тегом не найден.\nПроверьте правильность введенного тега.")
		bot.Send(editMsg)

		msg := tgbotapi.NewMessage(chatID, "Выберите действие:")
		msg.ReplyMarkup = MainMenu()
		bot.Send(msg)
		return nil
	}

	// Format player information
	message := m.formatPlayerInfo(playerData)

	// Create keyboard with achievements button
	var profileKeyboard [][]tgbotapi.InlineKeyboardButton
	achievementsBtn := tgbotapi.NewInlineKeyboardButtonData("🏆 Достижения",
		fmt.Sprintf("%s:%s", AchievementsCallback, playerTag))
	profileKeyboard = append(profileKeyboard, []tgbotapi.InlineKeyboardButton{achievementsBtn})

	// Add back keyboard buttons if provided
	if backKeyboard != nil {
		profileKeyboard = append(profileKeyboard, backKeyboard.InlineKeyboard...)
	}

	// Add keyboard buttons if provided
	if keyboard != nil {
		profileKeyboard = append(profileKeyboard, keyboard.InlineKeyboard...)
	}

	finalKeyboard := tgbotapi.NewInlineKeyboardMarkup(profileKeyboard...)

	editMsg := tgbotapi.NewEditMessageText(chatID, sentMsg.MessageID, message)
	editMsg.ParseMode = "Markdown"
	editMsg.ReplyMarkup = &finalKeyboard
	_, err = bot.Send(editMsg)
	return err
}

// formatPlayerInfo formats player data into a readable message
func (m *MessageGenerator) formatPlayerInfo(playerData map[string]interface{}) string {
	name := playerData["name"].(string)
	tag := playerData["tag"].(string)
	townHallLevel := int(playerData["townHallLevel"].(float64))
	expLevel := int(playerData["expLevel"].(float64))
	trophies := int(playerData["trophies"].(float64))

	message := fmt.Sprintf(
		"👤 *%s*\n"+
			"🏷 Тег: `%s`\n"+
			"🏰 Ратуша: %d\n"+
			"⭐ Уровень: %d\n"+
			"🏆 Трофеи: %d\n\n",
		m.escapeMarkdown(name), tag, townHallLevel, expLevel, trophies)

	// Add clan info if player is in a clan
	if clan, ok := playerData["clan"].(map[string]interface{}); ok {
		clanName := clan["name"].(string)
		clanTag := clan["tag"].(string)
		role, _ := clan["role"].(string)
		roleTranslation := m.roleTranslations[role]
		if roleTranslation == "" {
			roleTranslation = role
		}

		message += fmt.Sprintf(
			"🛡 Клан: %s\n"+
				"🏷 Тег клана: `%s`\n"+
				"👥 Роль: %s\n\n",
			m.escapeMarkdown(clanName), clanTag, roleTranslation)
	} else {
		message += "🛡 Клан: Не состоит в клане\n\n"
	}

	// Add war stats
	if warStars, ok := playerData["warStars"].(float64); ok {
		message += fmt.Sprintf("⭐ Звезд в войнах: %d\n", int(warStars))
	}
	if attackWins, ok := playerData["attackWins"].(float64); ok {
		message += fmt.Sprintf("⚔️ Побед в атаках: %d\n", int(attackWins))
	}
	if defenseWins, ok := playerData["defenseWins"].(float64); ok {
		message += fmt.Sprintf("🛡 Побед в защите: %d\n", int(defenseWins))
	}

	return message
}

// HandleMyClanRequest handles request to view own clan
func (m *MessageGenerator) HandleMyClanRequest(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID

	user, err := m.db.FindUser(chatID)
	if err != nil || user == nil {
		msg := tgbotapi.NewMessage(chatID, "Вы не привязали свой аккаунт. Используйте кнопку \"🔗 Привязать аккаунт\".")
		msg.ReplyMarkup = ProfileMenu(nil, false, 0)
		_, err := bot.Send(msg)
		return err
	}

	playerData, err := m.cocClient.GetPlayerInfo(user.PlayerTag)
	if err != nil || playerData == nil {
		msg := tgbotapi.NewMessage(chatID, "❌ Не удалось получить информацию о вашем профиле.")
		msg.ReplyMarkup = MainMenu()
		_, err := bot.Send(msg)
		return err
	}

	clan, ok := playerData["clan"].(map[string]interface{})
	if !ok {
		playerName := ""
		if name, ok := playerData["name"].(string); ok {
			playerName = name
		}
		msg := tgbotapi.NewMessage(chatID, "❌ Вы не состоите в клане или не удалось получить информацию о клане.")
		msg.ReplyMarkup = ProfileMenu(&playerName, false, 0)
		_, err := bot.Send(msg)
		return err
	}

	clanTag := clan["tag"].(string)
	return m.DisplayClanInfo(update, bot, clanTag)
}

// DisplayClanInfo displays clan information
func (m *MessageGenerator) DisplayClanInfo(update *tgbotapi.Update, bot *tgbotapi.BotAPI, clanTag string) error {
	chatID := update.Message.Chat.ID

	loadingMsg := tgbotapi.NewMessage(chatID, "🔍 Получение информации о клане...")
	sentMsg, err := bot.Send(loadingMsg)
	if err != nil {
		return err
	}

	clanData, err := m.cocClient.GetClanInfo(clanTag)
	if err != nil || clanData == nil {
		editMsg := tgbotapi.NewEditMessageText(chatID, sentMsg.MessageID,
			"❌ Клан с таким тегом не найден или ведутся тех работы на стороне хостинга/апи.")
		bot.Send(editMsg)
		return nil
	}

	message := m.formatClanInfo(clanData)

	// Create clan menu keyboard
	keyboard := ClanInspectionMenu()

	editMsg := tgbotapi.NewEditMessageText(chatID, sentMsg.MessageID, message)
	editMsg.ParseMode = "Markdown"
	editMsg.ReplyMarkup = &keyboard
	_, err = bot.Send(editMsg)
	return err
}

// formatClanInfo formats clan data into a readable message
func (m *MessageGenerator) formatClanInfo(clanData map[string]interface{}) string {
	name := clanData["name"].(string)
	tag := clanData["tag"].(string)
	clanLevel := int(clanData["clanLevel"].(float64))
	members := int(clanData["members"].(float64))

	message := fmt.Sprintf(
		"🛡 *%s*\n"+
			"🏷 Тег: `%s`\n"+
			"⭐ Уровень клана: %d\n"+
			"👥 Участников: %d/50\n\n",
		m.escapeMarkdown(name), tag, clanLevel, members)

	if clanPoints, ok := clanData["clanPoints"].(float64); ok {
		message += fmt.Sprintf("🏆 Очки клана: %d\n", int(clanPoints))
	}

	if warWins, ok := clanData["warWins"].(float64); ok {
		message += fmt.Sprintf("⚔️ Побед в войнах: %d\n", int(warWins))
	}

	if warWinStreak, ok := clanData["warWinStreak"].(float64); ok {
		message += fmt.Sprintf("🔥 Серия побед: %d\n", int(warWinStreak))
	}

	if description, ok := clanData["description"].(string); ok && description != "" {
		message += fmt.Sprintf("\n📝 Описание:\n%s\n", description)
	}

	return message
}

// ========== Notification Methods ==========

// HandleNotificationsMenu handles notifications menu
func (m *MessageGenerator) HandleNotificationsMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID

	msg := tgbotapi.NewMessage(chatID,
		"🔔 *Уведомления*\n\n"+
			"⏳ Функция управления уведомлениями в разработке...\n"+
			"Скоро вы сможете настраивать уведомления о войнах, донатах и других событиях.")
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = MainMenu()
	_, err := bot.Send(msg)
	return err
}

// ========== Subscription Methods ==========

// HandleSubscriptionMenu handles subscription menu
func (m *MessageGenerator) HandleSubscriptionMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID

	subscription, err := m.db.GetSubscription(chatID)

	var message string
	if err == nil && subscription != nil && subscription.IsActive && !subscription.IsExpired() {
		daysRemaining := subscription.DaysRemaining()
		message = fmt.Sprintf(
			"💎 *Ваша подписка*\n\n"+
				"✅ Активна\n"+
				"📦 Тип: %s\n"+
				"📅 Осталось дней: %d\n"+
				"📆 Дата окончания: %s\n\n"+
				"Хотите продлить подписку?",
			subscription.SubscriptionType, daysRemaining, subscription.EndDate)
	} else {
		message = "💎 *Подписки*\n\n" +
			"У вас нет активной подписки.\n" +
			"Выберите тип подписки для оформления:"
	}

	msg := tgbotapi.NewMessage(chatID, message)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = SubscriptionTypes()
	_, err = bot.Send(msg)
	return err
}

// ========== Community Center Methods ==========

// HandleCommunityCenterMenu handles community center menu
func (m *MessageGenerator) HandleCommunityCenterMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID

	message := "🏛 *Центр сообщества*\n\n" +
		"Добро пожаловать в центр сообщества!\n" +
		"Здесь вы можете найти полезную информацию и инструменты для игры.\n\n" +
		"📊 Стоимость улучшений зданий\n" +
		"🏗️ Рекомендуемые расстановки баз\n" +
		"📈 Статистика и аналитика\n"

	msg := tgbotapi.NewMessage(chatID, message)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = CommunityCenterMenu()
	_, err := bot.Send(msg)
	return err
}

// HandleBuildingCostsMenu handles building costs menu
func (m *MessageGenerator) HandleBuildingCostsMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID

	message := "🏗️ *Стоимость зданий*\n\n" +
		"⏳ Функция просмотра стоимости зданий в разработке...\n" +
		"Скоро вы сможете узнать стоимость и время улучшения всех зданий."

	msg := tgbotapi.NewMessage(chatID, message)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = MainMenu()
	_, err := bot.Send(msg)
	return err
}

// HandleAnalyzerMenu handles analyzer menu
func (m *MessageGenerator) HandleAnalyzerMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID

	user, err := m.db.FindUser(chatID)
	if err != nil || user == nil {
		msg := tgbotapi.NewMessage(chatID,
			"🤖 *Анализатор*\n\n"+
				"❌ Для использования анализатора необходимо привязать аккаунт.\n"+
				"Перейдите в профиль и привяжите ваш игровой аккаунт.")
		msg.ParseMode = "Markdown"
		msg.ReplyMarkup = MainMenu()
		_, err := bot.Send(msg)
		return err
	}

	message := "🤖 *Анализатор войн*\n\n" +
		"⏳ Функция анализа войн в разработке...\n" +
		"Скоро вы сможете получить детальный анализ текущих и прошлых войн вашего клана."

	msg := tgbotapi.NewMessage(chatID, message)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = MainMenu()
	_, err = bot.Send(msg)
	return err
}

// ========== Premium Methods ==========

// HandlePremiumMenu handles premium features menu
func (m *MessageGenerator) HandlePremiumMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID

	subscription, err := m.db.GetSubscription(chatID)
	hasPremium := err == nil && subscription != nil && subscription.IsActive && !subscription.IsExpired()

	var message string
	if hasPremium {
		message = "💎 *Premium функции*\n\n" +
			"✅ У вас активная подписка!\n\n" +
			"Доступные функции:\n" +
			"🏗️ Отслеживание улучшений зданий\n" +
			"🔔 Расширенные уведомления\n" +
			"📊 Продвинутая аналитика\n" +
			"👥 Множественные профили\n"
	} else {
		message = "💎 *Premium функции*\n\n" +
			"❌ У вас нет активной подписки\n\n" +
			"С подпиской доступны:\n" +
			"🏗️ Отслеживание улучшений зданий\n" +
			"🔔 Расширенные уведомления\n" +
			"📊 Продвинутая аналитика\n" +
			"👥 Множественные профили\n\n" +
			"Оформите подписку в меню подписок!"
	}

	msg := tgbotapi.NewMessage(chatID, message)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = PremiumMenu()
	_, err = bot.Send(msg)
	return err
}

// HandleBuildingTrackerMenu handles building tracker menu
func (m *MessageGenerator) HandleBuildingTrackerMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID

	subscription, err := m.db.GetSubscription(chatID)
	hasPremium := err == nil && subscription != nil && subscription.IsActive && !subscription.IsExpired()

	if !hasPremium {
		msg := tgbotapi.NewMessage(chatID,
			"❌ Отслеживание улучшений зданий доступно только с Premium подпиской.\n\n"+
				"Оформите подписку чтобы получить доступ к этой функции!")
		msg.ReplyMarkup = MainMenu()
		_, err := bot.Send(msg)
		return err
	}

	message := "🏗️ *Отслеживание улучшений*\n\n" +
		"⏳ Функция отслеживания улучшений зданий в разработке...\n" +
		"Скоро вы сможете получать уведомления об улучшениях зданий в реальном времени."

	msg := tgbotapi.NewMessage(chatID, message)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = MainMenu()
	_, err = bot.Send(msg)
	return err
}

// HandlePaymentRequest handles payment request for subscription
func (m *MessageGenerator) HandlePaymentRequest(update *tgbotapi.Update, bot *tgbotapi.BotAPI, subscriptionType string) error {
	var chatID int64
	var messageID int

	if update.CallbackQuery != nil {
		chatID = update.CallbackQuery.Message.Chat.ID
		messageID = update.CallbackQuery.Message.MessageID
	} else if update.Message != nil {
		chatID = update.Message.Chat.ID
	} else {
		return fmt.Errorf("invalid update type")
	}

	log.Printf("Processing payment request for subscription: %s", subscriptionType)

	// New subscription prices for the current format
	price := map[string]float64{
		// Premium
		"premium_7":   50.00,
		"premium_30":  150.00,
		"premium_90":  350.00,
		"premium_180": 600.00,
		// Pro Plus
		"pro_plus_7":   100.00,
		"pro_plus_30":  300.00,
		"pro_plus_90":  700.00,
		"pro_plus_180": 1200.00,
	}

	subscriptionNames := map[string]string{
		// Premium
		"premium_7":   "💎 Premium на 7 дней",
		"premium_30":  "💎 Premium на 30 дней",
		"premium_90":  "💎 Premium на 90 дней",
		"premium_180": "💎 Premium на 180 дней",
		// Pro Plus
		"pro_plus_7":   "💎💎 Pro Plus на 7 дней",
		"pro_plus_30":  "💎💎 Pro Plus на 30 дней",
		"pro_plus_90":  "💎💎 Pro Plus на 90 дней",
		"pro_plus_180": "💎💎 Pro Plus на 180 дней",
	}

	subscriptionPrice, exists := price[subscriptionType]
	if !exists {
		text := "❌ Неизвестный тип подписки"
		if update.CallbackQuery != nil {
			edit := tgbotapi.NewEditMessageText(chatID, messageID, text)
			bot.Send(edit)
		} else {
			msg := tgbotapi.NewMessage(chatID, text)
			bot.Send(msg)
		}
		return nil
	}

	subscriptionName := subscriptionNames[subscriptionType]
	if subscriptionName == "" {
		subscriptionName = subscriptionType
	}

	// Create real payment via YooKassa
	returnURL := fmt.Sprintf("https://t.me/%s", m.config.BotUsername)
	payment, err := m.paymentService.CreatePayment(chatID, subscriptionType, returnURL)
	if err != nil {
		log.Printf("Error creating payment for user %d, subscription %s: %v", chatID, subscriptionType, err)

		// Fallback: создаем простую ссылку для связи с поддержкой
		supportURL := fmt.Sprintf("https://t.me/%s?start=payment_support_%s", m.config.BotUsername, subscriptionType)

		text := fmt.Sprintf(
			"❌ Временные проблемы с платежной системой\n\n"+
				"💎 Подписка: %s\n"+
				"💰 Стоимость: %.0f ₽\n\n"+
				"🔗 [Связаться с поддержкой для оплаты](%s)\n\n"+
				"Извините за неудобства. Мы решаем проблему.",
			subscriptionName, subscriptionPrice, supportURL)

		keyboard := tgbotapi.NewInlineKeyboardMarkup(
			tgbotapi.NewInlineKeyboardRow(
				tgbotapi.NewInlineKeyboardButtonURL("📞 Поддержка", supportURL),
			),
			tgbotapi.NewInlineKeyboardRow(
				tgbotapi.NewInlineKeyboardButtonData("⬅️ Назад", "subscription"),
			),
		)

		if update.CallbackQuery != nil {
			edit := tgbotapi.NewEditMessageText(chatID, messageID, text)
			edit.ParseMode = "Markdown"
			edit.ReplyMarkup = &keyboard
			bot.Send(edit)
		} else {
			msg := tgbotapi.NewMessage(chatID, text)
			msg.ParseMode = "Markdown"
			msg.ReplyMarkup = keyboard
			bot.Send(msg)
		}
		return nil // Не возвращаем ошибку, так как показали пользователю альтернативу
	}

	log.Printf("Payment response: ID=%s, Status=%s, Confirmation=%+v", payment.ID, payment.Status, payment.Confirmation)

	paymentURL := payment.Confirmation.ConfirmationURL
	if paymentURL == "" {
		// Fallback to return URL if confirmation URL is not available
		paymentURL = payment.Confirmation.ReturnURL
		log.Printf("Using fallback URL: %s", paymentURL)
	}

	// Если все еще нет URL, создаем временный
	if paymentURL == "" {
		paymentURL = fmt.Sprintf("https://t.me/%s?start=payment_%s", m.config.BotUsername, payment.ID)
		log.Printf("Using telegram fallback URL: %s", paymentURL)
	}

	log.Printf("Final payment URL for user %d: %s", chatID, paymentURL)

	text := fmt.Sprintf(
		"💎 *Оплата подписки*\n\n"+
			"Тип: %s\n"+
			"Стоимость: %.0f ₽\n\n"+
			"🔗 [Нажмите для оплаты](%s)\n\n"+
			"После оплаты подписка будет активирована автоматически.",
		subscriptionName, subscriptionPrice, paymentURL)

	keyboard := tgbotapi.NewInlineKeyboardMarkup(
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonURL("💳 Оплатить", paymentURL),
		),
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonData("⬅️ Назад", "subscription"),
		),
	)

	if update.CallbackQuery != nil {
		edit := tgbotapi.NewEditMessageText(chatID, messageID, text)
		edit.ParseMode = "Markdown"
		edit.ReplyMarkup = &keyboard
		_, err := bot.Send(edit)
		return err
	} else {
		msg := tgbotapi.NewMessage(chatID, text)
		msg.ParseMode = "Markdown"
		msg.ReplyMarkup = keyboard
		_, err := bot.Send(msg)
		return err
	}
} // Close closes any resources held by the message generator
func (m *MessageGenerator) Close() error {
	// Nothing to close for now
	return nil
}
