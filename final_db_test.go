package main

import (
	"log"
	"os"
	"testing"

	"clashbot/internal/database"
)

// TestFinalDatabaseOperations проверяет финальные операции с БД
func TestFinalDatabaseOperations(t *testing.T) {
	db, err := database.New("test_final_operations.db")
	if err != nil {
		t.Fatalf("Ошибка создания БД: %v", err)
	}
	defer func() {
		db.Close()
		// Удаляем тестовый файл БД
		os.Remove("test_final_operations.db")
	}()

	// Тестируем создание пользователя
	_, err = db.CreateUser(12345, "final_test_user", "Final", "User")
	if err != nil {
		t.Fatalf("Ошибка создания пользователя: %v", err)
	}

	// Тестируем получение пользователя
	user, err := db.GetUserByTelegramID(12345)
	if err != nil {
		t.Fatalf("Ошибка получения пользователя: %v", err)
	}

	if user.Username != "final_test_user" {
		t.Errorf("Неверное имя пользователя: %s, ожидалось: final_test_user", user.Username)
	}

	log.Println("✅ Final database operations: SUCCESS")
}