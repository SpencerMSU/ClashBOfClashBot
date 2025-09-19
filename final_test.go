package main
import ("log"; "clashbot/internal/database")
func main() {
    db, err := database.New("test_final.db")
    if err != nil { log.Fatal(err) }
    defer db.Close()
    _, err = db.CreateUser(999, "final_test", "Final", "Test")
    if err != nil { log.Fatal(err) }
    log.Println("Database operations with CGO disabled: SUCCESS")
}
