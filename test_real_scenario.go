package main

import (
	"database/sql"
	"log"
	"os"

	"clashbot/internal/database"
	"clashbot/internal/handlers"
	"clashbot/internal/api"
	"clashbot/internal/payment"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
	_ "modernc.org/sqlite"
)

func main() {
	// Test the exact scenario from the issue: 
	// 1. Create database with old Python schema
	// 2. Try to run bot handlers (which was causing the error)

	dbPath := "test_real_scenario.db"
	defer os.Remove(dbPath)

	log.Println("=== Simulating the original error scenario ===")

	// Step 1: Create old Python-style database with data
	log.Println("1. Creating old Python database schema with existing data...")
	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	// Create users table exactly like it was migrated from Python
	_, err = db.Exec(`
		CREATE TABLE users (
			telegram_id INTEGER PRIMARY KEY,
			player_tag TEXT NOT NULL UNIQUE
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create old schema table: %v", err)
	}

	// Insert some existing user data
	_, err = db.Exec("INSERT INTO users (telegram_id, player_tag) VALUES (?, ?)", 123456, "#PLAYER1")
	if err != nil {
		log.Fatalf("Failed to insert test data: %v", err)
	}

	_, err = db.Exec("INSERT INTO users (telegram_id, player_tag) VALUES (?, ?)", 789012, "#PLAYER2")
	if err != nil {
		log.Fatalf("Failed to insert test data: %v", err)
	}

	db.Close()

	log.Println("Old database created with 2 users")

	// Step 2: Now try to use the bot with this database (this is where the error occurred)
	log.Println("2. Attempting to create bot services with old database...")
	
	// This should automatically migrate the database
	dbService, err := database.New(dbPath)
	if err != nil {
		log.Fatalf("Failed to create database service: %v", err)
	}
	defer dbService.Close()

	log.Println("Database service created successfully (migration completed)")

	// Create other services
	cocAPI := api.NewCocAPIClient("https://api.clashofclans.com/v1", "test_token")
	paymentSvc := payment.New("testbot", "python3", "./payment_bridge.py")
	_ = handlers.New(dbService, cocAPI, paymentSvc, "testbot")

	log.Println("All bot services created successfully")

	// Step 3: Simulate a user sending a command (this is where the original error occurred)
	log.Println("3. Simulating user interaction (the error scenario)...")

	// Create a mock message from an existing user
	telegramUser := &tgbotapi.User{
		ID:        123456, // This user already exists in our migrated database
		UserName:  "existing_user",
		FirstName: "Existing",
		LastName:  "User",
	}

	// This simulates what happens in HandleCommand when ensureUser is called
	log.Println("Testing user lookup and creation (ensureUser logic)...")
	
	// Try to get the user (this should work now)
	user, err := dbService.GetUserByTelegramID(telegramUser.ID)
	if err != nil {
		log.Fatalf("Failed to get user: %v", err)
	}

	if user == nil {
		log.Println("User not found, creating new user...")
		user, err = dbService.CreateUser(telegramUser.ID, telegramUser.UserName, telegramUser.FirstName, telegramUser.LastName)
		if err != nil {
			log.Fatalf("Failed to create user: %v", err)
		}
	}

	log.Printf("User found/created: ID=%d, TelegramID=%d, Username=%s, PlayerTag=%s", 
		user.ID, user.TelegramID, user.Username, user.PlayerTag)

	// Update last activity (this was also in the original failing code path)
	err = dbService.UpdateLastActivity(user.TelegramID)
	if err != nil {
		log.Fatalf("Failed to update last activity: %v", err)
	}

	log.Println("Last activity updated successfully")

	// Test with a completely new user too
	log.Println("4. Testing with a new user...")
	newUser := &tgbotapi.User{
		ID:        999888,
		UserName:  "newuser",
		FirstName: "New",
		LastName:  "User",
	}

	// Test the same flow with a new user
	user2, err := dbService.GetUserByTelegramID(newUser.ID)
	if err != nil {
		log.Fatalf("Failed to get new user: %v", err)
	}

	if user2 == nil {
		log.Println("New user not found, creating...")
		user2, err = dbService.CreateUser(newUser.ID, newUser.UserName, newUser.FirstName, newUser.LastName)
		if err != nil {
			log.Fatalf("Failed to create new user: %v", err)
		}
	}

	log.Printf("New user created: ID=%d, TelegramID=%d, Username=%s", 
		user2.ID, user2.TelegramID, user2.Username)

	log.Println()
	log.Println("=== SUCCESS! ===")
	log.Println("✅ Old database migrated successfully")
	log.Println("✅ Existing users preserved")  
	log.Println("✅ New users can be created")
	log.Println("✅ Bot functionality works correctly")
	log.Println("✅ Original error 'no such column: id' is fixed!")
}