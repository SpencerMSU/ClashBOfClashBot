package handlers

import (
	"fmt"
	"log"
	"strconv"
	"strings"
	"time"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
	"clashbot/internal/database"
	"clashbot/internal/api"
	"clashbot/internal/payment"
	"clashbot/internal/models"
)

// Handler представляет обработчик сообщений бота
type Handler struct {
	db         *database.Service
	cocAPI     *api.CocAPIClient
	paymentSvc *payment.PaymentService
	botUsername string
}

// New создает новый обработчик
func New(db *database.Service, cocAPI *api.CocAPIClient, paymentSvc *payment.PaymentService, botUsername string) *Handler {
	return &Handler{
		db:         db,
		cocAPI:     cocAPI,
		paymentSvc: paymentSvc,
		botUsername: botUsername,
	}
}

// HandleCommand обрабатывает команды бота
func (h *Handler) HandleCommand(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	if update.Message == nil {
		log.Println("⚠️ Получено пустое сообщение в HandleCommand")
		return
	}

	// Обновляем информацию о пользователе
	user, err := h.ensureUser(update.Message.From)
	if err != nil {
		log.Printf("Ошибка создания пользователя: %v", err)
		return
	}

	// Обновляем время последней активности
	h.db.UpdateLastActivity(user.TelegramID)

	command := update.Message.Command()
	
	switch command {
	case "start":
		h.handleStart(bot, update)
	case "profile":
		h.handleProfile(bot, update)
	case "link":
		h.handleLink(bot, update)
	case "clan":
		h.handleClan(bot, update)
	case "search":
		h.handleSearch(bot, update)
	case "subscription":
		h.handleSubscription(bot, update)
	case "help":
		h.handleHelp(bot, update)
	default:
		h.handleUnknownCommand(bot, update)
	}
}

// HandleCallback обрабатывает callback запросы
func (h *Handler) HandleCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	if update.CallbackQuery == nil {
		log.Println("⚠️ Получен пустой callback в HandleCallback")
		return
	}

	callback := update.CallbackQuery
	data := callback.Data

	log.Printf("🔘 Обработка callback: %s от пользователя %d", data, callback.From.ID)

	// Подтверждаем callback
	callbackConfig := tgbotapi.NewCallback(callback.ID, "")
	if _, err := bot.Request(callbackConfig); err != nil {
		log.Printf("Ошибка подтверждения callback: %v", err)
	}

	// Обрабатываем различные типы callback'ов
	switch {
	case strings.HasPrefix(data, "subscription_"):
		h.handleSubscriptionCallback(bot, update)
	case strings.HasPrefix(data, "payment_"):
		h.handlePaymentCallback(bot, update)
	case strings.HasPrefix(data, "clan_"):
		h.handleClanCallback(bot, update)
	case strings.HasPrefix(data, "members"):
		h.handleMembersCallback(bot, update)
	case strings.HasPrefix(data, "warlist"):
		h.handleWarListCallback(bot, update)
	case strings.HasPrefix(data, "warinfo"):
		h.handleWarInfoCallback(bot, update)
	case strings.HasPrefix(data, "profile"):
		h.handleProfileCallback(bot, update)
	case strings.HasPrefix(data, "notify_toggle"):
		h.handleNotifyToggleCallback(bot, update)
	case strings.HasPrefix(data, "cwlbonus"):
		h.handleCwlBonusCallback(bot, update)
	case strings.HasPrefix(data, "current_war"):
		h.handleCurrentWarCallback(bot, update)
	case strings.HasPrefix(data, "cwl_info"):
		h.handleCwlInfoCallback(bot, update)
	case strings.HasPrefix(data, "main_menu"):
		h.handleMainMenuCallback(bot, update)
	case strings.HasPrefix(data, "building_tracker"):
		h.handleBuildingTrackerCallback(bot, update)
	case strings.HasPrefix(data, "building_toggle"):
		h.handleBuildingToggleCallback(bot, update)
	case data == "noop":
		// Ничего не делаем - это заглушка
		return
	default:
		log.Printf("Неизвестный callback: %s", data)
		h.handleUnknownCallback(bot, update)
	}
}

// ensureUser создает пользователя если его нет в базе
func (h *Handler) ensureUser(from *tgbotapi.User) (*models.User, error) {
	user, err := h.db.GetUserByTelegramID(from.ID)
	if err != nil {
		return nil, err
	}

	if user == nil {
		// Создаем нового пользователя
		user, err = h.db.CreateUser(from.ID, from.UserName, from.FirstName, from.LastName)
		if err != nil {
			return nil, err
		}
	}

	return user, nil
}

// handleStart обрабатывает команду /start
func (h *Handler) handleStart(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	welcomeText := `🎮 Добро пожаловать в ClashBot!

Этот бот поможет вам отслеживать статистику Clash of Clans:

👤 **Профиль** - Привяжите свой аккаунт
🛡 **Клан** - Информация о клане
⚔️ **Войны** - Статистика войн
💎 **Премиум** - Дополнительные функции

Начните с команды /link чтобы привязать свой аккаунт!

Используйте /help для просмотра всех команд.`

	msg := tgbotapi.NewMessage(update.Message.Chat.ID, welcomeText)
	msg.ParseMode = tgbotapi.ModeMarkdown
	bot.Send(msg)
}

// handleProfile обрабатывает команду /profile
func (h *Handler) handleProfile(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	user, err := h.db.GetUserByTelegramID(update.Message.From.ID)
	if err != nil {
		log.Printf("Ошибка получения пользователя: %v", err)
		return
	}

	if user.PlayerTag == "" {
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
			"❌ Вы еще не привязали свой аккаунт!\n\nИспользуйте команду /link <ваш_тег> чтобы привязать аккаунт.")
		bot.Send(msg)
		return
	}

	// Получаем информацию об игроке через API
	playerInfo, err := h.cocAPI.GetPlayerInfo(user.PlayerTag)
	if err != nil {
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
			fmt.Sprintf("❌ Ошибка получения данных игрока: %v", err))
		bot.Send(msg)
		return
	}

	// Форматируем информацию о профиле
	profileText := h.formatPlayerProfile(playerInfo)
	
	// Добавляем инлайн клавиатуру с кнопками
	keyboard := tgbotapi.NewInlineKeyboardMarkup(
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonData("🛡 Мой клан", "clan_menu"),
			tgbotapi.NewInlineKeyboardButtonData("⚔️ Текущая война", "current_war"),
		),
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonData("🔔 Уведомления", "notify_toggle"),
			tgbotapi.NewInlineKeyboardButtonData("💎 Премиум", "subscription_menu"),
		),
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonData("🏠 Главное меню", "main_menu"),
		),
	)
	
	msg := tgbotapi.NewMessage(update.Message.Chat.ID, profileText)
	msg.ParseMode = tgbotapi.ModeMarkdown
	msg.ReplyMarkup = keyboard
	bot.Send(msg)
}

// handleLink обрабатывает команду /link
func (h *Handler) handleLink(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	args := strings.Fields(update.Message.Text)
	if len(args) < 2 {
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
			"❌ Укажите тег игрока!\n\nПример: `/link #ABC123`")
		msg.ParseMode = tgbotapi.ModeMarkdown
		bot.Send(msg)
		return
	}

	playerTag := args[1]
	
	// Проверяем валидность тега
	formattedTag, err := api.FormatPlayerTag(playerTag)
	if err != nil {
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
			fmt.Sprintf("❌ Неверный формат тега: %v", err))
		bot.Send(msg)
		return
	}

	// Проверяем существование игрока
	playerInfo, err := h.cocAPI.GetPlayerInfo(formattedTag)
	if err != nil {
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
			fmt.Sprintf("❌ Игрок не найден: %v", err))
		bot.Send(msg)
		return
	}

	// Привязываем игрока к пользователю
	err = h.db.UpdateUserPlayerTag(update.Message.From.ID, formattedTag)
	if err != nil {
		log.Printf("Ошибка привязки игрока: %v", err)
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
			"❌ Ошибка привязки аккаунта. Попробуйте позже.")
		bot.Send(msg)
		return
	}

	// Отправляем подтверждение
	confirmText := fmt.Sprintf("✅ Аккаунт успешно привязан!\n\n👤 **%s** `%s`\n🏆 %d 🏰 TH%d",
		playerInfo.Name, playerInfo.Tag, playerInfo.Trophies, playerInfo.TownHallLevel)
	
	msg := tgbotapi.NewMessage(update.Message.Chat.ID, confirmText)
	msg.ParseMode = tgbotapi.ModeMarkdown
	bot.Send(msg)
}

// handleClan обрабатывает команду /clan
func (h *Handler) handleClan(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	user, err := h.db.GetUserByTelegramID(update.Message.From.ID)
	if err != nil || user.PlayerTag == "" {
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
			"❌ Сначала привяжите свой аккаунт командой /link")
		bot.Send(msg)
		return
	}

	// Получаем информацию об игроке
	playerInfo, err := h.cocAPI.GetPlayerInfo(user.PlayerTag)
	if err != nil {
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
			fmt.Sprintf("❌ Ошибка получения данных: %v", err))
		bot.Send(msg)
		return
	}

	if playerInfo.Clan == nil {
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
			"❌ Вы не состоите в клане!")
		bot.Send(msg)
		return
	}

	// Получаем подробную информацию о клане
	clanInfo, err := h.cocAPI.GetClanInfo(playerInfo.Clan.Tag)
	if err != nil {
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
			fmt.Sprintf("❌ Ошибка получения данных клана: %v", err))
		bot.Send(msg)
		return
	}

	// Форматируем информацию о клане
	clanText := h.formatClanInfo(clanInfo)
	
	// Добавляем инлайн клавиатуру с кнопками
	keyboard := tgbotapi.NewInlineKeyboardMarkup(
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonData("👥 Участники", "members"),
			tgbotapi.NewInlineKeyboardButtonData("⚔️ Текущая война", "current_war"),
		),
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonData("📈 История войн", "warlist"),
			tgbotapi.NewInlineKeyboardButtonData("🏆 ЛВК", "cwl_info"),
		),
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonData("🏠 Главное меню", "main_menu"),
		),
	)
	
	msg := tgbotapi.NewMessage(update.Message.Chat.ID, clanText)
	msg.ParseMode = tgbotapi.ModeMarkdown
	msg.ReplyMarkup = keyboard
	bot.Send(msg)
}

// handleSearch обрабатывает команду /search
func (h *Handler) handleSearch(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	args := strings.Fields(update.Message.Text)
	if len(args) < 2 {
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
			"❌ Укажите тег для поиска!\n\nПример: `/search #ABC123`")
		msg.ParseMode = tgbotapi.ModeMarkdown
		bot.Send(msg)
		return
	}

	tag := args[1]
	
	// Проверяем формат тега - может быть игрок или клан
	if strings.HasPrefix(tag, "#") && len(tag) >= 4 {
		// Сначала пробуем как игрока
		if playerInfo, err := h.cocAPI.GetPlayerInfo(tag); err == nil {
			profileText := h.formatPlayerProfile(playerInfo)
			msg := tgbotapi.NewMessage(update.Message.Chat.ID, profileText)
			msg.ParseMode = tgbotapi.ModeMarkdown
			bot.Send(msg)
			return
		}
		
		// Потом как клан
		if clanInfo, err := h.cocAPI.GetClanInfo(tag); err == nil {
			clanText := h.formatClanInfo(clanInfo)
			msg := tgbotapi.NewMessage(update.Message.Chat.ID, clanText)
			msg.ParseMode = tgbotapi.ModeMarkdown
			bot.Send(msg)
			return
		}
	}

	msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
		"❌ Игрок или клан не найден!")
	bot.Send(msg)
}

// handleSubscription обрабатывает команду /subscription
func (h *Handler) handleSubscription(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	// Проверяем активную подписку
	subscription, err := h.db.GetActiveSubscription(update.Message.From.ID)
	if err != nil {
		log.Printf("Ошибка получения подписки: %v", err)
		return
	}

	var text string
	var keyboard tgbotapi.InlineKeyboardMarkup

	if subscription != nil {
		// Пользователь уже имеет активную подписку
		text = fmt.Sprintf("💎 **Ваша подписка**\n\n📋 Тип: %s\n📅 Активна до: %s",
			subscription.SubscriptionType,
			subscription.EndDate.Format("02.01.2006 15:04"))
			
		keyboard = tgbotapi.NewInlineKeyboardMarkup(
			tgbotapi.NewInlineKeyboardRow(
				tgbotapi.NewInlineKeyboardButtonData("🔄 Продлить", "subscription_extend"),
			),
		)
	} else {
		// Пользователь не имеет активной подписки
		text = `💎 **Премиум подписка ClashBot**

🎯 **Премиум возможности:**
• 🏗️ Отслеживание улучшений зданий
• 📊 Расширенная статистика  
• 🔔 Персональные уведомления
• 📈 Детальная аналитика войн

💰 **Тарифы:**`

		keyboard = tgbotapi.NewInlineKeyboardMarkup(
			tgbotapi.NewInlineKeyboardRow(
				tgbotapi.NewInlineKeyboardButtonData("1 месяц - 49₽", "subscription_premium_1month"),
			),
			tgbotapi.NewInlineKeyboardRow(
				tgbotapi.NewInlineKeyboardButtonData("3 месяца - 119₽", "subscription_premium_3months"),
			),
			tgbotapi.NewInlineKeyboardRow(
				tgbotapi.NewInlineKeyboardButtonData("6 месяцев - 199₽", "subscription_premium_6months"),
			),
			tgbotapi.NewInlineKeyboardRow(
				tgbotapi.NewInlineKeyboardButtonData("1 год - 349₽", "subscription_premium_1year"),
			),
		)
	}

	msg := tgbotapi.NewMessage(update.Message.Chat.ID, text)
	msg.ParseMode = tgbotapi.ModeMarkdown
	msg.ReplyMarkup = keyboard
	bot.Send(msg)
}

// handleHelp обрабатывает команду /help
func (h *Handler) handleHelp(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	helpText := `🎮 **Команды ClashBot**

👤 **Профиль:**
/link <тег> - Привязать аккаунт
/profile - Мой профиль

🛡 **Клан:**
/clan - Информация о клане
/search <тег> - Поиск игрока/клана

💎 **Премиум:**
/subscription - Управление подпиской

ℹ️ **Справка:**
/help - Список команд

**Примеры:**
/link #ABC123DEF
/search #ClanTag`

	msg := tgbotapi.NewMessage(update.Message.Chat.ID, helpText)
	msg.ParseMode = tgbotapi.ModeMarkdown
	bot.Send(msg)
}

// handleUnknownCommand обрабатывает неизвестные команды
func (h *Handler) handleUnknownCommand(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
		"❌ Неизвестная команда. Используйте /help для просмотра доступных команд.")
	bot.Send(msg)
}

// Вспомогательные методы для форматирования

// formatPlayerProfile форматирует профиль игрока
func (h *Handler) formatPlayerProfile(player *api.PlayerInfo) string {
	text := fmt.Sprintf("👤 **%s** `%s`\n\n", player.Name, player.Tag)
	text += fmt.Sprintf("🏰 TH%d • 🏆 %d • ⭐ %d\n", player.TownHallLevel, player.Trophies, player.WarStars)
	text += fmt.Sprintf("📈 Рекорд: %d 🏆\n", player.BestTrophies)
	text += fmt.Sprintf("⚔️ Атак: %d • 🛡 Защит: %d\n", player.AttackWins, player.DefenseWins)
	text += fmt.Sprintf("🎁 Дано: %d • Получено: %d\n", player.DonationsGiven, player.DonationsReceived)
	
	if player.Clan != nil {
		text += fmt.Sprintf("\n🛡 **Клан:** %s `%s`", player.Clan.Name, player.Clan.Tag)
	}
	
	return text
}

// formatClanInfo форматирует информацию о клане
func (h *Handler) formatClanInfo(clan *api.ClanInfo) string {
	text := fmt.Sprintf("🛡 **%s** `%s`\n\n", clan.Name, clan.Tag)
	text += fmt.Sprintf("📈 Уровень: %d • 🏆 %d очков\n", clan.ClanLevel, clan.ClanPoints)
	text += fmt.Sprintf("👥 Участников: %d/50\n", clan.Members)
	text += fmt.Sprintf("⚔️ Войны: %d побед, %d поражений\n", clan.WarWins, clan.WarLosses)
	text += fmt.Sprintf("🔥 Серия: %d\n", clan.WarWinStreak)
	
	if clan.Description != "" {
		text += fmt.Sprintf("\n📝 %s", clan.Description)
	}
	
	return text
}

// handleSubscriptionCallback обрабатывает callback'и подписки
func (h *Handler) handleSubscriptionCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	subscriptionType := strings.TrimPrefix(callback.Data, "subscription_")
	
	// Создаем платеж через Python YooKassa API
	returnURL := fmt.Sprintf("https://t.me/%s?start=payment_success_%s", h.botUsername, subscriptionType)
	
	paymentData, err := h.paymentSvc.CreatePayment(callback.From.ID, subscriptionType, returnURL)
	if err != nil {
		log.Printf("Ошибка создания платежа: %v", err)
		
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			"❌ Ошибка создания платежа. Попробуйте позже.")
		bot.Send(msg)
		return
	}
	
	// Получаем название и цену подписки
	name, _ := h.paymentSvc.GetSubscriptionName(subscriptionType)
	price, _ := h.paymentSvc.GetSubscriptionPrice(subscriptionType)
	
	text := fmt.Sprintf("💳 **Оплата подписки**\n\n📋 %s\n💰 Сумма: %.2f ₽\n\n👆 Нажмите кнопку для оплаты:", 
		name, price)
	
	// Извлекаем URL для оплаты
	var paymentURL string
	if confirmation, ok := paymentData.Confirmation["confirmation_url"]; ok {
		paymentURL = confirmation.(string)
	}
	
	keyboard := tgbotapi.NewInlineKeyboardMarkup(
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonURL("💳 Оплатить", paymentURL),
		),
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonData("🔄 Проверить оплату", "payment_check_"+paymentData.ID),
		),
	)
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, text)
	msg.ParseMode = tgbotapi.ModeMarkdown
	msg.ReplyMarkup = keyboard
	bot.Send(msg)
}

// handlePaymentCallback обрабатывает callback'и платежей
func (h *Handler) handlePaymentCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	paymentID := strings.TrimPrefix(callback.Data, "payment_check_")
	
	// Проверяем статус платежа
	paymentData, err := h.paymentSvc.CheckPaymentStatus(paymentID)
	if err != nil {
		log.Printf("Ошибка проверки платежа: %v", err)
		
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			"❌ Ошибка проверки платежа. Попробуйте позже.")
		bot.Send(msg)
		return
	}
	
	if paymentData.Status == "succeeded" {
		// Платеж успешен - создаем подписку
		subscriptionType := paymentData.Metadata["subscription_type"]
		duration := h.paymentSvc.GetSubscriptionDuration(subscriptionType)
		
		amount, _ := strconv.ParseFloat(paymentData.Amount["value"].(string), 64)
		
		subscription := &models.Subscription{
			TelegramID:       callback.From.ID,
			SubscriptionType: subscriptionType,
			StartDate:        time.Now(),
			EndDate:          time.Now().Add(duration),
			IsActive:         true,
			PaymentID:        paymentID,
			Amount:           amount,
		}
		
		err = h.db.CreateSubscription(subscription)
		if err != nil {
			log.Printf("Ошибка создания подписки: %v", err)
		}
		
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			"✅ Платеж успешно подтвержден! Подписка активирована.")
		bot.Send(msg)
	} else {
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			"⏳ Платеж еще не подтвержден. Попробуйте позже.")
		bot.Send(msg)
	}
}

// handleClanCallback обрабатывает callback'и клана
func (h *Handler) handleClanCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	// Здесь можно добавить обработку различных действий с кланом
	// Например, просмотр участников, статистики войн и т.д.
	callback := update.CallbackQuery
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
		"🛡 Функции клана временно недоступны.")
	bot.Send(msg)
}

// handleMembersCallback обрабатывает callback'и участников клана
func (h *Handler) handleMembersCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	user, err := h.db.GetUserByTelegramID(callback.From.ID)
	if err != nil || user.PlayerTag == "" {
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			"❌ Сначала привяжите свой аккаунт командой /link")
		bot.Send(msg)
		return
	}

	// Получаем информацию об игроке
	playerInfo, err := h.cocAPI.GetPlayerInfo(user.PlayerTag)
	if err != nil || playerInfo.Clan == nil {
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			"❌ Вы не состоите в клане!")
		bot.Send(msg)
		return
	}

	// Получаем список участников клана
	clanInfo, err := h.cocAPI.GetClanInfo(playerInfo.Clan.Tag)
	if err != nil {
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			"❌ Ошибка получения данных клана")
		bot.Send(msg)
		return
	}

	// Форматируем список участников
	membersText := h.formatClanMembers(clanInfo)
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, membersText)
	msg.ParseMode = tgbotapi.ModeMarkdown
	bot.Send(msg)
}

// handleWarListCallback обрабатывает callback'и списка войн
func (h *Handler) handleWarListCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
		"⚔️ История войн временно недоступна.")
	bot.Send(msg)
}

// handleWarInfoCallback обрабатывает callback'и информации о войне
func (h *Handler) handleWarInfoCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
		"⚔️ Подробная информация о войне временно недоступна.")
	bot.Send(msg)
}

// handleProfileCallback обрабатывает callback'и профиля
func (h *Handler) handleProfileCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	data := callback.Data
	
	// Извлекаем тег игрока из callback данных
	parts := strings.Split(data, ":")
	if len(parts) < 2 {
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			"❌ Неверный формат данных профиля")
		bot.Send(msg)
		return
	}
	
	playerTag := parts[1]
	
	// Получаем информацию об игроке
	playerInfo, err := h.cocAPI.GetPlayerInfo(playerTag)
	if err != nil {
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			fmt.Sprintf("❌ Ошибка получения данных игрока: %v", err))
		bot.Send(msg)
		return
	}

	// Форматируем информацию о профиле
	profileText := h.formatPlayerProfile(playerInfo)
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, profileText)
	msg.ParseMode = tgbotapi.ModeMarkdown
	bot.Send(msg)
}

// handleNotifyToggleCallback обрабатывает callback'и переключения уведомлений
func (h *Handler) handleNotifyToggleCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
		"🔔 Настройки уведомлений временно недоступны.")
	bot.Send(msg)
}

// handleCwlBonusCallback обрабатывает callback'и бонусов ЛВК
func (h *Handler) handleCwlBonusCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
		"🏆 Информация о бонусах ЛВК временно недоступна.")
	bot.Send(msg)
}

// handleCurrentWarCallback обрабатывает callback'и текущей войны
func (h *Handler) handleCurrentWarCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	user, err := h.db.GetUserByTelegramID(callback.From.ID)
	if err != nil || user.PlayerTag == "" {
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			"❌ Сначала привяжите свой аккаунт командой /link")
		bot.Send(msg)
		return
	}

	// Получаем информацию об игроке
	playerInfo, err := h.cocAPI.GetPlayerInfo(user.PlayerTag)
	if err != nil || playerInfo.Clan == nil {
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			"❌ Вы не состоите в клане!")
		bot.Send(msg)
		return
	}

	// Получаем информацию о текущей войне
	warInfo, err := h.cocAPI.GetClanCurrentWar(playerInfo.Clan.Tag)
	if err != nil {
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
			"❌ Ошибка получения данных войны")
		bot.Send(msg)
		return
	}

	// Форматируем информацию о войне
	warText := h.formatWarInfo(warInfo)
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, warText)
	msg.ParseMode = tgbotapi.ModeMarkdown
	bot.Send(msg)
}

// handleCwlInfoCallback обрабатывает callback'и информации ЛВК
func (h *Handler) handleCwlInfoCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
		"🏆 Информация о Лиге Кланов временно недоступна.")
	bot.Send(msg)
}

// handleMainMenuCallback обрабатывает callback'и главного меню
func (h *Handler) handleMainMenuCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	// Создаем главное меню
	welcomeText := `🎮 **Главное меню ClashBot**

Выберите нужную функцию:

👤 **/profile** - Мой профиль
🛡 **/clan** - Информация о клане  
🔍 **/search** - Поиск игрока/клана
💎 **/subscription** - Премиум подписка
❓ **/help** - Справка по командам`

	// Создаем инлайн клавиатуру
	keyboard := tgbotapi.NewInlineKeyboardMarkup(
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonData("👤 Профиль", "profile_menu"),
			tgbotapi.NewInlineKeyboardButtonData("🛡 Клан", "clan_menu"),
		),
		tgbotapi.NewInlineKeyboardRow(
			tgbotapi.NewInlineKeyboardButtonData("🔍 Поиск", "search_menu"),
			tgbotapi.NewInlineKeyboardButtonData("💎 Премиум", "subscription_menu"),
		),
	)

	// Отправляем или редактируем сообщение
	if callback.Message.Text != "" {
		edit := tgbotapi.NewEditMessageText(callback.Message.Chat.ID, callback.Message.MessageID, welcomeText)
		edit.ParseMode = tgbotapi.ModeMarkdown
		edit.ReplyMarkup = &keyboard
		bot.Send(edit)
	} else {
		msg := tgbotapi.NewMessage(callback.Message.Chat.ID, welcomeText)
		msg.ParseMode = tgbotapi.ModeMarkdown
		msg.ReplyMarkup = keyboard
		bot.Send(msg)
	}
}

// handleBuildingTrackerCallback обрабатывает callback'и отслеживания зданий
func (h *Handler) handleBuildingTrackerCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
		"🏗️ Отслеживание улучшений зданий временно недоступно.")
	bot.Send(msg)
}

// handleBuildingToggleCallback обрабатывает callback'и переключения отслеживания зданий
func (h *Handler) handleBuildingToggleCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
		"🔄 Переключение отслеживания зданий временно недоступно.")
	bot.Send(msg)
}

// handleUnknownCallback обрабатывает неизвестные callback'и
func (h *Handler) handleUnknownCallback(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	msg := tgbotapi.NewMessage(callback.Message.Chat.ID, 
		"❌ Неизвестная команда кнопки.")
	bot.Send(msg)
}

// formatClanMembers форматирует список участников клана
func (h *Handler) formatClanMembers(clan *api.ClanInfo) string {
	text := fmt.Sprintf("👥 **Участники клана %s**\n\n", clan.Name)
	
	// Группируем по ролям
	leaders := []api.ClanMember{}
	coLeaders := []api.ClanMember{}
	elders := []api.ClanMember{}
	members := []api.ClanMember{}
	
	for _, member := range clan.MemberList {
		switch member.Role {
		case "leader":
			leaders = append(leaders, member)
		case "coLeader":
			coLeaders = append(coLeaders, member)
		case "admin":
			elders = append(elders, member)
		default:
			members = append(members, member)
		}
	}
	
	// Добавляем лидеров
	if len(leaders) > 0 {
		text += "👑 **Лидеры:**\n"
		for _, member := range leaders {
			text += fmt.Sprintf("• %s `%s` 🏆%d\n", member.Name, member.Tag, member.Trophies)
		}
		text += "\n"
	}
	
	// Добавляем соруководителей
	if len(coLeaders) > 0 {
		text += "🔶 **Соруководители:**\n"
		for _, member := range coLeaders {
			text += fmt.Sprintf("• %s `%s` 🏆%d\n", member.Name, member.Tag, member.Trophies)
		}
		text += "\n"
	}
	
	// Добавляем старейшин
	if len(elders) > 0 {
		text += "🔸 **Старейшины:**\n"
		for _, member := range elders {
			text += fmt.Sprintf("• %s `%s` 🏆%d\n", member.Name, member.Tag, member.Trophies)
		}
		text += "\n"
	}
	
	// Добавляем участников (показываем только первых 10)
	if len(members) > 0 {
		text += "⚫ **Участники:**\n"
		for i, member := range members {
			if i >= 10 {
				text += fmt.Sprintf("... и еще %d участников\n", len(members)-10)
				break
			}
			text += fmt.Sprintf("• %s `%s` 🏆%d\n", member.Name, member.Tag, member.Trophies)
		}
	}
	
	return text
}

// formatWarInfo форматирует информацию о войне
func (h *Handler) formatWarInfo(war *api.WarInfo) string {
	text := "⚔️ **Информация о войне**\n\n"
	
	// Статус войны
	var status string
	switch war.State {
	case "preparation":
		status = "🔄 Подготовка"
	case "inWar":
		status = "⚔️ Идет война"
	case "warEnded":
		status = "✅ Завершена"
	default:
		status = war.State
	}
	
	text += fmt.Sprintf("📊 Статус: %s\n", status)
	text += fmt.Sprintf("👥 Размер: %d vs %d\n\n", war.TeamSize, war.TeamSize)
	
	// Информация о кланах
	if war.Clan != nil {
		text += fmt.Sprintf("🛡 **%s**\n", war.Clan.Name)
		text += fmt.Sprintf("⭐ Звезд: %d\n", war.Clan.Stars)
		text += fmt.Sprintf("💥 Разрушений: %.1f%%\n", war.Clan.DestructionPercentage)
		text += fmt.Sprintf("⚔️ Атак: %d\n\n", war.Clan.Attacks)
	}
	
	if war.Opponent != nil {
		text += fmt.Sprintf("🏴 **%s**\n", war.Opponent.Name)
		text += fmt.Sprintf("⭐ Звезд: %d\n", war.Opponent.Stars)
		text += fmt.Sprintf("💥 Разрушений: %.1f%%\n", war.Opponent.DestructionPercentage)
		text += fmt.Sprintf("⚔️ Атак: %d\n", war.Opponent.Attacks)
	}
	
	return text
}