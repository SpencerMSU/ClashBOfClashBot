package main

import (
	"context"
	"os"
	"os/signal"
	"syscall"

	"clashbot-go/internal/config"
	"clashbot-go/internal/utils"
	"clashbot-go/pkg/logger"
)

// main is the entry point - exact copy from Python main.py structure
func main() {
	// Load configuration
	cfg, err := config.LoadConfig()
	if err != nil {
		logger.GetLogger().Fatalf("Failed to load configuration: %v", err)
	}

	// Initialize logger
	logger.InitLogger(cfg.Debug)
	log := logger.GetLogger()

	log.Info("🚀 Starting ClashBot Go version...")

	// Validate configuration
	if cfg.BotToken == "" {
		log.Error("BOT_TOKEN not set. Add token to api_tokens.txt or BOT_TOKEN environment variable.")
		return
	}

	if cfg.CocAPIToken == "" {
		log.Error("COC_API_TOKEN not set. Add token to api_tokens.txt or COC_API_TOKEN environment variable.")
		return
	}

	// Run component validation if requested
	if len(os.Args) > 1 && os.Args[1] == "--validate" {
		validator := utils.NewComponentValidator()
		if err := validator.RunFullValidation(); err != nil {
			log.Fatalf("Validation failed: %v", err)
		}
		log.Info("✅ All validations passed! Bot is ready to start.")
		return
	}

	// Create test tokens file if requested
	if len(os.Args) > 1 && os.Args[1] == "--create-tokens" {
		validator := utils.NewComponentValidator()
		if err := validator.CreateTestTokensFile(); err != nil {
			log.Fatalf("Failed to create tokens file: %v", err)
		}
		return
	}

	// TODO: Initialize and start bot components
	// This will be implemented when we migrate bot.py
	log.Info("🚧 Bot initialization is not yet implemented")
	log.Info("📋 Available commands:")
	log.Info("  --validate: Run component validation")
	log.Info("  --create-tokens: Create example tokens file")

	// Setup graceful shutdown
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Listen for interrupt signals
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Wait for shutdown signal
	select {
	case sig := <-sigChan:
		log.Infof("Received signal %v, shutting down gracefully...", sig)
		cancel()
	case <-ctx.Done():
		log.Info("Context cancelled, shutting down...")
	}

	log.Info("🛑 ClashBot shutdown complete")
}