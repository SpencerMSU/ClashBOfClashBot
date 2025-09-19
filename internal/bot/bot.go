package bot

import (
	"log"
	"fmt"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
	"clashbot/internal/config"
	"clashbot/internal/database"
	"clashbot/internal/api"
	"clashbot/internal/payment"
	"clashbot/internal/handlers"
)

// Bot представляет основной класс Telegram бота
type Bot struct {
	config     *config.Config
	bot        *tgbotapi.BotAPI
	db         *database.Service
	cocAPI     *api.CocAPIClient
	paymentSvc *payment.PaymentService
	handler    *handlers.Handler
}

// New создает новый экземпляр бота
func New(cfg *config.Config) (*Bot, error) {
	// Проверяем конфигурацию
	if err := cfg.Validate(); err != nil {
		return nil, fmt.Errorf("неверная конфигурация: %v", err)
	}

	// Создаем Telegram Bot API
	botAPI, err := tgbotapi.NewBotAPI(cfg.BotToken)
	if err != nil {
		return nil, fmt.Errorf("ошибка создания Telegram Bot API: %v", err)
	}

	log.Printf("Авторизован как @%s", botAPI.Self.UserName)

	// Создаем подключение к базе данных
	db, err := database.New(cfg.DatabasePath)
	if err != nil {
		return nil, fmt.Errorf("ошибка подключения к базе данных: %v", err)
	}

	// Создаем клиент Clash of Clans API
	cocAPI := api.NewCocAPIClient(cfg.CocAPIBaseURL, cfg.CocAPIToken)

	// Создаем сервис платежей
	paymentSvc := payment.New(cfg.BotUsername, "python3", "./payment_bridge.py")

	// Создаем обработчик сообщений
	handler := handlers.New(db, cocAPI, paymentSvc, cfg.BotUsername)

	return &Bot{
		config:     cfg,
		bot:        botAPI,
		db:         db,
		cocAPI:     cocAPI,
		paymentSvc: paymentSvc,
		handler:    handler,
	}, nil
}

// Run запускает бота
func (b *Bot) Run() error {
	log.Println("Запуск бота...")

	// Настраиваем обновления
	u := tgbotapi.NewUpdate(0)
	u.Timeout = 60

	updates := b.bot.GetUpdatesChan(u)

	// Основной цикл обработки сообщений
	for update := range updates {
		go b.handleUpdate(update)
	}

	return nil
}

// handleUpdate обрабатывает входящие обновления
func (b *Bot) handleUpdate(update tgbotapi.Update) {
	defer func() {
		if r := recover(); r != nil {
			log.Printf("Паника в обработчике обновления: %v", r)
		}
	}()

	switch {
	case update.Message != nil:
		b.handleMessage(update)
	case update.CallbackQuery != nil:
		b.handleCallbackQuery(update)
	default:
		log.Printf("Неизвестный тип обновления: %+v", update)
	}
}

// handleMessage обрабатывает текстовые сообщения
func (b *Bot) handleMessage(update tgbotapi.Update) {
	message := update.Message

	// Логируем сообщение
	log.Printf("[%s] %s", message.From.UserName, message.Text)

	// Обрабатываем команды
	if message.IsCommand() {
		b.handler.HandleCommand(b.bot, update)
		return
	}

	// Обрабатываем обычные сообщения
	b.handleTextMessage(update)
}

// handleTextMessage обрабатывает обычные текстовые сообщения
func (b *Bot) handleTextMessage(update tgbotapi.Update) {
	// Здесь можно добавить обработку обычных текстовых сообщений
	// Например, если пользователь находится в состоянии ввода тега игрока
	
	// Пока просто отправляем справку
	helpText := "Используйте команды для взаимодействия с ботом. Напишите /help для просмотра доступных команд."
	
	msg := tgbotapi.NewMessage(update.Message.Chat.ID, helpText)
	b.bot.Send(msg)
}

// handleCallbackQuery обрабатывает callback запросы
func (b *Bot) handleCallbackQuery(update tgbotapi.Update) {
	callback := update.CallbackQuery
	
	// Логируем callback
	log.Printf("[%s] Callback: %s", callback.From.UserName, callback.Data)
	
	// Передаем обработку в handler
	b.handler.HandleCallback(b.bot, update)
}

// Close закрывает ресурсы бота
func (b *Bot) Close() error {
	log.Println("Завершение работы бота...")
	
	// Останавливаем бота
	b.bot.StopReceivingUpdates()
	
	// Закрываем базу данных
	if err := b.db.Close(); err != nil {
		log.Printf("Ошибка закрытия базы данных: %v", err)
		return err
	}
	
	log.Println("Бот успешно завершил работу")
	return nil
}