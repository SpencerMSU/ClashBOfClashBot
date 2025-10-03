package bot

import (
	"ClashBOfClashBot/config"
	"ClashBOfClashBot/internal/api"
	"ClashBOfClashBot/internal/database"
	"ClashBOfClashBot/internal/models"
	"fmt"
	"log"
	"strings"
	"time"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

// MessageGenerator generates and formats messages for the bot
type MessageGenerator struct {
	db        *database.DatabaseService
	cocClient *api.CocApiClient
	config    *config.Config
	
	// Constants for formatting
	MembersPerPage int
	WarsPerPage    int
	
	// Role translations
	roleTranslations map[string]string
}

// NewMessageGenerator creates a new message generator
func NewMessageGenerator(db *database.DatabaseService, cocClient *api.CocApiClient, cfg *config.Config) *MessageGenerator {
	return &MessageGenerator{
		db:             db,
		cocClient:      cocClient,
		config:         cfg,
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
	return fmt.Sprintf("%s", strings.ReplaceAll(fmt.Sprintf("%d", n), "", ""))
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
	
	playerData, err := m.cocClient.GetPlayerInfo(playerTag)
	if err != nil || playerData == nil {
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
		msg := tgbotapi.NewMessage(chatID, "❌ Ошибка при привязке аккаунта. Попробуйте позже.")
		msg.ReplyMarkup = ProfileMenu(nil, false, 0)
		_, err := bot.Send(msg)
		return err
	}
	
	playerName := playerData["name"].(string)
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
	
	playerData, err := m.cocClient.GetPlayerInfo(playerTag)
	if err != nil || playerData == nil {
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

// Close closes any resources held by the message generator
func (m *MessageGenerator) Close() error {
	// Nothing to close for now
	return nil
}
