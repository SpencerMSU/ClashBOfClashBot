package config

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

// Config представляет конфигурацию бота
type Config struct {
	// Основные токены и настройки
	BotToken     string
	BotUsername  string
	CocAPIToken  string

	// YooKassa платежные реквизиты  
	YooKassaShopID    string
	YooKassaSecretKey string

	// Настройки базы данных
	DatabasePath string

	// Настройки клана
	OurClanTag string

	// Настройки API
	CocAPIBaseURL string

	// Настройки архивации
	ArchiveCheckInterval    int // в секундах
	DonationSnapshotInterval int // в секундах
}

// Load загружает конфигурацию из файла api_tokens.txt и переменных окружения
func Load() (*Config, error) {
	cfg := &Config{
		// Значения по умолчанию
		DatabasePath:             "clashbot.db",
		OurClanTag:              "#2PQU0PLJ2",
		CocAPIBaseURL:           "https://api.clashofclans.com/v1",
		ArchiveCheckInterval:     900,  // 15 минут
		DonationSnapshotInterval: 21600, // 6 часов
	}

	// Сначала читаем токены из файла
	apiTokens, err := readAPITokens("api_tokens.txt")
	if err != nil {
		// Файл может не существовать, это не критично
		apiTokens = make(map[string]string)
	}

	// Загружаем основные настройки
	cfg.BotToken = getConfigValue(apiTokens, "BOT_TOKEN", "")
	cfg.BotUsername = getConfigValue(apiTokens, "BOT_USERNAME", "")
	cfg.CocAPIToken = getConfigValue(apiTokens, "COC_API_TOKEN", "")
	cfg.YooKassaShopID = getConfigValue(apiTokens, "YOOKASSA_SHOP_ID", "")
	cfg.YooKassaSecretKey = getConfigValue(apiTokens, "YOOKASSA_SECRET_KEY", "")

	// Переменные окружения (с возможностью переопределения)
	if val := os.Getenv("DATABASE_PATH"); val != "" {
		cfg.DatabasePath = val
	}
	if val := os.Getenv("OUR_CLAN_TAG"); val != "" {
		cfg.OurClanTag = val
	}
	if val := os.Getenv("ARCHIVE_CHECK_INTERVAL"); val != "" {
		if interval, err := strconv.Atoi(val); err == nil {
			cfg.ArchiveCheckInterval = interval
		}
	}
	if val := os.Getenv("DONATION_SNAPSHOT_INTERVAL"); val != "" {
		if interval, err := strconv.Atoi(val); err == nil {
			cfg.DonationSnapshotInterval = interval
		}
	}

	return cfg, nil
}

// readAPITokens читает токены из текстового файла
func readAPITokens(filename string) (map[string]string, error) {
	tokens := make(map[string]string)

	file, err := os.Open(filename)
	if err != nil {
		return tokens, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		
		// Пропускаем пустые строки и комментарии
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		// Парсим строки формата KEY=VALUE
		parts := strings.SplitN(line, "=", 2)
		if len(parts) == 2 {
			key := strings.TrimSpace(parts[0])
			value := strings.TrimSpace(parts[1])
			tokens[key] = value
		}
	}

	return tokens, scanner.Err()
}

// getConfigValue получает значение конфигурации сначала из файла, потом из переменных окружения
func getConfigValue(apiTokens map[string]string, key, defaultValue string) string {
	// Сначала проверяем файл токенов
	if value, exists := apiTokens[key]; exists && value != "" {
		return value
	}
	// Потом переменные окружения
	if value := os.Getenv(key); value != "" {
		return value
	}
	// И наконец значение по умолчанию
	return defaultValue
}

// Validate проверяет обязательные параметры конфигурации
func (c *Config) Validate() error {
	if c.BotToken == "" {
		return fmt.Errorf("BOT_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменные окружения")
	}
	if c.CocAPIToken == "" {
		return fmt.Errorf("COC_API_TOKEN не установлен. Добавьте токен в файл api_tokens.txt или переменные окружения")
	}
	return nil
}