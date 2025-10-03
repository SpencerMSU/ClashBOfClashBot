package bot

import (
	"ClashBOfClashBot/internal/utils"
	"fmt"
	"log"
	"strings"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

// MessageHandler handles text messages
type MessageHandler struct {
	messageGen *MessageGenerator
	userStates map[int64]utils.UserState // chatID -> state
}

// NewMessageHandler creates a new message handler
func NewMessageHandler(messageGen *MessageGenerator) *MessageHandler {
	return &MessageHandler{
		messageGen: messageGen,
		userStates: make(map[int64]utils.UserState),
	}
}

// HandleMessage processes incoming text messages
func (h *MessageHandler) HandleMessage(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	if update.Message == nil || update.Message.Text == "" {
		return nil
	}
	
	chatID := update.Message.Chat.ID
	text := strings.TrimSpace(update.Message.Text)
	
	// Check if user is in a state awaiting input
	if state, exists := h.userStates[chatID]; exists {
		return h.handleStateMessage(update, bot, text, state)
	}
	
	// Handle menu commands
	return h.handleMenuCommand(update, bot, text)
}

// handleStateMessage handles messages when user is in a specific state
func (h *MessageHandler) handleStateMessage(update *tgbotapi.Update, bot *tgbotapi.BotAPI, 
	text string, state utils.UserState) error {
	
	chatID := update.Message.Chat.ID
	
	// Check if the text is a menu command - if so, clear state and handle as menu
	if h.isMenuCommand(text) {
		delete(h.userStates, chatID)
		return h.handleMenuCommand(update, bot, text)
	}
	
	// Handle based on state
	switch state {
	case utils.AwaitingPlayerTagToLink:
		// TODO: Implement player tag linking
		msg := tgbotapi.NewMessage(chatID, "⏳ Функция привязки игрока в разработке...")
		msg.ReplyMarkup = MainMenu()
		bot.Send(msg)
		delete(h.userStates, chatID)
		
	case utils.AwaitingPlayerTagToSearch:
		// TODO: Implement player search
		msg := tgbotapi.NewMessage(chatID, "⏳ Функция поиска игрока в разработке...")
		msg.ReplyMarkup = MainMenu()
		bot.Send(msg)
		delete(h.userStates, chatID)
		
	case utils.AwaitingClanTagToSearch:
		// TODO: Implement clan search
		msg := tgbotapi.NewMessage(chatID, "⏳ Функция поиска клана в разработке...")
		msg.ReplyMarkup = MainMenu()
		bot.Send(msg)
		delete(h.userStates, chatID)
		
	default:
		delete(h.userStates, chatID)
	}
	
	return nil
}

// handleMenuCommand handles menu button commands
func (h *MessageHandler) handleMenuCommand(update *tgbotapi.Update, bot *tgbotapi.BotAPI, text string) error {
	chatID := update.Message.Chat.ID
	
	switch text {
	case ProfileBtn:
		return h.handleProfileMenu(update, bot)
		
	case ClanBtn:
		return h.handleClanMenu(update, bot)
		
	case NotificationsBtn:
		return h.handleNotificationsMenu(update, bot)
		
	case CommunityCenterBtn:
		return h.handleCommunityCenterMenu(update, bot)
		
	case AnalyzerBtn:
		return h.handleAnalyzerMenu(update, bot)
		
	case BackBtn:
		msg := tgbotapi.NewMessage(chatID, "Главное меню:")
		msg.ReplyMarkup = MainMenu()
		bot.Send(msg)
		
	case LinkAccBtn:
		msg := tgbotapi.NewMessage(chatID, 
			"🔗 Привяжите ваш игровой аккаунт\n\n"+
			"Введите ваш игровой тег (например: #2PP или 2PP):")
		bot.Send(msg)
		h.userStates[chatID] = utils.AwaitingPlayerTagToLink
		
	case SearchProfileBtn:
		msg := tgbotapi.NewMessage(chatID, 
			"🔍 Поиск игрока\n\n"+
			"Введите тег игрока (например: #2PP или 2PP):")
		bot.Send(msg)
		h.userStates[chatID] = utils.AwaitingPlayerTagToSearch
		
	case SearchClanBtn:
		msg := tgbotapi.NewMessage(chatID, 
			"🔍 Поиск клана\n\n"+
			"Введите тег клана (например: #2PPU или 2PPU):")
		bot.Send(msg)
		h.userStates[chatID] = utils.AwaitingClanTagToSearch
		
	default:
		msg := tgbotapi.NewMessage(chatID, 
			"Используйте кнопки меню для навигации.")
		msg.ReplyMarkup = MainMenu()
		bot.Send(msg)
	}
	
	return nil
}

// handleProfileMenu shows the profile menu
func (h *MessageHandler) handleProfileMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID
	
	// TODO: Check if user has linked account
	// For now, show basic menu
	text := "👤 *Профиль*\n\n" +
		"Здесь вы можете:\n" +
		"• Привязать игровой аккаунт\n" +
		"• Просмотреть свою статистику\n" +
		"• Найти других игроков\n" +
		"• Управлять подпиской"
	
	msg := tgbotapi.NewMessage(chatID, text)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = ProfileMenu(nil, false, 0)
	bot.Send(msg)
	
	return nil
}

// handleClanMenu shows the clan menu
func (h *MessageHandler) handleClanMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID
	
	text := "🛡 *Клан*\n\n" +
		"Здесь вы можете:\n" +
		"• Найти клан по тегу\n" +
		"• Посмотреть информацию о клане\n" +
		"• Просмотреть историю войн\n" +
		"• Привязать кланы"
	
	msg := tgbotapi.NewMessage(chatID, text)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = ClanMenu(nil, false, 0)
	bot.Send(msg)
	
	return nil
}

// handleNotificationsMenu shows the notifications menu
func (h *MessageHandler) handleNotificationsMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID
	
	text := "🔔 *Уведомления*\n\n" +
		"Настройте уведомления о:\n" +
		"• Начале войн\n" +
		"• Окончании войн\n" +
		"• Улучшениях зданий (Премиум)"
	
	msg := tgbotapi.NewMessage(chatID, text)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = NotificationToggle()
	bot.Send(msg)
	
	return nil
}

// handleCommunityCenterMenu shows the community center menu
func (h *MessageHandler) handleCommunityCenterMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID
	
	text := "🏛️ *Центр сообщества*\n\n" +
		"Полезная информация:\n" +
		"• Стоимость улучшений зданий\n" +
		"• Базы для разных ТХ\n" +
		"• Гайды и советы"
	
	msg := tgbotapi.NewMessage(chatID, text)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = CommunityCenterMenu()
	bot.Send(msg)
	
	return nil
}

// handleAnalyzerMenu shows the analyzer menu
func (h *MessageHandler) handleAnalyzerMenu(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	chatID := update.Message.Chat.ID
	
	text := "🤖 *Анализатор*\n\n" +
		"⏳ Функция анализатора войн в разработке...\n\n" +
		"Скоро здесь будет:\n" +
		"• Анализ ваших атак\n" +
		"• Рекомендации по улучшению\n" +
		"• Статистика побед и поражений"
	
	msg := tgbotapi.NewMessage(chatID, text)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = MainMenu()
	bot.Send(msg)
	
	return nil
}

// isMenuCommand checks if text is a menu command
func (h *MessageHandler) isMenuCommand(text string) bool {
	menuCommands := []string{
		ProfileBtn, ClanBtn, NotificationsBtn, CommunityCenterBtn, 
		AnalyzerBtn, BackBtn, LinkAccBtn, SearchProfileBtn, 
		SearchClanBtn, MyClanBtn,
	}
	
	for _, cmd := range menuCommands {
		if text == cmd {
			return true
		}
	}
	
	return strings.HasPrefix(text, MyProfilePrefix)
}

// CallbackHandler handles callback queries from inline keyboards
type CallbackHandler struct {
	messageGen *MessageGenerator
}

// NewCallbackHandler creates a new callback handler
func NewCallbackHandler(messageGen *MessageGenerator) *CallbackHandler {
	return &CallbackHandler{
		messageGen: messageGen,
	}
}

// HandleCallback processes callback queries
func (h *CallbackHandler) HandleCallback(update *tgbotapi.Update, bot *tgbotapi.BotAPI) error {
	if update.CallbackQuery == nil {
		return nil
	}
	
	callback := tgbotapi.NewCallback(update.CallbackQuery.ID, "")
	bot.Request(callback)
	
	data := update.CallbackQuery.Data
	chatID := update.CallbackQuery.Message.Chat.ID
	messageID := update.CallbackQuery.Message.MessageID
	
	log.Printf("Callback received: %s from chat %d", data, chatID)
	
	// Parse callback data
	parts := strings.Split(data, ":")
	action := parts[0]
	
	switch action {
	case "main_menu":
		text := "Главное меню"
		edit := tgbotapi.NewEditMessageText(chatID, messageID, text)
		edit.ReplyMarkup = nil
		bot.Send(edit)
		
		msg := tgbotapi.NewMessage(chatID, "Выберите раздел:")
		msg.ReplyMarkup = MainMenu()
		bot.Send(msg)
		
	case MembersCallback:
		// TODO: Implement members list
		text := "⏳ Список участников в разработке..."
		edit := tgbotapi.NewEditMessageText(chatID, messageID, text)
		bot.Send(edit)
		
	case WarListCallback:
		// TODO: Implement war list
		text := "⏳ История войн в разработке..."
		edit := tgbotapi.NewEditMessageText(chatID, messageID, text)
		bot.Send(edit)
		
	case SubscriptionCallback:
		text := "💎 *Премиум подписка*\n\n" +
			"Выберите тип подписки:\n\n" +
			"💎 Premium - базовые премиум функции\n" +
			"💎💎 Pro Plus - расширенные возможности"
		kbd := SubscriptionTypes()
		edit := tgbotapi.NewEditMessageText(chatID, messageID, text)
		edit.ParseMode = "Markdown"
		edit.ReplyMarkup = &kbd
		bot.Send(edit)
		
	case SubscriptionTypeCallback:
		if len(parts) < 2 {
			return fmt.Errorf("invalid subscription type callback")
		}
		subType := parts[1]
		
		text := fmt.Sprintf("💎 Выберите период подписки %s:", subType)
		kbd := SubscriptionPeriods(subType)
		edit := tgbotapi.NewEditMessageText(chatID, messageID, text)
		edit.ReplyMarkup = &kbd
		bot.Send(edit)
		
	case CommunityCenterCallback:
		text := "🏛️ *Центр сообщества*\n\nВыберите раздел:"
		kbd := CommunityCenterMenu()
		edit := tgbotapi.NewEditMessageText(chatID, messageID, text)
		edit.ParseMode = "Markdown"
		edit.ReplyMarkup = &kbd
		bot.Send(edit)
		
	case BuildingCostsCallback:
		text := "🏗️ *Стоимость зданий*\n\nВыберите категорию:"
		kbd := BuildingCostsMenu()
		edit := tgbotapi.NewEditMessageText(chatID, messageID, text)
		edit.ParseMode = "Markdown"
		edit.ReplyMarkup = &kbd
		bot.Send(edit)
		
	default:
		text := fmt.Sprintf("⏳ Функция '%s' в разработке...", action)
		edit := tgbotapi.NewEditMessageText(chatID, messageID, text)
		bot.Send(edit)
	}
	
	return nil
}
