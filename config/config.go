package config

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

// Config holds all bot configuration
type Config struct {
	// Telegram Bot Configuration
	BotToken    string
	BotUsername string

	// Clash of Clans API
	CocAPIToken   string
	CocAPIBaseURL string

	// YooKassa Payment Gateway
	YooKassaShopID    string
	YooKassaSecretKey string

	// Database
	DatabasePath string

	// Clan Settings
	OurClanTag string

	// Archive Settings
	ArchiveCheckInterval     int // seconds
	DonationSnapshotInterval int // seconds
}

var AppConfig *Config

// LoadConfig reads configuration from api_tokens.txt and environment variables
func LoadConfig() (*Config, error) {
	cfg := &Config{
		// Default values
		CocAPIBaseURL:            "https://api.clashofclans.com/v1",
		DatabasePath:             "clashbot.db",
		OurClanTag:               "#2PQU0PLJ2",
		ArchiveCheckInterval:     900,   // 15 minutes
		DonationSnapshotInterval: 21600, // 6 hours
	}

	// Read from api_tokens.txt
	tokens, err := readAPITokens("api_tokens.txt")
	if err != nil {
		// Not critical, we can use environment variables
		fmt.Printf("Warning: Could not read api_tokens.txt: %v\n", err)
	}

	// Load configuration with priority: api_tokens.txt -> env variables
	cfg.BotToken = getConfigValue(tokens, "BOT_TOKEN", "BOT_TOKEN", "")
	cfg.BotUsername = getConfigValue(tokens, "BOT_USERNAME", "BOT_USERNAME", "")
	cfg.CocAPIToken = getConfigValue(tokens, "COC_API_TOKEN", "COC_API_TOKEN", "")
	cfg.YooKassaShopID = getConfigValue(tokens, "YOOKASSA_SHOP_ID", "YOOKASSA_SHOP_ID", "")
	cfg.YooKassaSecretKey = getConfigValue(tokens, "YOOKASSA_SECRET_KEY", "YOOKASSA_SECRET_KEY", "")

	// Optional overrides from environment
	if dbPath := os.Getenv("DATABASE_PATH"); dbPath != "" {
		cfg.DatabasePath = dbPath
	}
	if clanTag := os.Getenv("OUR_CLAN_TAG"); clanTag != "" {
		cfg.OurClanTag = clanTag
	}
	if interval := os.Getenv("ARCHIVE_CHECK_INTERVAL"); interval != "" {
		if val, err := strconv.Atoi(interval); err == nil {
			cfg.ArchiveCheckInterval = val
		}
	}
	if interval := os.Getenv("DONATION_SNAPSHOT_INTERVAL"); interval != "" {
		if val, err := strconv.Atoi(interval); err == nil {
			cfg.DonationSnapshotInterval = val
		}
	}

	// Validate required fields
	if err := cfg.Validate(); err != nil {
		return nil, err
	}

	AppConfig = cfg
	return cfg, nil
}

// Validate checks if all required configuration is present
func (c *Config) Validate() error {
	if c.BotToken == "" {
		return fmt.Errorf("BOT_TOKEN is not set. Add token to api_tokens.txt or set environment variable BOT_TOKEN")
	}
	if c.CocAPIToken == "" {
		return fmt.Errorf("COC_API_TOKEN is not set. Add token to api_tokens.txt or set environment variable COC_API_TOKEN")
	}
	return nil
}

// readAPITokens reads tokens from api_tokens.txt file
func readAPITokens(filename string) (map[string]string, error) {
	tokens := make(map[string]string)

	// Try current directory first
	file, err := os.Open(filename)
	if err != nil {
		return tokens, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())

		// Skip comments and empty lines
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		// Parse key=value
		parts := strings.SplitN(line, "=", 2)
		if len(parts) == 2 {
			key := strings.TrimSpace(parts[0])
			value := strings.TrimSpace(parts[1])
			tokens[key] = value
		}
	}

	if err := scanner.Err(); err != nil {
		return tokens, err
	}

	return tokens, nil
}

// getConfigValue gets configuration value with priority: file -> env -> default
func getConfigValue(tokens map[string]string, tokenKey, envKey, defaultValue string) string {
	// First try tokens file
	if val, ok := tokens[tokenKey]; ok && val != "" {
		return val
	}
	// Then try environment
	if val := os.Getenv(envKey); val != "" {
		return val
	}
	// Finally use default
	return defaultValue
}
