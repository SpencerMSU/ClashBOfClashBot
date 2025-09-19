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
	log.Printf("👤 Обработка пользователя: %d", update.Message.From.ID)
	user, err := h.ensureUser(update.Message.From)
	if err != nil {
		log.Printf("❌ Ошибка создания пользователя: %v", err)
		return
	}
	log.Printf("✅ Пользователь обработан: ID=%d, PlayerTag=%s", user.TelegramID, user.PlayerTag)

	// Обновляем время последней активности
	h.db.UpdateLastActivity(user.TelegramID)

	command := update.Message.Command()
	log.Printf("⚡ Выполнение команды: %s", command)
	
	switch command {
	case "start":
		log.Println("🎯 Обработка команды /start")
		h.handleStart(bot, update)
	case "profile":
		log.Println("👤 Обработка команды /profile")
		h.handleProfile(bot, update)
	case "link":
		log.Println("🔗 Обработка команды /link")
		h.handleLink(bot, update)
	case "clan":
		log.Println("🛡 Обработка команды /clan")
		h.handleClan(bot, update)
	case "search":
		log.Println("🔍 Обработка команды /search")
		h.handleSearch(bot, update)
	case "subscription":
		log.Println("💎 Обработка команды /subscription")
		h.handleSubscription(bot, update)
	case "help":
		log.Println("❓ Обработка команды /help")
		h.handleHelp(bot, update)
	default:
		log.Printf("❓ Неизвестная команда: %s", command)
		h.handleUnknownCommand(bot, update)
	}
	
	log.Printf("✅ Команда %s обработана", command)
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
		log.Printf("⚠️ Ошибка подтверждения callback: %v", err)
	} else {
		log.Println("✅ Callback подтвержден")
	}

	// Обрабатываем различные типы callback'ов
	switch {
	case strings.HasPrefix(data, "subscription_"):
		log.Println("💎 Обработка callback подписки")
		h.handleSubscriptionCallback(bot, update)
	case strings.HasPrefix(data, "payment_"):
		log.Println("💳 Обработка callback платежа")
		h.handlePaymentCallback(bot, update)
	case strings.HasPrefix(data, "clan_"):
		log.Println("🛡 Обработка callback клана")
		h.handleClanCallback(bot, update)
	default:
		log.Printf("❓ Неизвестный callback: %s", data)
	}
	
	log.Printf("✅ Callback %s обработан", data)
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
	
	msg := tgbotapi.NewMessage(update.Message.Chat.ID, profileText)
	msg.ParseMode = tgbotapi.ModeMarkdown
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
	
	msg := tgbotapi.NewMessage(update.Message.Chat.ID, clanText)
	msg.ParseMode = tgbotapi.ModeMarkdown
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
}