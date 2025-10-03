package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"ClashBOfClashBot/config"
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

	// TODO: Initialize components
	// 1. Database Service
	// 2. COC API Client
	// 3. Payment Service
	// 4. Message Generator
	// 5. Handlers
	// 6. Bot Instance

	fmt.Println(`
┌─────────────────────────────────────────────┐
│                                             │
│    🎮 ClashBot - Golang Edition 🎮         │
│                                             │
│    ✅ Конфигурация загружена                │
│    ⏳ Инициализация компонентов...          │
│                                             │
│    Статус миграции:                         │
│    ├── ✅ Модели (models)                   │
│    ├── ✅ Конфигурация (config)             │
│    ├── ⏳ База данных (database)            │
│    ├── ⏳ COC API (api)                     │
│    ├── ⏳ Обработчики (handlers)            │
│    ├── ⏳ Клавиатуры (keyboards)            │
│    ├── ⏳ Сервисы (services)                │
│    └── ⏳ Основной бот (bot)                │
│                                             │
└─────────────────────────────────────────────┘
	`)

	log.Println("⚠️  МИГРАЦИЯ В ПРОЦЕССЕ: Полная функциональность будет доступна после завершения переноса всех компонентов")
	log.Println("📚 См. ADMINSTR.md для инструкций по запуску")

	// Setup graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)

	// Wait for interrupt signal
	<-sigChan
	log.Println("\n🛑 Получен сигнал завершения, останавливаем бота...")

	// TODO: Cleanup
	// - Close database connections
	// - Stop background workers
	// - Save state

	log.Println("✅ Бот успешно остановлен")
}
