package config

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/sirupsen/logrus"
	"github.com/spf13/viper"
)

// BotConfig holds all bot configuration - exact copy from Python config.py
type BotConfig struct {
	// Main bot configuration
	BotToken    string `mapstructure:"bot_token"`
	BotUsername string `mapstructure:"bot_username"`

	// Clash of Clans API
	CocAPIToken   string `mapstructure:"coc_api_token"`
	CocAPIBaseURL string `mapstructure:"coc_api_base_url"`

	// Database
	DatabasePath string `mapstructure:"database_path"`

	// YooKassa payment configuration
	YooKassaShopID    string `mapstructure:"yookassa_shop_id"`
	YooKassaSecretKey string `mapstructure:"yookassa_secret_key"`

	// Archive settings
	ArchiveCheckInterval      time.Duration `mapstructure:"archive_check_interval"`
	DonationSnapshotInterval  time.Duration `mapstructure:"donation_snapshot_interval"`
	BuildingMonitorInterval   time.Duration `mapstructure:"building_monitor_interval"`

	// Clan configuration
	OurClanTag string `mapstructure:"our_clan_tag"`

	// Debug settings
	Debug bool `mapstructure:"debug"`
}

var Config *BotConfig

// LoadConfig loads configuration from various sources - copy of Python _read_api_tokens
func LoadConfig() (*BotConfig, error) {
	// First try to read from api_tokens.txt file
	tokens := readAPITokens("api_tokens.txt")

	config := &BotConfig{
		// Set defaults first, then override with file/env values
		CocAPIBaseURL:             "https://api.clashofclans.com/v1",
		DatabasePath:              "clashbot.db",
		ArchiveCheckInterval:      5 * time.Minute,
		DonationSnapshotInterval:  6 * time.Hour,
		BuildingMonitorInterval:   30 * time.Second,
		Debug:                     false,
	}

	// Priority: file values -> environment variables -> defaults
	config.BotToken = getConfigValue(tokens["BOT_TOKEN"], os.Getenv("BOT_TOKEN"), "")
	config.BotUsername = getConfigValue(tokens["BOT_USERNAME"], os.Getenv("BOT_USERNAME"), "")
	config.CocAPIToken = getConfigValue(tokens["COC_API_TOKEN"], os.Getenv("COC_API_TOKEN"), "")

	// YooKassa configuration
	config.YooKassaShopID = getConfigValue(tokens["YOOKASSA_SHOP_ID"], os.Getenv("YOOKASSA_SHOP_ID"), "")
	config.YooKassaSecretKey = getConfigValue(tokens["YOOKASSA_SECRET_KEY"], os.Getenv("YOOKASSA_SECRET_KEY"), "")

	// Other settings
	config.OurClanTag = getConfigValue(tokens["OUR_CLAN_TAG"], os.Getenv("OUR_CLAN_TAG"), "")
	config.DatabasePath = getConfigValue(tokens["DATABASE_PATH"], os.Getenv("DATABASE_PATH"), config.DatabasePath)

	// Parse interval settings
	if archiveInterval := getConfigValue(tokens["ARCHIVE_CHECK_INTERVAL"], os.Getenv("ARCHIVE_CHECK_INTERVAL"), ""); archiveInterval != "" {
		if interval, err := time.ParseDuration(archiveInterval); err == nil {
			config.ArchiveCheckInterval = interval
		}
	}

	if donationInterval := getConfigValue(tokens["DONATION_SNAPSHOT_INTERVAL"], os.Getenv("DONATION_SNAPSHOT_INTERVAL"), ""); donationInterval != "" {
		if interval, err := time.ParseDuration(donationInterval); err == nil {
			config.DonationSnapshotInterval = interval
		}
	}

	if buildingInterval := getConfigValue(tokens["BUILDING_MONITOR_INTERVAL"], os.Getenv("BUILDING_MONITOR_INTERVAL"), ""); buildingInterval != "" {
		if interval, err := time.ParseDuration(buildingInterval); err == nil {
			config.BuildingMonitorInterval = interval
		}
	}

	// Debug setting
	if debugStr := getConfigValue(tokens["DEBUG"], os.Getenv("DEBUG"), "false"); debugStr != "" {
		if debug, err := strconv.ParseBool(debugStr); err == nil {
			config.Debug = debug
		}
	}

	// Validate required configuration
	if err := config.validate(); err != nil {
		return nil, err
	}

	Config = config
	return config, nil
}

// readAPITokens reads API tokens from text file - exact copy from Python
func readAPITokens(filename string) map[string]string {
	tokens := make(map[string]string)

	// First try current directory
	filePath := filename
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		// Try script directory
		if execPath, err := os.Executable(); err == nil {
			scriptDir := filepath.Dir(execPath)
			filePath = filepath.Join(scriptDir, filename)
		}
	}

	file, err := os.Open(filePath)
	if err != nil {
		logrus.Warnf("Could not read tokens file %s: %v", filename, err)
		return tokens
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		// Skip comments and empty lines
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		if strings.Contains(line, "=") {
			parts := strings.SplitN(line, "=", 2)
			if len(parts) == 2 {
				key := strings.TrimSpace(parts[0])
				value := strings.TrimSpace(parts[1])
				tokens[key] = value
			}
		}
	}

	if err := scanner.Err(); err != nil {
		logrus.Errorf("Error reading tokens file %s: %v", filename, err)
	}

	return tokens
}

// getConfigValue returns the first non-empty value from the given options
func getConfigValue(options ...string) string {
	for _, option := range options {
		if option != "" {
			return option
		}
	}
	return ""
}

// validate validates the required configuration parameters - copy from Python _validate_config
func (c *BotConfig) validate() error {
	if c.BotToken == "" {
		return fmt.Errorf("BOT_TOKEN is required. Add it to api_tokens.txt or BOT_TOKEN environment variable")
	}

	if c.CocAPIToken == "" {
		return fmt.Errorf("COC_API_TOKEN is required. Add it to api_tokens.txt or COC_API_TOKEN environment variable")
	}

	if c.BotUsername == "" {
		logrus.Warn("BOT_USERNAME not set. Some features may not work correctly")
	}

	return nil
}

// SetupViper configures viper for additional config file support
func SetupViper() {
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath("./configs")
	viper.AddConfigPath(".")

	// Environment variables
	viper.SetEnvPrefix("CLASHBOT")
	viper.AutomaticEnv()
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

	// Read config file if it exists
	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			logrus.Errorf("Error reading config file: %v", err)
		}
	}
}