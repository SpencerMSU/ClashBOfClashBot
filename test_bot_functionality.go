package main

import (
	"log"
	"os"

	"clashbot/internal/database"
	"clashbot/internal/handlers"
	"clashbot/internal/api"
	"clashbot/internal/payment"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

func main() {
	// Test the full bot functionality with migrated database
	dbPath := "test_bot_functionality.db"
	defer os.Remove(dbPath)

	// Create a database service (will trigger migration if needed)
	log.Println("Creating database service...")
	db, err := database.New(dbPath)
	if err != nil {
		log.Fatalf("Failed to create database service: %v", err)
	}
	defer db.Close()

	// Create mock API and payment services
	cocAPI := api.NewCocAPIClient("https://api.clashofclans.com/v1", "test_token")
	paymentSvc := payment.New("testbot", "python3", "./payment_bridge.py")

	// Create handlers (to verify they can be created with migrated database)
	_ = handlers.New(db, cocAPI, paymentSvc, "testbot")

	// Create a mock Telegram user and update
	telegramUser := &tgbotapi.User{
		ID:        123456789,
		UserName:  "testuser",
		FirstName: "Test",
		LastName:  "User",
	}

	// Test ensureUser functionality (this was where the error occurred)
	log.Println("Testing user creation functionality...")
	// Test the database functionality directly since ensureUser is private
	user, err := db.CreateUser(telegramUser.ID, telegramUser.UserName, telegramUser.FirstName, telegramUser.LastName)
	if err != nil {
		log.Fatalf("Failed to create user: %v", err)
	}

	log.Printf("User created successfully: ID=%d, TelegramID=%d, Username=%s", 
		user.ID, user.TelegramID, user.Username)

	// Test retrieving the user
	retrievedUser, err := db.GetUserByTelegramID(telegramUser.ID)
	if err != nil {
		log.Fatalf("Failed to retrieve user: %v", err)
	}

	if retrievedUser == nil {
		log.Fatal("User not found after creation")
	}

	log.Printf("User retrieved successfully: ID=%d, TelegramID=%d, Username=%s", 
		retrievedUser.ID, retrievedUser.TelegramID, retrievedUser.Username)

	// Test updating user activity
	err = db.UpdateLastActivity(telegramUser.ID)
	if err != nil {
		log.Fatalf("Failed to update last activity: %v", err)
	}

	log.Println("User activity updated successfully")
	log.Println("All bot functionality tests passed!")
}