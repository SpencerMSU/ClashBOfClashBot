package main

import (
	"log"

	"clashbot/internal/bot"
	"clashbot/internal/config"
)

func main() {
	// Инициализация логирования
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	log.Println("Запуск бота Clash of Clans...")

	// Загрузка конфигурации
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Ошибка загрузки конфигурации: %v", err)
	}

	// Проверка обязательных параметров
	if cfg.BotToken == "" {
		log.Fatal("BOT_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменную окружения BOT_TOKEN.")
	}

	if cfg.CocAPIToken == "" {
		log.Fatal("COC_API_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменную окружения COC_API_TOKEN.")
	}

	// Создание и запуск бота
	clashBot, err := bot.New(cfg)
	if err != nil {
		log.Fatalf("Ошибка создания бота: %v", err)
	}

	// Запуск бота
	if err := clashBot.Run(); err != nil {
		log.Fatalf("Ошибка при работе бота: %v", err)
	}
}