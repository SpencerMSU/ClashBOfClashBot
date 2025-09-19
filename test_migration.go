package main

import (
	"database/sql"
	"log"
	"os"

	"clashbot/internal/database"
	_ "modernc.org/sqlite"
)

func main() {
	// Test migration from Python schema to Go schema
	dbPath := "test_migration.db"
	defer os.Remove(dbPath)

	// Create a database with old Python schema
	log.Println("Creating old Python-style database schema...")
	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}

	// Create users table without ID column and other missing columns (simulating Python version)
	_, err = db.Exec(`
		CREATE TABLE users (
			telegram_id INTEGER PRIMARY KEY,
			player_tag TEXT NOT NULL UNIQUE
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create old schema table: %v", err)
	}

	// Insert test data
	_, err = db.Exec("INSERT INTO users (telegram_id, player_tag) VALUES (123456, '#TESTPLAYER')")
	if err != nil {
		log.Fatalf("Failed to insert test data: %v", err)
	}

	_, err = db.Exec("INSERT INTO users (telegram_id, player_tag) VALUES (789012, '#ANOTHERPLAYER')")
	if err != nil {
		log.Fatalf("Failed to insert test data: %v", err)
	}

	db.Close()

	// Show schema before migration
	log.Println("\nSchema before migration:")
	showUsersSchema(dbPath)

	// Show data before migration
	log.Println("\nData before migration:")
	showUsersData(dbPath)

	// Now test our migration using the database service
	log.Println("\nTesting migration with database service...")
	service, err := database.New(dbPath)
	if err != nil {
		log.Fatalf("Failed to create database service: %v", err)
	}
	defer service.Close()

	log.Println("Migration completed successfully!")

	// Show schema after migration
	log.Println("\nSchema after migration:")
	showUsersSchema(dbPath)

	// Show data after migration
	log.Println("\nData after migration:")
	showUsersData(dbPath)

	// Test creating a user using the new service
	log.Println("\nTesting user creation with new schema...")
	user, err := service.CreateUser(999888, "testuser", "Test", "User")
	if err != nil {
		log.Fatalf("Failed to create user: %v", err)
	}
	log.Printf("Created user: ID=%d, TelegramID=%d, Username=%s", user.ID, user.TelegramID, user.Username)

	// Test getting user by telegram ID
	retrievedUser, err := service.GetUserByTelegramID(123456)
	if err != nil {
		log.Fatalf("Failed to get user: %v", err)
	}
	if retrievedUser != nil {
		log.Printf("Retrieved user: ID=%d, TelegramID=%d, PlayerTag=%s", retrievedUser.ID, retrievedUser.TelegramID, retrievedUser.PlayerTag)
	} else {
		log.Println("User not found")
	}

	log.Println("\nMigration test completed successfully!")
}

func showUsersSchema(dbPath string) {
	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		log.Printf("Failed to open database: %v", err)
		return
	}
	defer db.Close()

	rows, err := db.Query("PRAGMA table_info(users)")
	if err != nil {
		log.Printf("Failed to get table info: %v", err)
		return
	}
	defer rows.Close()

	for rows.Next() {
		var cid int
		var name, type_ string
		var notNull, pk int
		var defaultValue sql.NullString
		err = rows.Scan(&cid, &name, &type_, &notNull, &defaultValue, &pk)
		if err != nil {
			log.Printf("Error scanning schema: %v", err)
			continue
		}
		log.Printf("  %d: %s %s (notnull=%d, pk=%d, default=%s)", cid, name, type_, notNull, pk, defaultValue.String)
	}
}

func showUsersData(dbPath string) {
	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		log.Printf("Failed to open database: %v", err)
		return
	}
	defer db.Close()

	rows, err := db.Query("SELECT * FROM users")
	if err != nil {
		log.Printf("Failed to query users: %v", err)
		return
	}
	defer rows.Close()

	columns, err := rows.Columns()
	if err != nil {
		log.Printf("Failed to get columns: %v", err)
		return
	}

	log.Printf("Columns: %v", columns)

	for rows.Next() {
		values := make([]interface{}, len(columns))
		valuePtrs := make([]interface{}, len(columns))
		for i := range values {
			valuePtrs[i] = &values[i]
		}

		err = rows.Scan(valuePtrs...)
		if err != nil {
			log.Printf("Error scanning row: %v", err)
			continue
		}

		log.Printf("  Row: %v", values)
	}
}