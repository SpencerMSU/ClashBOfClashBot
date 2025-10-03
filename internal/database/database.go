package database

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"time"

	_ "github.com/mattn/go-sqlite3"

	"ClashBOfClashBot/internal/models"
)

// DatabaseService предоставляет все операции с базой данных SQLite
type DatabaseService struct {
	db     *sql.DB
	dbPath string
}

// NewDatabaseService создает новый экземпляр DatabaseService
func NewDatabaseService(dbPath string) (*DatabaseService, error) {
	if dbPath == "" {
		dbPath = "clash_bot.db"
	}

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, fmt.Errorf("не удалось открыть базу данных: %w", err)
	}

	// Настройка connection pool
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(5 * time.Minute)

	service := &DatabaseService{
		db:     db,
		dbPath: dbPath,
	}

	return service, nil
}

// InitDB инициализирует все таблицы базы данных
func (s *DatabaseService) InitDB() error {
	// Создание таблицы пользователей
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			telegram_id INTEGER PRIMARY KEY,
			player_tag TEXT NOT NULL UNIQUE
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу users: %w", err)
	}

	// Создание таблицы профилей для премиум пользователей
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS user_profiles (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			telegram_id INTEGER NOT NULL,
			player_tag TEXT NOT NULL,
			profile_name TEXT,
			is_primary INTEGER NOT NULL DEFAULT 0,
			created_at TEXT NOT NULL,
			UNIQUE(telegram_id, player_tag)
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу user_profiles: %w", err)
	}

	// Создание индекса для профилей
	if _, err := s.db.Exec(`
		CREATE INDEX IF NOT EXISTS idx_user_profiles_telegram_id 
		ON user_profiles(telegram_id)
	`); err != nil {
		return fmt.Errorf("не удалось создать индекс idx_user_profiles_telegram_id: %w", err)
	}

	// Создание таблицы войн
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS wars (
			end_time TEXT PRIMARY KEY,
			opponent_name TEXT NOT NULL,
			team_size INTEGER NOT NULL,
			clan_stars INTEGER NOT NULL,
			opponent_stars INTEGER NOT NULL,
			clan_destruction REAL NOT NULL,
			opponent_destruction REAL NOT NULL,
			clan_attacks_used INTEGER NOT NULL,
			result TEXT NOT NULL,
			is_cwl_war INTEGER NOT NULL DEFAULT 0,
			total_violations INTEGER DEFAULT 0
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу wars: %w", err)
	}

	// Создание таблицы атак
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS attacks (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			war_id TEXT NOT NULL,
			attacker_tag TEXT,
			attacker_name TEXT NOT NULL,
			defender_tag TEXT,
			stars INTEGER NOT NULL,
			destruction REAL NOT NULL,
			attack_order INTEGER,
			attack_timestamp INTEGER,
			is_rule_violation INTEGER,
			FOREIGN KEY (war_id) REFERENCES wars(end_time)
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу attacks: %w", err)
	}

	// Создание таблицы сезонов ЛВК
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS cwl_seasons (
			season_date TEXT PRIMARY KEY,
			participants_json TEXT,
			bonus_results_json TEXT
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу cwl_seasons: %w", err)
	}

	// Создание таблицы снимков статистики игроков
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS player_stats_snapshots (
			snapshot_time TEXT NOT NULL,
			player_tag TEXT NOT NULL,
			donations INTEGER NOT NULL,
			PRIMARY KEY (snapshot_time, player_tag)
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу player_stats_snapshots: %w", err)
	}

	// Создание таблицы уведомлений
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS notifications (
			telegram_id INTEGER PRIMARY KEY
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу notifications: %w", err)
	}

	// Создание таблицы подписок
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS subscriptions (
			telegram_id INTEGER PRIMARY KEY,
			subscription_type TEXT NOT NULL,
			start_date TEXT NOT NULL,
			end_date TEXT NOT NULL,
			is_active INTEGER NOT NULL DEFAULT 1,
			payment_id TEXT,
			amount REAL,
			currency TEXT DEFAULT 'RUB',
			created_at TEXT NOT NULL,
			updated_at TEXT NOT NULL
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу subscriptions: %w", err)
	}

	// Создание таблицы отслеживания зданий
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS building_trackers (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			telegram_id INTEGER NOT NULL,
			player_tag TEXT NOT NULL,
			is_active INTEGER NOT NULL DEFAULT 0,
			created_at TEXT NOT NULL,
			last_check TEXT,
			UNIQUE(telegram_id, player_tag)
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу building_trackers: %w", err)
	}

	// Создание таблицы снимков зданий
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS building_snapshots (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			player_tag TEXT NOT NULL,
			snapshot_time TEXT NOT NULL,
			buildings_data TEXT NOT NULL,
			UNIQUE(player_tag, snapshot_time)
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу building_snapshots: %w", err)
	}

	// Создание таблицы привязанных кланов
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS linked_clans (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			telegram_id INTEGER NOT NULL,
			clan_tag TEXT NOT NULL,
			clan_name TEXT NOT NULL,
			slot_number INTEGER NOT NULL,
			created_at TEXT NOT NULL,
			UNIQUE(telegram_id, slot_number)
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу linked_clans: %w", err)
	}

	// Создание индекса для привязанных кланов
	if _, err := s.db.Exec(`
		CREATE INDEX IF NOT EXISTS idx_linked_clans_telegram_id 
		ON linked_clans(telegram_id)
	`); err != nil {
		return fmt.Errorf("не удалось создать индекс idx_linked_clans_telegram_id: %w", err)
	}

	// Создание таблицы запросов на сканирование войн
	if _, err := s.db.Exec(`
		CREATE TABLE IF NOT EXISTS war_scan_requests (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			telegram_id INTEGER NOT NULL,
			clan_tag TEXT NOT NULL,
			request_date TEXT NOT NULL,
			status TEXT NOT NULL,
			wars_added INTEGER DEFAULT 0,
			created_at TEXT NOT NULL,
			UNIQUE(telegram_id, clan_tag, request_date)
		)
	`); err != nil {
		return fmt.Errorf("не удалось создать таблицу war_scan_requests: %w", err)
	}

	// Создание индекса для запросов на сканирование
	if _, err := s.db.Exec(`
		CREATE INDEX IF NOT EXISTS idx_war_scan_requests_telegram_id_date 
		ON war_scan_requests(telegram_id, request_date)
	`); err != nil {
		return fmt.Errorf("не удалось создать индекс idx_war_scan_requests_telegram_id_date: %w", err)
	}

	log.Println("База данных успешно инициализирована")

	// Предоставление вечной PRO PLUS подписки для указанного пользователя
	if err := s.GrantPermanentProPlusSubscription(5545099444); err != nil {
		log.Printf("Предупреждение: не удалось предоставить вечную подписку: %v", err)
	}

	return nil
}

// GrantPermanentProPlusSubscription предоставляет вечную PRO PLUS подписку
func (s *DatabaseService) GrantPermanentProPlusSubscription(telegramID int64) error {
	// Создаем подписку, которая истекает через 100 лет (фактически вечная)
	startDate := time.Now()
	endDate := startDate.AddDate(100, 0, 0) // 100 лет

	subscription := models.NewSubscription(
		telegramID,
		"proplus_permanent",
		startDate,
		endDate,
		true,
		"PERMANENT_GRANT",
		0.0,
		"RUB",
	)

	if err := s.SaveSubscription(subscription); err != nil {
		return fmt.Errorf("не удалось сохранить вечную подписку: %w", err)
	}

	log.Printf("Предоставлена вечная PRO PLUS подписка для пользователя %d", telegramID)
	return nil
}

// Close закрывает соединение с базой данных
func (s *DatabaseService) Close() error {
	return s.db.Close()
}

// ==================== МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ====================

// FindUser ищет пользователя по Telegram ID
func (s *DatabaseService) FindUser(telegramID int64) (*models.User, error) {
	var user models.User
	err := s.db.QueryRow(
		"SELECT telegram_id, player_tag FROM users WHERE telegram_id = ?",
		telegramID,
	).Scan(&user.TelegramID, &user.PlayerTag)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("ошибка при поиске пользователя: %w", err)
	}

	return &user, nil
}

// SaveUser сохраняет пользователя
func (s *DatabaseService) SaveUser(user *models.User) error {
	_, err := s.db.Exec(
		"INSERT OR REPLACE INTO users (telegram_id, player_tag) VALUES (?, ?)",
		user.TelegramID, user.PlayerTag,
	)
	if err != nil {
		return fmt.Errorf("ошибка при сохранении пользователя: %w", err)
	}
	return nil
}

// DeleteUser удаляет пользователя
func (s *DatabaseService) DeleteUser(telegramID int64) error {
	_, err := s.db.Exec("DELETE FROM users WHERE telegram_id = ?", telegramID)
	if err != nil {
		return fmt.Errorf("ошибка при удалении пользователя: %w", err)
	}
	return nil
}

// ==================== МЕТОДЫ ДЛЯ РАБОТЫ С ПРОФИЛЯМИ ====================

// SaveUserProfile сохраняет профиль пользователя
func (s *DatabaseService) SaveUserProfile(profile *models.UserProfile) error {
	isPrimary := 0
	if profile.IsPrimary {
		isPrimary = 1
	}

	_, err := s.db.Exec(`
		INSERT OR REPLACE INTO user_profiles 
		(telegram_id, player_tag, profile_name, is_primary, created_at)
		VALUES (?, ?, ?, ?, ?)
	`, profile.TelegramID, profile.PlayerTag, profile.ProfileName, isPrimary, profile.CreatedAt.Format(time.RFC3339))

	if err != nil {
		return fmt.Errorf("ошибка при сохранении профиля: %w", err)
	}
	return nil
}

// GetUserProfiles получает все профили пользователя
func (s *DatabaseService) GetUserProfiles(telegramID int64) ([]*models.UserProfile, error) {
	rows, err := s.db.Query(`
		SELECT id, telegram_id, player_tag, profile_name, is_primary, created_at
		FROM user_profiles WHERE telegram_id = ? ORDER BY is_primary DESC, created_at ASC
	`, telegramID)
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении профилей: %w", err)
	}
	defer rows.Close()

	var profiles []*models.UserProfile
	for rows.Next() {
		var profile models.UserProfile
		var isPrimary int
		var createdAt string

		if err := rows.Scan(&profile.ProfileID, &profile.TelegramID, &profile.PlayerTag,
			&profile.ProfileName, &isPrimary, &createdAt); err != nil {
			return nil, fmt.Errorf("ошибка при чтении профиля: %w", err)
		}

		profile.IsPrimary = isPrimary == 1
		profile.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
		profiles = append(profiles, &profile)
	}

	return profiles, nil
}

// DeleteUserProfile удаляет профиль пользователя
func (s *DatabaseService) DeleteUserProfile(telegramID int64, playerTag string) error {
	_, err := s.db.Exec(
		"DELETE FROM user_profiles WHERE telegram_id = ? AND player_tag = ?",
		telegramID, playerTag,
	)
	if err != nil {
		return fmt.Errorf("ошибка при удалении профиля: %w", err)
	}
	return nil
}

// GetUserProfileCount получает количество профилей пользователя
func (s *DatabaseService) GetUserProfileCount(telegramID int64) (int, error) {
	var count int
	err := s.db.QueryRow(
		"SELECT COUNT(*) FROM user_profiles WHERE telegram_id = ?",
		telegramID,
	).Scan(&count)

	if err != nil {
		return 0, fmt.Errorf("ошибка при подсчете профилей: %w", err)
	}
	return count, nil
}

// SetPrimaryProfile устанавливает основной профиль
func (s *DatabaseService) SetPrimaryProfile(telegramID int64, playerTag string) error {
	tx, err := s.db.Begin()
	if err != nil {
		return fmt.Errorf("не удалось начать транзакцию: %w", err)
	}
	defer tx.Rollback()

	// Сбрасываем is_primary для всех профилей пользователя
	if _, err := tx.Exec(
		"UPDATE user_profiles SET is_primary = 0 WHERE telegram_id = ?",
		telegramID,
	); err != nil {
		return fmt.Errorf("ошибка при сбросе primary флага: %w", err)
	}

	// Устанавливаем is_primary для выбранного профиля
	if _, err := tx.Exec(
		"UPDATE user_profiles SET is_primary = 1 WHERE telegram_id = ? AND player_tag = ?",
		telegramID, playerTag,
	); err != nil {
		return fmt.Errorf("ошибка при установке primary флага: %w", err)
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("не удалось завершить транзакцию: %w", err)
	}

	return nil
}

// GetPrimaryProfile получает основной профиль пользователя
func (s *DatabaseService) GetPrimaryProfile(telegramID int64) (*models.UserProfile, error) {
	var profile models.UserProfile
	var isPrimary int
	var createdAt string

	err := s.db.QueryRow(`
		SELECT id, telegram_id, player_tag, profile_name, is_primary, created_at
		FROM user_profiles WHERE telegram_id = ? AND is_primary = 1
	`, telegramID).Scan(&profile.ProfileID, &profile.TelegramID, &profile.PlayerTag,
		&profile.ProfileName, &isPrimary, &createdAt)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении основного профиля: %w", err)
	}

	profile.IsPrimary = isPrimary == 1
	profile.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)

	return &profile, nil
}

// ==================== МЕТОДЫ ДЛЯ РАБОТЫ С ВОЙНАМИ ====================

// SaveWar сохраняет войну
func (s *DatabaseService) SaveWar(war *models.WarToSave) error {
	tx, err := s.db.Begin()
	if err != nil {
		return fmt.Errorf("не удалось начать транзакцию: %w", err)
	}
	defer tx.Rollback()

	isCWLWar := 0
	if war.IsCWLWar {
		isCWLWar = 1
	}

	// Сохраняем войну
	_, err = tx.Exec(`
		INSERT OR REPLACE INTO wars 
		(end_time, opponent_name, team_size, clan_stars, opponent_stars, 
		 clan_destruction, opponent_destruction, clan_attacks_used, result, 
		 is_cwl_war, total_violations)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	`, war.EndTime, war.OpponentName, war.TeamSize, war.ClanStars, war.OpponentStars,
		war.ClanDestruction, war.OpponentDestruction, war.ClanAttacksUsed, war.Result,
		isCWLWar, war.TotalViolations)

	if err != nil {
		return fmt.Errorf("ошибка при сохранении войны: %w", err)
	}

	// Сохраняем атаки
	for _, attack := range war.Attacks {
		isViolation := 0
		if attack.IsRuleViolation != 0 {
			isViolation = 1
		}

		_, err = tx.Exec(`
			INSERT INTO attacks 
			(war_id, attacker_tag, attacker_name, defender_tag, stars, destruction, 
			 attack_order, attack_timestamp, is_rule_violation)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
		`, war.EndTime, attack.AttackerTag, attack.AttackerName, attack.DefenderTag,
			attack.Stars, attack.Destruction, attack.AttackOrder, attack.AttackTimestamp,
			isViolation)

		if err != nil {
			return fmt.Errorf("ошибка при сохранении атаки: %w", err)
		}
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("не удалось завершить транзакцию: %w", err)
	}

	return nil
}

// WarExists проверяет существование войны
func (s *DatabaseService) WarExists(endTime string) (bool, error) {
	var count int
	err := s.db.QueryRow("SELECT COUNT(*) FROM wars WHERE end_time = ?", endTime).Scan(&count)
	if err != nil {
		return false, fmt.Errorf("ошибка при проверке существования войны: %w", err)
	}
	return count > 0, nil
}

// GetSubscribedUsers получает список пользователей с включенными уведомлениями
func (s *DatabaseService) GetSubscribedUsers() ([]int64, error) {
	rows, err := s.db.Query("SELECT telegram_id FROM notifications")
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении пользователей с уведомлениями: %w", err)
	}
	defer rows.Close()

	var userIDs []int64
	for rows.Next() {
		var id int64
		if err := rows.Scan(&id); err != nil {
			return nil, fmt.Errorf("ошибка при чтении ID пользователя: %w", err)
		}
		userIDs = append(userIDs, id)
	}

	return userIDs, nil
}

// ToggleNotifications переключает уведомления для пользователя
func (s *DatabaseService) ToggleNotifications(telegramID int64) (bool, error) {
	// Проверяем, включены ли уведомления
	enabled, err := s.IsNotificationsEnabled(telegramID)
	if err != nil {
		return false, err
	}

	if enabled {
		// Выключаем уведомления
		if err := s.DisableNotifications(telegramID); err != nil {
			return false, err
		}
		return false, nil
	} else {
		// Включаем уведомления
		if err := s.EnableNotifications(telegramID); err != nil {
			return false, err
		}
		return true, nil
	}
}

// SaveDonationSnapshot сохраняет снапшот донатов
func (s *DatabaseService) SaveDonationSnapshot(members []map[string]interface{}, snapshotTime string) error {
	if snapshotTime == "" {
		snapshotTime = time.Now().Format(time.RFC3339)
	}

	tx, err := s.db.Begin()
	if err != nil {
		return fmt.Errorf("не удалось начать транзакцию: %w", err)
	}
	defer tx.Rollback()

	for _, member := range members {
		playerTag, _ := member["tag"].(string)
		donations, _ := member["donations"].(int)

		_, err = tx.Exec(`
			INSERT OR REPLACE INTO player_stats_snapshots 
			(snapshot_time, player_tag, donations)
			VALUES (?, ?, ?)
		`, snapshotTime, playerTag, donations)

		if err != nil {
			return fmt.Errorf("ошибка при сохранении снапшота донатов: %w", err)
		}
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("не удалось завершить транзакцию: %w", err)
	}

	return nil
}

// GetWarList получает список войн с пагинацией
func (s *DatabaseService) GetWarList(limit, offset int) ([]map[string]interface{}, error) {
	rows, err := s.db.Query(`
		SELECT end_time, opponent_name, team_size, clan_stars, opponent_stars, 
		       clan_destruction, opponent_destruction, result, is_cwl_war, total_violations
		FROM wars ORDER BY end_time DESC LIMIT ? OFFSET ?
	`, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении списка войн: %w", err)
	}
	defer rows.Close()

	var wars []map[string]interface{}
	for rows.Next() {
		var endTime, opponentName, result string
		var teamSize, clanStars, opponentStars, isCWLWar, totalViolations int
		var clanDestruction, opponentDestruction float64

		if err := rows.Scan(&endTime, &opponentName, &teamSize, &clanStars, &opponentStars,
			&clanDestruction, &opponentDestruction, &result, &isCWLWar, &totalViolations); err != nil {
			return nil, fmt.Errorf("ошибка при чтении войны: %w", err)
		}

		war := map[string]interface{}{
			"end_time":             endTime,
			"opponent_name":        opponentName,
			"team_size":            teamSize,
			"clan_stars":           clanStars,
			"opponent_stars":       opponentStars,
			"clan_destruction":     clanDestruction,
			"opponent_destruction": opponentDestruction,
			"result":               result,
			"is_cwl_war":           isCWLWar == 1,
			"total_violations":     totalViolations,
		}
		wars = append(wars, war)
	}

	return wars, nil
}

// GetCWLBonusData получает данные о бонусах CWL
func (s *DatabaseService) GetCWLBonusData(yearMonth string) ([]map[string]interface{}, error) {
	var bonusResultsJSON string
	err := s.db.QueryRow(
		"SELECT bonus_results_json FROM cwl_seasons WHERE season_date = ?",
		yearMonth,
	).Scan(&bonusResultsJSON)

	if err == sql.ErrNoRows {
		return []map[string]interface{}{}, nil
	}
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении данных CWL бонусов: %w", err)
	}

	var bonusResults []map[string]interface{}
	if err := json.Unmarshal([]byte(bonusResultsJSON), &bonusResults); err != nil {
		return nil, fmt.Errorf("ошибка при разборе JSON бонусов: %w", err)
	}

	return bonusResults, nil
}

// GetCWLSeasonDonationStats получает статистику донатов за сезон CWL
func (s *DatabaseService) GetCWLSeasonDonationStats(seasonStart, seasonEnd string) (map[string]int, error) {
	// Получаем снапшоты на начало и конец сезона
	startRows, err := s.db.Query(`
		SELECT player_tag, donations FROM player_stats_snapshots 
		WHERE snapshot_time >= ? AND snapshot_time < ? ORDER BY snapshot_time ASC
	`, seasonStart, seasonStart+" 23:59:59")
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении начального снапшота: %w", err)
	}
	defer startRows.Close()

	startDonations := make(map[string]int)
	for startRows.Next() {
		var playerTag string
		var donations int
		if err := startRows.Scan(&playerTag, &donations); err != nil {
			continue
		}
		if _, exists := startDonations[playerTag]; !exists {
			startDonations[playerTag] = donations
		}
	}

	endRows, err := s.db.Query(`
		SELECT player_tag, donations FROM player_stats_snapshots 
		WHERE snapshot_time >= ? ORDER BY snapshot_time DESC
	`, seasonEnd)
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении конечного снапшота: %w", err)
	}
	defer endRows.Close()

	endDonations := make(map[string]int)
	for endRows.Next() {
		var playerTag string
		var donations int
		if err := endRows.Scan(&playerTag, &donations); err != nil {
			continue
		}
		if _, exists := endDonations[playerTag]; !exists {
			endDonations[playerTag] = donations
		}
	}

	// Вычисляем разницу
	result := make(map[string]int)
	for playerTag, endDonation := range endDonations {
		startDonation := startDonations[playerTag]
		diff := endDonation - startDonation
		if diff > 0 {
			result[playerTag] = diff
		}
	}

	return result, nil
}

// GetCWLSeasonAttackStats получает статистику атак за сезон CWL
func (s *DatabaseService) GetCWLSeasonAttackStats(seasonStart, seasonEnd string) (map[string]map[string]interface{}, error) {
	rows, err := s.db.Query(`
		SELECT a.attacker_tag, a.attacker_name, a.stars, a.destruction
		FROM attacks a
		INNER JOIN wars w ON a.war_id = w.end_time
		WHERE w.is_cwl_war = 1 AND w.end_time >= ? AND w.end_time <= ?
	`, seasonStart, seasonEnd)
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении статистики атак CWL: %w", err)
	}
	defer rows.Close()

	stats := make(map[string]map[string]interface{})
	for rows.Next() {
		var attackerTag, attackerName string
		var stars int
		var destruction float64

		if err := rows.Scan(&attackerTag, &attackerName, &stars, &destruction); err != nil {
			continue
		}

		if _, exists := stats[attackerTag]; !exists {
			stats[attackerTag] = map[string]interface{}{
				"name":              attackerName,
				"total_attacks":     0,
				"total_stars":       0,
				"total_destruction": 0.0,
				"three_stars":       0,
				"two_stars":         0,
			}
		}

		stat := stats[attackerTag]
		stat["total_attacks"] = stat["total_attacks"].(int) + 1
		stat["total_stars"] = stat["total_stars"].(int) + stars
		stat["total_destruction"] = stat["total_destruction"].(float64) + destruction

		if stars == 3 {
			stat["three_stars"] = stat["three_stars"].(int) + 1
		} else if stars == 2 {
			stat["two_stars"] = stat["two_stars"].(int) + 1
		}
	}

	return stats, nil
}

// GetWarDetails получает детальную информацию о войне
func (s *DatabaseService) GetWarDetails(endTime string) (map[string]interface{}, error) {
	var opponentName, result string
	var teamSize, clanStars, opponentStars, clanAttacksUsed, isCWLWar, totalViolations int
	var clanDestruction, opponentDestruction float64

	err := s.db.QueryRow(`
		SELECT opponent_name, team_size, clan_stars, opponent_stars, 
		       clan_destruction, opponent_destruction, clan_attacks_used, result, 
		       is_cwl_war, total_violations
		FROM wars WHERE end_time = ?
	`, endTime).Scan(&opponentName, &teamSize, &clanStars, &opponentStars,
		&clanDestruction, &opponentDestruction, &clanAttacksUsed, &result,
		&isCWLWar, &totalViolations)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении деталей войны: %w", err)
	}

	// Получаем атаки
	attacksRows, err := s.db.Query(`
		SELECT attacker_tag, attacker_name, defender_tag, stars, destruction, 
		       attack_order, attack_timestamp, is_rule_violation
		FROM attacks WHERE war_id = ? ORDER BY attack_order
	`, endTime)
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении атак: %w", err)
	}
	defer attacksRows.Close()

	var attacks []map[string]interface{}
	for attacksRows.Next() {
		var attackerTag, attackerName, defenderTag string
		var stars, attackOrder, attackTimestamp, isViolation int
		var destruction float64

		if err := attacksRows.Scan(&attackerTag, &attackerName, &defenderTag, &stars,
			&destruction, &attackOrder, &attackTimestamp, &isViolation); err != nil {
			continue
		}

		attack := map[string]interface{}{
			"attacker_tag":      attackerTag,
			"attacker_name":     attackerName,
			"defender_tag":      defenderTag,
			"stars":             stars,
			"destruction":       destruction,
			"attack_order":      attackOrder,
			"attack_timestamp":  attackTimestamp,
			"is_rule_violation": isViolation == 1,
		}
		attacks = append(attacks, attack)
	}

	war := map[string]interface{}{
		"end_time":             endTime,
		"opponent_name":        opponentName,
		"team_size":            teamSize,
		"clan_stars":           clanStars,
		"opponent_stars":       opponentStars,
		"clan_destruction":     clanDestruction,
		"opponent_destruction": opponentDestruction,
		"clan_attacks_used":    clanAttacksUsed,
		"result":               result,
		"is_cwl_war":           isCWLWar == 1,
		"total_violations":     totalViolations,
		"attacks":              attacks,
	}

	return war, nil
}

// ==================== МЕТОДЫ ДЛЯ РАБОТЫ С ПОДПИСКАМИ ====================

// SaveSubscription сохраняет подписку
func (s *DatabaseService) SaveSubscription(subscription *models.Subscription) error {
	isActive := 0
	if subscription.IsActive {
		isActive = 1
	}

	_, err := s.db.Exec(`
		INSERT OR REPLACE INTO subscriptions 
		(telegram_id, subscription_type, start_date, end_date, is_active, 
		 payment_id, amount, currency, created_at, updated_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	`, subscription.TelegramID, subscription.SubscriptionType,
		subscription.StartDate.Format(time.RFC3339), subscription.EndDate.Format(time.RFC3339),
		isActive, subscription.PaymentID, subscription.Amount, subscription.Currency,
		subscription.CreatedAt.Format(time.RFC3339), subscription.UpdatedAt.Format(time.RFC3339))

	if err != nil {
		return fmt.Errorf("ошибка при сохранении подписки: %w", err)
	}
	return nil
}

// GetSubscription получает подписку пользователя
func (s *DatabaseService) GetSubscription(telegramID int64) (*models.Subscription, error) {
	var subscription models.Subscription
	var isActive int
	var startDate, endDate, createdAt, updatedAt string

	err := s.db.QueryRow(`
		SELECT telegram_id, subscription_type, start_date, end_date, is_active, 
		       payment_id, amount, currency, created_at, updated_at
		FROM subscriptions WHERE telegram_id = ?
	`, telegramID).Scan(&subscription.TelegramID, &subscription.SubscriptionType,
		&startDate, &endDate, &isActive, &subscription.PaymentID,
		&subscription.Amount, &subscription.Currency, &createdAt, &updatedAt)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении подписки: %w", err)
	}

	subscription.IsActive = isActive == 1
	subscription.StartDate, _ = time.Parse(time.RFC3339, startDate)
	subscription.EndDate, _ = time.Parse(time.RFC3339, endDate)
	subscription.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
	subscription.UpdatedAt, _ = time.Parse(time.RFC3339, updatedAt)

	return &subscription, nil
}

// ExtendSubscription продлевает подписку
func (s *DatabaseService) ExtendSubscription(telegramID int64, additionalDays int) error {
	subscription, err := s.GetSubscription(telegramID)
	if err != nil {
		return err
	}
	if subscription == nil {
		return fmt.Errorf("подписка не найдена")
	}

	// Продляем существующую подписку
	subscription.EndDate = subscription.EndDate.AddDate(0, 0, additionalDays)
	subscription.IsActive = true
	subscription.UpdatedAt = time.Now()

	return s.SaveSubscription(subscription)
}

// DeactivateSubscription деактивирует подписку
func (s *DatabaseService) DeactivateSubscription(telegramID int64) error {
	_, err := s.db.Exec(
		"UPDATE subscriptions SET is_active = 0, updated_at = ? WHERE telegram_id = ?",
		time.Now().Format(time.RFC3339), telegramID,
	)
	if err != nil {
		return fmt.Errorf("ошибка при деактивации подписки: %w", err)
	}
	return nil
}

// GetExpiredSubscriptions получает список истекших подписок
func (s *DatabaseService) GetExpiredSubscriptions() ([]*models.Subscription, error) {
	rows, err := s.db.Query(`
		SELECT telegram_id, subscription_type, start_date, end_date, is_active, 
		       payment_id, amount, currency, created_at, updated_at
		FROM subscriptions WHERE is_active = 1 AND end_date < ?
	`, time.Now().Format(time.RFC3339))
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении истекших подписок: %w", err)
	}
	defer rows.Close()

	var subscriptions []*models.Subscription
	for rows.Next() {
		var subscription models.Subscription
		var isActive int
		var startDate, endDate, createdAt, updatedAt string

		if err := rows.Scan(&subscription.TelegramID, &subscription.SubscriptionType,
			&startDate, &endDate, &isActive, &subscription.PaymentID,
			&subscription.Amount, &subscription.Currency, &createdAt, &updatedAt); err != nil {
			continue
		}

		subscription.IsActive = isActive == 1
		subscription.StartDate, _ = time.Parse(time.RFC3339, startDate)
		subscription.EndDate, _ = time.Parse(time.RFC3339, endDate)
		subscription.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
		subscription.UpdatedAt, _ = time.Parse(time.RFC3339, updatedAt)

		subscriptions = append(subscriptions, &subscription)
	}

	return subscriptions, nil
}

// ==================== МЕТОДЫ ДЛЯ РАБОТЫ С УВЕДОМЛЕНИЯМИ ====================

// IsNotificationsEnabled проверяет, включены ли уведомления для пользователя
func (s *DatabaseService) IsNotificationsEnabled(telegramID int64) (bool, error) {
	var count int
	err := s.db.QueryRow(
		"SELECT COUNT(*) FROM notifications WHERE telegram_id = ?",
		telegramID,
	).Scan(&count)

	if err != nil {
		return false, fmt.Errorf("ошибка при проверке уведомлений: %w", err)
	}
	return count > 0, nil
}

// EnableNotifications включает уведомления для пользователя
func (s *DatabaseService) EnableNotifications(telegramID int64) error {
	_, err := s.db.Exec(
		"INSERT OR IGNORE INTO notifications (telegram_id) VALUES (?)",
		telegramID,
	)
	if err != nil {
		return fmt.Errorf("ошибка при включении уведомлений: %w", err)
	}
	return nil
}

// DisableNotifications выключает уведомления для пользователя
func (s *DatabaseService) DisableNotifications(telegramID int64) error {
	_, err := s.db.Exec(
		"DELETE FROM notifications WHERE telegram_id = ?",
		telegramID,
	)
	if err != nil {
		return fmt.Errorf("ошибка при выключении уведомлений: %w", err)
	}
	return nil
}

// GetNotificationUsers получает список пользователей с включенными уведомлениями
func (s *DatabaseService) GetNotificationUsers() ([]int64, error) {
	return s.GetSubscribedUsers()
}

// ==================== МЕТОДЫ ДЛЯ РАБОТЫ С ТРЕКЕРАМИ ЗДАНИЙ ====================

// SaveBuildingTracker сохраняет трекер зданий
func (s *DatabaseService) SaveBuildingTracker(tracker *models.BuildingTracker) error {
	isActive := 0
	if tracker.IsActive {
		isActive = 1
	}

	lastCheck := ""
	lastCheck = tracker.LastCheck.Format(time.RFC3339)
	_, err := s.db.Exec(`
		INSERT OR REPLACE INTO building_trackers 
		(telegram_id, player_tag, is_active, created_at, last_check)
		VALUES (?, ?, ?, ?, ?)
	`, tracker.TelegramID, tracker.PlayerTag, isActive,
		tracker.CreatedAt.Format(time.RFC3339), lastCheck)

	if err != nil {
		return fmt.Errorf("ошибка при сохранении трекера зданий: %w", err)
	}
	return nil
}

// GetBuildingTracker получает трекер зданий
func (s *DatabaseService) GetBuildingTracker(telegramID int64) (*models.BuildingTracker, error) {
	return s.GetBuildingTrackerForProfile(telegramID, "")
}

// GetUserBuildingTrackers получает все трекеры зданий пользователя
func (s *DatabaseService) GetUserBuildingTrackers(telegramID int64) ([]*models.BuildingTracker, error) {
	rows, err := s.db.Query(`
		SELECT id, telegram_id, player_tag, is_active, created_at, last_check
		FROM building_trackers WHERE telegram_id = ?
	`, telegramID)
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении трекеров зданий: %w", err)
	}
	defer rows.Close()

	var trackers []*models.BuildingTracker
	for rows.Next() {
		var tracker models.BuildingTracker
		var isActive int
		var createdAt, lastCheck string

		if err := rows.Scan(&tracker.TrackerID, &tracker.TelegramID, &tracker.PlayerTag,
			&isActive, &createdAt, &lastCheck); err != nil {
			continue
		}

		tracker.IsActive = isActive == 1
		tracker.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
		if lastCheck != "" {
			t, _ := time.Parse(time.RFC3339, lastCheck)
			tracker.LastCheck = t
		}

		trackers = append(trackers, &tracker)
	}

	return trackers, nil
}

// GetBuildingTrackerForProfile получает трекер зданий для конкретного профиля
func (s *DatabaseService) GetBuildingTrackerForProfile(telegramID int64, playerTag string) (*models.BuildingTracker, error) {
	query := "SELECT id, telegram_id, player_tag, is_active, created_at, last_check FROM building_trackers WHERE telegram_id = ?"
	args := []interface{}{telegramID}

	if playerTag != "" {
		query += " AND player_tag = ?"
		args = append(args, playerTag)
	}

	var tracker models.BuildingTracker
	var isActive int
	var createdAt, lastCheck string

	err := s.db.QueryRow(query, args...).Scan(&tracker.TrackerID, &tracker.TelegramID,
		&tracker.PlayerTag, &isActive, &createdAt, &lastCheck)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении трекера зданий: %w", err)
	}

	tracker.IsActive = isActive == 1
	tracker.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
	if lastCheck != "" {
		t, _ := time.Parse(time.RFC3339, lastCheck)
		tracker.LastCheck = t
	}

	return &tracker, nil
}

// ToggleBuildingTrackerForProfile переключает трекер зданий для профиля
func (s *DatabaseService) ToggleBuildingTrackerForProfile(telegramID int64, playerTag string) (bool, error) {
	tracker, err := s.GetBuildingTrackerForProfile(telegramID, playerTag)
	if err != nil {
		return false, err
	}

	if tracker == nil {
		// Создаем новый трекер
		newTracker := models.NewBuildingTracker(telegramID, playerTag)
		if err := s.SaveBuildingTracker(newTracker); err != nil {
			return false, err
		}
		return true, nil
	}

	// Переключаем состояние
	tracker.IsActive = !tracker.IsActive
	if err := s.SaveBuildingTracker(tracker); err != nil {
		return false, err
	}

	return tracker.IsActive, nil
}

// GetActiveBuildingTrackers получает все активные трекеры зданий
func (s *DatabaseService) GetActiveBuildingTrackers() ([]*models.BuildingTracker, error) {
	rows, err := s.db.Query(`
		SELECT id, telegram_id, player_tag, is_active, created_at, last_check
		FROM building_trackers WHERE is_active = 1
	`)
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении активных трекеров: %w", err)
	}
	defer rows.Close()

	var trackers []*models.BuildingTracker
	for rows.Next() {
		var tracker models.BuildingTracker
		var isActive int
		var createdAt, lastCheck string

		if err := rows.Scan(&tracker.TrackerID, &tracker.TelegramID, &tracker.PlayerTag,
			&isActive, &createdAt, &lastCheck); err != nil {
			continue
		}

		tracker.IsActive = isActive == 1
		tracker.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
		if lastCheck != "" {
			t, _ := time.Parse(time.RFC3339, lastCheck)
			tracker.LastCheck = t
		}

		trackers = append(trackers, &tracker)
	}

	return trackers, nil
}

// SaveBuildingSnapshot сохраняет снапшот зданий
func (s *DatabaseService) SaveBuildingSnapshot(snapshot *models.BuildingSnapshot) error {
	buildingsJSON, err := json.Marshal(snapshot.BuildingsData)
	if err != nil {
		return fmt.Errorf("ошибка при сериализации данных зданий: %w", err)
	}

	_, err = s.db.Exec(`
		INSERT OR REPLACE INTO building_snapshots 
		(player_tag, snapshot_time, buildings_data)
		VALUES (?, ?, ?)
	`, snapshot.PlayerTag, snapshot.SnapshotTime.Format(time.RFC3339), string(buildingsJSON))

	if err != nil {
		return fmt.Errorf("ошибка при сохранении снапшота зданий: %w", err)
	}
	return nil
}

// GetLatestBuildingSnapshot получает последний снапшот зданий
func (s *DatabaseService) GetLatestBuildingSnapshot(playerTag string) (*models.BuildingSnapshot, error) {
	var snapshot models.BuildingSnapshot
	var snapshotTime, buildingsJSON string

	err := s.db.QueryRow(`
		SELECT id, player_tag, snapshot_time, buildings_data
		FROM building_snapshots WHERE player_tag = ? 
		ORDER BY snapshot_time DESC LIMIT 1
	`, playerTag).Scan(&snapshot.SnapshotID, &snapshot.PlayerTag, &snapshotTime, &buildingsJSON)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении снапшота зданий: %w", err)
	}

	snapshot.SnapshotTime, _ = time.Parse(time.RFC3339, snapshotTime)
	if err := json.Unmarshal([]byte(buildingsJSON), &snapshot.BuildingsData); err != nil {
		return nil, fmt.Errorf("ошибка при разборе данных зданий: %w", err)
	}

	return &snapshot, nil
}

// UpdateTrackerLastCheck обновляет время последней проверки трекера
func (s *DatabaseService) UpdateTrackerLastCheck(telegramID int64, lastCheck string, playerTag string) error {
	query := "UPDATE building_trackers SET last_check = ? WHERE telegram_id = ?"
	args := []interface{}{lastCheck, telegramID}

	if playerTag != "" {
		query += " AND player_tag = ?"
		args = append(args, playerTag)
	}

	_, err := s.db.Exec(query, args...)
	if err != nil {
		return fmt.Errorf("ошибка при обновлении времени проверки: %w", err)
	}
	return nil
}

// ==================== МЕТОДЫ ДЛЯ РАБОТЫ С ПРИВЯЗАННЫМИ КЛАНАМИ ====================

// GetLinkedClans получает все привязанные кланы пользователя
func (s *DatabaseService) GetLinkedClans(telegramID int64) ([]*models.LinkedClan, error) {
	rows, err := s.db.Query(`
		SELECT id, telegram_id, clan_tag, clan_name, slot_number, created_at
		FROM linked_clans WHERE telegram_id = ? ORDER BY slot_number
	`, telegramID)
	if err != nil {
		return nil, fmt.Errorf("ошибка при получении привязанных кланов: %w", err)
	}
	defer rows.Close()

	var clans []*models.LinkedClan
	for rows.Next() {
		var clan models.LinkedClan
		var createdAt string

		if err := rows.Scan(&clan.ID, &clan.TelegramID, &clan.ClanTag,
			&clan.ClanName, &clan.SlotNumber, &createdAt); err != nil {
			continue
		}

		clan.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
		clans = append(clans, &clan)
	}

	return clans, nil
}

// SaveLinkedClan сохраняет привязанный клан
func (s *DatabaseService) SaveLinkedClan(clan *models.LinkedClan) error {
	_, err := s.db.Exec(`
		INSERT OR REPLACE INTO linked_clans 
		(telegram_id, clan_tag, clan_name, slot_number, created_at)
		VALUES (?, ?, ?, ?, ?)
	`, clan.TelegramID, clan.ClanTag, clan.ClanName, clan.SlotNumber,
		clan.CreatedAt.Format(time.RFC3339))

	if err != nil {
		return fmt.Errorf("ошибка при сохранении привязанного клана: %w", err)
	}
	return nil
}

// DeleteLinkedClan удаляет привязанный клан
func (s *DatabaseService) DeleteLinkedClan(telegramID int64, slotNumber int) error {
	_, err := s.db.Exec(
		"DELETE FROM linked_clans WHERE telegram_id = ? AND slot_number = ?",
		telegramID, slotNumber,
	)
	if err != nil {
		return fmt.Errorf("ошибка при удалении привязанного клана: %w", err)
	}
	return nil
}

// GetMaxLinkedClansForUser получает максимальное количество привязанных кланов для пользователя
func (s *DatabaseService) GetMaxLinkedClansForUser(telegramID int64) (int, error) {
	// Проверяем подписку пользователя
	subscription, err := s.GetSubscription(telegramID)
	if err != nil {
		return 1, err // По умолчанию 1 клан
	}

	if subscription == nil || subscription.IsExpired() {
		return 1, nil // Бесплатные пользователи - 1 клан
	}

	if subscription.IsPremium() {
		return 3, nil // Premium - 3 клана
	}

	if subscription.IsProPlus() {
		return 5, nil // PRO PLUS - 5 кланов
	}

	return 1, nil
}

// ==================== МЕТОДЫ ДЛЯ РАБОТЫ СО СКАНИРОВАНИЕМ ВОЙН ====================

// CanRequestWarScan проверяет, может ли пользователь запросить сканирование войн
func (s *DatabaseService) CanRequestWarScan(telegramID int64) (bool, error) {
	// Проверяем количество запросов за сегодня
	count, err := s.GetWarScanRequestsToday(telegramID)
	if err != nil {
		return false, err
	}

	// Проверяем подписку
	subscription, err := s.GetSubscription(telegramID)
	if err != nil {
		return false, err
	}

	// Лимиты в зависимости от подписки
	if subscription == nil || subscription.IsExpired() {
		return count < 1, nil // Бесплатно - 1 запрос в день
	}

	if subscription.IsPremium() {
		return count < 3, nil // Premium - 3 запроса в день
	}

	if subscription.IsProPlus() {
		return count < 10, nil // PRO PLUS - 10 запросов в день
	}

	return count < 1, nil
}

// SaveWarScanRequest сохраняет запрос на сканирование войн
func (s *DatabaseService) SaveWarScanRequest(telegramID int64, clanTag, status string, warsAdded int) error {
	requestDate := time.Now().Format("2006-01-02")
	createdAt := time.Now().Format(time.RFC3339)

	_, err := s.db.Exec(`
		INSERT OR REPLACE INTO war_scan_requests 
		(telegram_id, clan_tag, request_date, status, wars_added, created_at)
		VALUES (?, ?, ?, ?, ?, ?)
	`, telegramID, clanTag, requestDate, status, warsAdded, createdAt)

	if err != nil {
		return fmt.Errorf("ошибка при сохранении запроса на сканирование: %w", err)
	}
	return nil
}

// GetWarScanRequestsToday получает количество запросов на сканирование за сегодня
func (s *DatabaseService) GetWarScanRequestsToday(telegramID int64) (int, error) {
	requestDate := time.Now().Format("2006-01-02")

	var count int
	err := s.db.QueryRow(`
		SELECT COUNT(*) FROM war_scan_requests 
		WHERE telegram_id = ? AND request_date = ?
	`, telegramID, requestDate).Scan(&count)

	if err != nil {
		return 0, fmt.Errorf("ошибка при подсчете запросов на сканирование: %w", err)
	}
	return count, nil
}
