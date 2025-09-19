package main

import (
	"log"

	"clashbot/internal/bot"
	"clashbot/internal/config"
)

func main() {
	// Инициализация логирования
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	log.Println("🚀 Запуск бота Clash of Clans...")

	// Показываем диагностическую информацию
	log.Println("📋 Инициализация компонентов:")

	// Загрузка конфигурации
	log.Println("  ⏳ Загрузка конфигурации...")
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("❌ Ошибка загрузки конфигурации: %v", err)
	}
	log.Println("  ✅ Конфигурация загружена")

	// Проверка обязательных параметров
	log.Println("  ⏳ Валидация конфигурации...")
	if cfg.BotToken == "" {
		log.Fatal("❌ BOT_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменную окружения BOT_TOKEN.")
	}

	if cfg.CocAPIToken == "" {
		log.Fatal("❌ COC_API_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменную окружения COC_API_TOKEN.")
	}
	log.Println("  ✅ Конфигурация валидна")

	// Создание и запуск бота
	log.Println("  ⏳ Инициализация бота...")
	clashBot, err := bot.New(cfg)
	if err != nil {
		log.Fatalf("❌ Ошибка создания бота: %v", err)
	}
	log.Println("  ✅ Бот инициализирован")

	// Запуск бота
	log.Println("🎯 Запуск основного цикла бота...")
	if err := clashBot.Run(); err != nil {
		log.Fatalf("❌ Ошибка при работе бота: %v", err)
	}
}