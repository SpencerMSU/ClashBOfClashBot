package main

import (
	"database/sql"
	"log"
	"os"

	_ "modernc.org/sqlite"
)

func main() {
	// Create a test database file with the old Python schema
	dbPath := "test_old_schema.db"
	defer os.Remove(dbPath)

	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// Create users table without ID column (simulating Python version schema)
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

	// Try to select with ID column (this should fail)
	row := db.QueryRow("SELECT id, telegram_id, username, first_name, last_name, player_tag, clan_tag, is_active, joined_at, last_activity FROM users WHERE telegram_id = ?", 123456)

	var id int64
	var telegramID int64
	var username, firstName, lastName, playerTag, clanTag string
	var isActive bool
	var joinedAt, lastActivity string

	err = row.Scan(&id, &telegramID, &username, &firstName, &lastName, &playerTag, &clanTag, &isActive, &joinedAt, &lastActivity)
	if err != nil {
		log.Printf("Error: %v", err)
		log.Println("This reproduces the 'no such column: id' error")
	}

	// Show current schema
	rows, err := db.Query("PRAGMA table_info(users)")
	if err != nil {
		log.Fatalf("Failed to get table info: %v", err)
	}
	defer rows.Close()

	log.Println("Current users table schema:")
	for rows.Next() {
		var cid int
		var name, type_, defaultValue string
		var notNull, pk int
		err = rows.Scan(&cid, &name, &type_, &notNull, &defaultValue, &pk)
		if err != nil {
			log.Printf("Error scanning schema: %v", err)
			continue
		}
		log.Printf("  %d: %s %s (notnull=%d, pk=%d)", cid, name, type_, notNull, pk)
	}
}