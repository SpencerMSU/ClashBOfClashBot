package main

import (
	"fmt"
	"log"
	"os"

	"clashbot/internal/config"
)

// validateSetup валидирует настройку бота
func validateSetup() {
	fmt.Println("🔍 ClashBot - Диагностика установки")
	fmt.Println("=====================================")

	// 1. Проверка Go версии
	fmt.Println("\n📦 Проверка среды:")
	fmt.Printf("   Go версия: %s\n", os.Getenv("GOVERSION"))

	// 2. Проверка файлов конфигурации
	fmt.Println("\n⚙️ Проверка конфигурации:")
	
	if _, err := os.Stat("api_tokens.txt"); os.IsNotExist(err) {
		fmt.Println("   ❌ Файл api_tokens.txt не найден")
		fmt.Println("   💡 Создайте файл api_tokens.txt с необходимыми токенами")
		fmt.Println("   📖 См. GO-LANG-VER-SETUP.md для подробностей")
	} else {
		fmt.Println("   ✅ Файл api_tokens.txt найден")
	}

	// 3. Попытка загрузки конфигурации
	fmt.Println("\n🔧 Проверка загрузки конфигурации:")
	cfg, err := config.Load()
	if err != nil {
		fmt.Printf("   ❌ Ошибка загрузки конфигурации: %v\n", err)
		return
	}
	fmt.Println("   ✅ Конфигурация загружена")

	// 4. Проверка обязательных параметров
	fmt.Println("\n🔑 Проверка токенов:")
	
	if cfg.BotToken == "" {
		fmt.Println("   ❌ BOT_TOKEN не установлен")
		fmt.Println("   💡 Добавьте BOT_TOKEN в api_tokens.txt")
	} else {
		fmt.Printf("   ✅ BOT_TOKEN установлен (длина: %d)\n", len(cfg.BotToken))
	}

	if cfg.CocAPIToken == "" {
		fmt.Println("   ❌ COC_API_TOKEN не установлен")
		fmt.Println("   💡 Добавьте COC_API_TOKEN в api_tokens.txt")
	} else {
		fmt.Printf("   ✅ COC_API_TOKEN установлен (длина: %d)\n", len(cfg.CocAPIToken))
	}

	// 5. Проверка необязательных параметров
	fmt.Println("\n🔧 Дополнительные настройки:")
	if cfg.BotUsername == "" {
		fmt.Println("   ⚠️ BOT_USERNAME не установлен (не критично)")
	} else {
		fmt.Printf("   ✅ BOT_USERNAME: @%s\n", cfg.BotUsername)
	}

	fmt.Printf("   📂 Путь к БД: %s\n", cfg.DatabasePath)
	fmt.Printf("   🛡 Тег клана: %s\n", cfg.OurClanTag)

	// 6. Проверка Python для платежей
	fmt.Println("\n🐍 Проверка Python компонентов:")
	if _, err := os.Stat("payment_bridge.py"); os.IsNotExist(err) {
		fmt.Println("   ❌ payment_bridge.py не найден")
	} else {
		fmt.Println("   ✅ payment_bridge.py найден")
	}

	// 7. Валидация полной конфигурации
	fmt.Println("\n✅ Итоговая проверка:")
	if err := cfg.Validate(); err != nil {
		fmt.Printf("   ❌ Конфигурация невалидна: %v\n", err)
		fmt.Println("\n🚨 Исправьте ошибки перед запуском бота!")
		return
	}

	fmt.Println("   ✅ Конфигурация валидна")
	fmt.Println("\n🎉 Бот готов к запуску!")
	fmt.Println("   Запустите: go run main.go")
}

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	validateSetup()
}