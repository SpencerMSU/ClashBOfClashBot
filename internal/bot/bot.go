package bot

import (
	"ClashBOfClashBot/config"
	"ClashBOfClashBot/internal/api"
	"ClashBOfClashBot/internal/database"
	// "ClashBOfClashBot/internal/services"  // Temporarily disabled - requires model compatibility fixes
	"ClashBOfClashBot/internal/utils"
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

// ClashBot is the main bot structure
type ClashBot struct {
	config    *config.Config
	bot       *tgbotapi.BotAPI
	db        *database.DatabaseService
	cocClient *api.CocApiClient
	// warArchiver     *services.WarArchiver     // Temporarily disabled
	// buildingMonitor *services.BuildingMonitor // Temporarily disabled
	
	// Handlers
	messageHandler  *MessageHandler
	callbackHandler *CallbackHandler
	messageGen      *MessageGenerator
	
	// Context for cancellation
	ctx    context.Context
	cancel context.CancelFunc
}

// NewClashBot creates a new ClashBot instance
func NewClashBot(cfg *config.Config) (*ClashBot, error) {
	bot, err := tgbotapi.NewBotAPI(cfg.BotToken)
	if err != nil {
		return nil, fmt.Errorf("failed to create bot: %w", err)
	}
	
	bot.Debug = false
	log.Printf("Authorized on account %s", bot.Self.UserName)
	
	// Create context for graceful shutdown
	ctx, cancel := context.WithCancel(context.Background())
	
	clashBot := &ClashBot{
		config: cfg,
		bot:    bot,
		ctx:    ctx,
		cancel: cancel,
	}
	
	return clashBot, nil
}

// Initialize initializes all bot components
func (b *ClashBot) Initialize() error {
	log.Println("🔧 Initializing bot components...")
	
	// Initialize database
	var err error
	b.db, err = database.NewDatabaseService(b.config.DatabasePath)
	if err != nil {
		return fmt.Errorf("failed to initialize database: %w", err)
	}
	log.Println("✅ Database initialized")
	
	// Initialize COC API client
	b.cocClient = api.NewCocApiClient("https://api.clashofclans.com/v1", b.config.CocAPIToken)
	log.Println("✅ COC API client initialized")
	
	// Initialize message generator
	b.messageGen = NewMessageGenerator(b.db, b.cocClient, b.config)
	log.Println("✅ Message generator initialized")
	
	// Initialize handlers
	b.messageHandler = NewMessageHandler(b.messageGen)
	b.callbackHandler = NewCallbackHandler(b.messageGen)
	log.Println("✅ Handlers initialized")
	
	// Start background services
	if err := b.startBackgroundServices(); err != nil {
		return fmt.Errorf("failed to start background services: %w", err)
	}
	
	log.Println("✅ Bot components initialized successfully")
	return nil
}

// startBackgroundServices starts the war archiver and building monitor
func (b *ClashBot) startBackgroundServices() error {
	// TODO: Fix compatibility issues in services layer
	// Start War Archiver
	/*
	b.warArchiver = services.NewWarArchiver(
		b.config.OurClanTag,
		b.db,
		b.cocClient,
		b.bot,
	)
	go b.warArchiver.Start(b.ctx)
	log.Printf("✅ War archiver started for clan %s", b.config.OurClanTag)
	*/
	
	// Start Building Monitor
	/*
	b.buildingMonitor = services.NewBuildingMonitor(
		b.db,
		b.cocClient,
		b.bot,
	)
	go b.buildingMonitor.Start(b.ctx)
	log.Println("✅ Building monitor started")
	*/
	
	log.Println("⚠️  Background services (War Archiver, Building Monitor) temporarily disabled - require model compatibility fixes")
	
	return nil
}

// Run starts the bot and handles updates
func (b *ClashBot) Run() error {
	log.Println("🚀 Starting bot...")
	
	u := tgbotapi.NewUpdate(0)
	u.Timeout = 60
	
	updates := b.bot.GetUpdatesChan(u)
	
	// Setup graceful shutdown
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	
	log.Println("✅ Bot is running. Press Ctrl+C to stop.")
	
	for {
		select {
		case <-stop:
			log.Println("🛑 Received interrupt signal, shutting down...")
			b.Shutdown()
			return nil
			
		case update := <-updates:
			if update.Message != nil {
				go b.handleMessage(update)
			} else if update.CallbackQuery != nil {
				go b.handleCallback(update)
			}
		}
	}
}

// handleMessage handles incoming text messages
func (b *ClashBot) handleMessage(update tgbotapi.Update) {
	// Handle /start command
	if update.Message.IsCommand() {
		switch update.Message.Command() {
		case "start":
			b.handleStartCommand(update)
		case "help":
			b.handleHelpCommand(update)
		default:
			msg := tgbotapi.NewMessage(update.Message.Chat.ID, 
				"Неизвестная команда. Используйте меню для навигации.")
			msg.ReplyMarkup = MainMenu()
			b.bot.Send(msg)
		}
		return
	}
	
	// Handle text messages through message handler
	if err := b.messageHandler.HandleMessage(&update, b.bot); err != nil {
		log.Printf("Error handling message: %v", err)
	}
}

// handleCallback handles callback queries from inline keyboards
func (b *ClashBot) handleCallback(update tgbotapi.Update) {
	if err := b.callbackHandler.HandleCallback(&update, b.bot); err != nil {
		log.Printf("Error handling callback: %v", err)
	}
}

// handleStartCommand handles the /start command
func (b *ClashBot) handleStartCommand(update tgbotapi.Update) {
	welcomeText := `🎮 *Добро пожаловать в ClashBot!*

🏆 *Все функции бота:*

👤 *ПРОФИЛИ И ИГРОКИ*
• Привязка и управление профилями игроков
• Просмотр детальной статистики игрока
• Поиск игроков по тегу
• Менеджер нескольких профилей (Премиум)

🛡 *КЛАНЫ И ВОЙНЫ*
• Информация о клане и участниках
• История клановых войн
• Текущие войны и ЛВК
• Анализ атак и нарушений
• Привязка нескольких кланов

🔔 *УВЕДОМЛЕНИЯ*
• Автоматические уведомления о войнах
• Персональная настройка времени (Премиум)
• Уведомления об улучшениях зданий (Премиум)

💎 *ПРЕМИУМ ФУНКЦИИ*
• 🏗️ Отслеживание улучшений зданий в реальном времени
• 👥 Управление несколькими профилями
• ⚙️ Расширенные настройки уведомлений
• 📊 Дополнительная статистика

📋 [Политика использования](` + utils.GetPolicyURL() + `)

Используйте меню ниже для навигации:`

	msg := tgbotapi.NewMessage(update.Message.Chat.ID, welcomeText)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = MainMenu()
	b.bot.Send(msg)
}

// handleHelpCommand handles the /help command
func (b *ClashBot) handleHelpCommand(update tgbotapi.Update) {
	helpText := `📖 *Помощь по использованию бота*

*Основные разделы:*
👤 Профиль - управление вашими игровыми профилями
🛡 Клан - информация о кланах и войнах
🔔 Уведомления - настройка уведомлений
🏛️ Центр сообщества - полезная информация
💎 Премиум - премиум функции

*Команды:*
/start - главное меню
/help - эта справка

По всем вопросам обращайтесь к @Negodayo`

	msg := tgbotapi.NewMessage(update.Message.Chat.ID, helpText)
	msg.ParseMode = "Markdown"
	msg.ReplyMarkup = MainMenu()
	b.bot.Send(msg)
}

// Shutdown gracefully shuts down the bot
func (b *ClashBot) Shutdown() {
	log.Println("🔄 Shutting down bot...")
	
	// Cancel context to stop background services
	b.cancel()
	
	// Close database connection
	if b.db != nil {
		b.db.Close()
		log.Println("✅ Database connection closed")
	}
	
	// Stop bot
	b.bot.StopReceivingUpdates()
	log.Println("✅ Bot stopped receiving updates")
	
	log.Println("✅ Bot shutdown complete")
}
