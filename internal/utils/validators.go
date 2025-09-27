package utils

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/sirupsen/logrus"
	
	"clashbot-go/internal/config"
	"clashbot-go/internal/database"
	"clashbot-go/internal/services"
)

// ComponentValidator validates bot components - exact copy from Python validate.py
type ComponentValidator struct {
	logger *logrus.Logger
}

// NewComponentValidator creates a new component validator
func NewComponentValidator() *ComponentValidator {
	return &ComponentValidator{
		logger: logrus.StandardLogger(),
	}
}

// ValidateComponents validates all bot components - exact copy from Python validate_components()
func (cv *ComponentValidator) ValidateComponents() error {
	cv.logger.Info("🔍 Starting component validation...")
	
	// Validate configuration
	if err := cv.validateConfig(); err != nil {
		return fmt.Errorf("configuration validation failed: %w", err)
	}
	cv.logger.Info("✅ Configuration validation passed")
	
	// Validate database
	if err := cv.validateDatabase(); err != nil {
		return fmt.Errorf("database validation failed: %w", err)
	}
	cv.logger.Info("✅ Database validation passed")
	
	// Validate API services
	if err := cv.validateAPIServices(); err != nil {
		return fmt.Errorf("API services validation failed: %w", err)
	}
	cv.logger.Info("✅ API services validation passed")
	
	// Validate file structure
	if err := cv.validateFileStructure(); err != nil {
		return fmt.Errorf("file structure validation failed: %w", err)
	}
	cv.logger.Info("✅ File structure validation passed")
	
	cv.logger.Info("🎉 All component validations passed successfully!")
	return nil
}

// validateConfig validates configuration - exact copy from Python
func (cv *ComponentValidator) validateConfig() error {
	cv.logger.Info("Validating configuration...")
	
	// Load and validate configuration
	config, err := config.LoadConfig()
	if err != nil {
		return fmt.Errorf("failed to load configuration: %w", err)
	}
	
	// Check required fields
	if config.BotToken == "" {
		return fmt.Errorf("BOT_TOKEN is required")
	}
	
	if config.CocAPIToken == "" {
		return fmt.Errorf("COC_API_TOKEN is required")
	}
	
	// Check optional but recommended fields
	if config.BotUsername == "" {
		cv.logger.Warn("BOT_USERNAME is not set - some features may not work correctly")
	}
	
	if config.YooKassaShopID == "" || config.YooKassaSecretKey == "" {
		cv.logger.Warn("YooKassa credentials not set - payment features will use test mode")
	}
	
	cv.logger.Info("Configuration loaded successfully")
	return nil
}

// validateDatabase validates database connection and schema - exact copy from Python
func (cv *ComponentValidator) validateDatabase() error {
	cv.logger.Info("Validating database...")
	
	// Create database service
	dbService, err := database.NewDatabaseService("")
	if err != nil {
		return fmt.Errorf("failed to create database service: %w", err)
	}
	defer dbService.Close()
	
	// Test basic operations
	if err := cv.testDatabaseOperations(dbService); err != nil {
		return fmt.Errorf("database operations test failed: %w", err)
	}
	
	cv.logger.Info("Database connection and schema validated")
	return nil
}

// testDatabaseOperations tests basic database operations
func (cv *ComponentValidator) testDatabaseOperations(db *database.DatabaseService) error {
	// Test user operations
	testTelegramID := int64(123456789)
	
	// Save test user
	err := db.SaveUser(testTelegramID, "testuser", "Test", "User", "#TEST123", false, "en")
	if err != nil {
		return fmt.Errorf("failed to save test user: %w", err)
	}
	
	// Find test user
	user, err := db.FindUser(testTelegramID)
	if err != nil {
		return fmt.Errorf("failed to find test user: %w", err)
	}
	
	if user == nil {
		return fmt.Errorf("test user not found after saving")
	}
	
	// Clean up test user
	err = db.DeleteUser(testTelegramID)
	if err != nil {
		return fmt.Errorf("failed to delete test user: %w", err)
	}
	
	cv.logger.Debug("Database CRUD operations test passed")
	return nil
}

// validateAPIServices validates external API services - exact copy from Python
func (cv *ComponentValidator) validateAPIServices() error {
	cv.logger.Info("Validating API services...")
	
	// Load configuration
	config, err := config.LoadConfig()
	if err != nil {
		return fmt.Errorf("failed to load config for API validation: %w", err)
	}
	
	// Validate Clash of Clans API
	if err := cv.validateCocAPI(config); err != nil {
		return fmt.Errorf("CoC API validation failed: %w", err)
	}
	
	// Validate YooKassa service
	if err := cv.validateYooKassaService(config); err != nil {
		cv.logger.Warn("YooKassa validation failed (will use test mode): %v", err)
	}
	
	return nil
}

// validateCocAPI validates Clash of Clans API connection
func (cv *ComponentValidator) validateCocAPI(config *config.BotConfig) error {
	cv.logger.Info("Testing Clash of Clans API connection...")
	
	// Create CoC API client
	cocClient := services.NewCocApiClient(config.CocAPIToken, config.CocAPIBaseURL)
	defer cocClient.Close()
	
	// Test with a known clan tag (Supercell's official clan)
	testClanTag := "#2PP"
	clan, err := cocClient.GetClan(testClanTag)
	if err != nil {
		return fmt.Errorf("failed to fetch test clan %s: %w", testClanTag, err)
	}
	
	if clan == nil {
		return fmt.Errorf("test clan %s not found", testClanTag)
	}
	
	cv.logger.Infof("CoC API test successful - fetched clan: %s", clan.Name)
	return nil
}

// validateYooKassaService validates YooKassa payment service
func (cv *ComponentValidator) validateYooKassaService(config *config.BotConfig) error {
	cv.logger.Info("Testing YooKassa service...")
	
	// Create YooKassa service
	yooKassaService := services.NewYooKassaService(
		config.YooKassaShopID,
		config.YooKassaSecretKey,
		config.BotUsername,
	)
	defer yooKassaService.Close()
	
	// Test subscription price retrieval
	price := yooKassaService.GetSubscriptionPrice("premium_1month")
	if price <= 0 {
		return fmt.Errorf("invalid subscription price: %f", price)
	}
	
	// Test subscription name retrieval
	name := yooKassaService.GetSubscriptionName("premium_1month")
	if name == "" {
		return fmt.Errorf("empty subscription name")
	}
	
	cv.logger.Infof("YooKassa service test successful - subscription: %s (%.2f RUB)", name, price)
	return nil
}

// validateFileStructure validates project file structure - exact copy from Python
func (cv *ComponentValidator) validateFileStructure() error {
	cv.logger.Info("Validating file structure...")
	
	// Required directories
	requiredDirs := []string{
		"internal/config",
		"internal/models",
		"internal/database",
		"internal/services",
		"internal/utils",
		"pkg/logger",
		"cmd/bot",
	}
	
	// Check required directories
	for _, dir := range requiredDirs {
		if err := cv.checkDirectory(dir); err != nil {
			return fmt.Errorf("directory validation failed: %w", err)
		}
	}
	
	// Required files
	requiredFiles := []string{
		"go.mod",
		"go.sum",
		"Makefile",
		"internal/config/config.go",
		"internal/models/user.go",
		"internal/database/database.go",
		"internal/services/coc_api.go",
		"internal/services/payment.go",
		"pkg/logger/logger.go",
	}
	
	// Check required files
	for _, file := range requiredFiles {
		if err := cv.checkFile(file); err != nil {
			return fmt.Errorf("file validation failed: %w", err)
		}
	}
	
	cv.logger.Info("File structure validation completed")
	return nil
}

// checkDirectory checks if directory exists
func (cv *ComponentValidator) checkDirectory(dir string) error {
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		return fmt.Errorf("required directory does not exist: %s", dir)
	}
	return nil
}

// checkFile checks if file exists
func (cv *ComponentValidator) checkFile(file string) error {
	if _, err := os.Stat(file); os.IsNotExist(err) {
		return fmt.Errorf("required file does not exist: %s", file)
	}
	return nil
}

// CreateTestTokensFile creates a test tokens file - exact copy from Python create_test_tokens_file()
func (cv *ComponentValidator) CreateTestTokensFile() error {
	cv.logger.Info("Creating test tokens file...")
	
	tokensFile := "api_tokens.txt"
	
	// Check if file already exists
	if _, err := os.Stat(tokensFile); err == nil {
		cv.logger.Info("Tokens file already exists, skipping creation")
		return nil
	}
	
	// Create test tokens content
	content := `# ClashBot API Tokens Configuration
# Replace with your actual tokens

# Telegram Bot Token (required)
# Get from @BotFather on Telegram
BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Bot Username (recommended)
# Your bot's username without @
BOT_USERNAME=YourBotUsername

# Clash of Clans API Token (required)
# Get from https://developer.clashofclans.com
COC_API_TOKEN=YOUR_COC_API_TOKEN_HERE

# YooKassa Payment Credentials (optional)
# Get from https://yookassa.ru
YOOKASSA_SHOP_ID=YOUR_SHOP_ID
YOOKASSA_SECRET_KEY=YOUR_SECRET_KEY

# Database Configuration (optional)
DATABASE_PATH=clashbot.db

# Clan Configuration (optional)
OUR_CLAN_TAG=#YOUR_CLAN_TAG

# Debug Mode (optional)
DEBUG=false

# Intervals (optional)
ARCHIVE_CHECK_INTERVAL=5m
DONATION_SNAPSHOT_INTERVAL=6h
BUILDING_MONITOR_INTERVAL=30s
`
	
	// Write file
	err := os.WriteFile(tokensFile, []byte(content), 0644)
	if err != nil {
		return fmt.Errorf("failed to create tokens file: %w", err)
	}
	
	cv.logger.Infof("Test tokens file created: %s", tokensFile)
	cv.logger.Info("Please edit the file and add your actual tokens")
	return nil
}

// GetProjectStats returns project statistics
func (cv *ComponentValidator) GetProjectStats() map[string]interface{} {
	stats := make(map[string]interface{})
	
	// Count Go files
	goFiles := 0
	totalLines := 0
	
	err := filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		
		if filepath.Ext(path) == ".go" && !info.IsDir() {
			goFiles++
			
			// Count lines in file
			if content, err := os.ReadFile(path); err == nil {
				lines := len(strings.Split(string(content), "\n"))
				totalLines += lines
			}
		}
		
		return nil
	})
	
	if err != nil {
		cv.logger.Errorf("Error walking project files: %v", err)
	}
	
	stats["go_files"] = goFiles
	stats["total_lines"] = totalLines
	stats["project_status"] = "migration_in_progress"
	
	return stats
}

// RunFullValidation runs complete validation suite
func (cv *ComponentValidator) RunFullValidation() error {
	cv.logger.Info("🚀 Starting full validation suite...")
	
	// Run component validation
	if err := cv.ValidateComponents(); err != nil {
		return fmt.Errorf("component validation failed: %w", err)
	}
	
	// Print project statistics
	stats := cv.GetProjectStats()
	cv.logger.Infof("📊 Project Statistics:")
	cv.logger.Infof("   - Go files: %d", stats["go_files"])
	cv.logger.Infof("   - Total lines: %d", stats["total_lines"])
	cv.logger.Infof("   - Status: %s", stats["project_status"])
	
	cv.logger.Info("✅ Full validation completed successfully!")
	return nil
}