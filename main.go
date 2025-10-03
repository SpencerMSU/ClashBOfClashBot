package main

import (
	"fmt"
	"log"
	"os"

	"ClashBOfClashBot/config"
	"ClashBOfClashBot/internal/bot"
)

func main() {
	// Setup logging
	log.SetOutput(os.Stdout)
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)

	log.Println("🚀 Запуск бота Clash of Clans...")

	// Load configuration
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("❌ Ошибка загрузки конфигурации: %v", err)
	}

	log.Printf("✅ Конфигурация загружена успешно")
	log.Printf("📱 Bot Username: %s", cfg.BotUsername)
	log.Printf("🗄️  Database: %s", cfg.DatabasePath)

	fmt.Println(`
┌─────────────────────────────────────────────┐
│                                             │
│    🎮 ClashBot - Golang Edition 🎮         │
│                                             │
│    ✅ Конфигурация загружена                │
│    🔄 Инициализация компонентов...          │
│                                             │
│    Статус миграции:                         │
│    ├── ✅ Модели (models)                   │
│    ├── ✅ Конфигурация (config)             │
│    ├── ✅ База данных (database)            │
│    ├── ✅ COC API (api)                     │
│    ├── ✅ Обработчики (handlers)            │
│    ├── ✅ Клавиатуры (keyboards)            │
│    ├── ✅ Сервисы (services)                │
│    ├── ✅ User State                        │
│    ├── ✅ Policy                            │
│    └── ✅ Основной бот (bot)                │
│                                             │
└─────────────────────────────────────────────┘
	`)

	log.Println("🔧 Создание экземпляра бота...")
	
	// Create bot instance
	clashBot, err := bot.NewClashBot(cfg)
	if err != nil {
		log.Fatalf("❌ Ошибка создания бота: %v", err)
	}
	
	// Initialize bot components
	if err := clashBot.Initialize(); err != nil {
		log.Fatalf("❌ Ошибка инициализации бота: %v", err)
	}
	
	log.Println("✅ Бот успешно инициализирован")
	log.Println("📝 Примечание: Полная функциональность message_generator (~52 метода) требует дополнительной реализации")
	log.Println("📝 Текущая версия включает базовую структуру и основные обработчики")
	
	// Run bot
	if err := clashBot.Run(); err != nil {
		log.Fatalf("❌ Ошибка запуска бота: %v", err)
	}
}
