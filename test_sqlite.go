package main

import (
"log"
"clashbot/internal/database"
)

func main() {
log.Println("Testing SQLite with CGO_ENABLED=0")
_, err := database.New("test.db")
if err != nil {
log.Fatalf("Error: %v", err)
}
}
