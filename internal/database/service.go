package database

import (
	"database/sql"
	"fmt"
	"time"

	"clashbot/internal/models"
	_ "modernc.org/sqlite"
)

// Service представляет сервис для работы с базой данных
type Service struct {
	db *sql.DB
}

// New создает новый экземпляр сервиса базы данных
func New(dbPath string) (*Service, error) {
	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		return nil, fmt.Errorf("ошибка открытия базы данных: %v", err)
	}

	service := &Service{db: db}
	
	// Создаем таблицы если их нет
	if err := service.createTables(); err != nil {
		return nil, fmt.Errorf("ошибка создания таблиц: %v", err)
	}

	return service, nil
}

// Close закрывает соединение с базой данных
func (s *Service) Close() error {
	return s.db.Close()
}

// createTables создает таблицы в базе данных
func (s *Service) createTables() error {
	queries := []string{
		`CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			telegram_id INTEGER UNIQUE NOT NULL,
			username TEXT,
			first_name TEXT,
			last_name TEXT,
			player_tag TEXT,
			clan_tag TEXT,
			is_active BOOLEAN DEFAULT 1,
			joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,
		
		`CREATE TABLE IF NOT EXISTS subscriptions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			telegram_id INTEGER NOT NULL,
			subscription_type TEXT NOT NULL,
			start_date DATETIME NOT NULL,
			end_date DATETIME NOT NULL,
			is_active BOOLEAN DEFAULT 1,
			payment_id TEXT,
			amount REAL,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
		)`,
		
		`CREATE TABLE IF NOT EXISTS wars (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			clan_tag TEXT NOT NULL,
			opponent_tag TEXT NOT NULL,
			opponent_name TEXT,
			team_size INTEGER,
			state TEXT,
			preparation_start DATETIME,
			start_time DATETIME,
			end_time DATETIME,
			clan_stars INTEGER DEFAULT 0,
			opponent_stars INTEGER DEFAULT 0,
			clan_destruction REAL DEFAULT 0.0,
			opponent_destruction REAL DEFAULT 0.0,
			is_notified BOOLEAN DEFAULT 0,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,
		
		`CREATE TABLE IF NOT EXISTS attacks (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			war_id INTEGER NOT NULL,
			attacker_tag TEXT NOT NULL,
			attacker_name TEXT,
			defender_tag TEXT NOT NULL,
			defender_name TEXT,
			stars INTEGER DEFAULT 0,
			destruction REAL DEFAULT 0.0,
			order_number INTEGER,
			attacker_map_position INTEGER,
			defender_map_position INTEGER,
			duration INTEGER,
			FOREIGN KEY (war_id) REFERENCES wars(id)
		)`,
		
		`CREATE TABLE IF NOT EXISTS cwl_seasons (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			clan_tag TEXT NOT NULL,
			season TEXT NOT NULL,
			league TEXT,
			state TEXT,
			total_stars INTEGER DEFAULT 0,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,
		
		`CREATE TABLE IF NOT EXISTS player_stats_snapshots (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			player_tag TEXT NOT NULL,
			player_name TEXT,
			clan_tag TEXT,
			donations_given INTEGER DEFAULT 0,
			donations_received INTEGER DEFAULT 0,
			trophies INTEGER DEFAULT 0,
			war_stars INTEGER DEFAULT 0,
			snapshot_date DATE NOT NULL,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,
		
		`CREATE TABLE IF NOT EXISTS building_trackers (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			telegram_id INTEGER NOT NULL,
			player_tag TEXT NOT NULL,
			player_name TEXT,
			is_active BOOLEAN DEFAULT 1,
			last_check DATETIME,
			notifications_sent INTEGER DEFAULT 0,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
		)`,
		
		`CREATE TABLE IF NOT EXISTS building_snapshots (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			player_tag TEXT NOT NULL,
			player_name TEXT,
			buildings TEXT NOT NULL,
			snapshot_date DATE NOT NULL,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,
		
		`CREATE TABLE IF NOT EXISTS building_upgrades (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			player_tag TEXT NOT NULL,
			player_name TEXT,
			building_name TEXT NOT NULL,
			old_level INTEGER,
			new_level INTEGER,
			village TEXT,
			upgrade_date DATE NOT NULL,
			is_notified BOOLEAN DEFAULT 0,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,
		
		`CREATE TABLE IF NOT EXISTS notifications (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			telegram_id INTEGER NOT NULL,
			message TEXT NOT NULL,
			is_sent BOOLEAN DEFAULT 0,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			sent_at DATETIME
		)`,
	}

	for _, query := range queries {
		if _, err := s.db.Exec(query); err != nil {
			return fmt.Errorf("ошибка выполнения запроса: %v", err)
		}
	}

	return nil
}

// CreateUser создает нового пользователя
func (s *Service) CreateUser(telegramID int64, username, firstName, lastName string) (*models.User, error) {
	query := `INSERT INTO users (telegram_id, username, first_name, last_name) 
			  VALUES (?, ?, ?, ?) 
			  ON CONFLICT(telegram_id) DO UPDATE SET
			  username = excluded.username,
			  first_name = excluded.first_name,
			  last_name = excluded.last_name,
			  last_activity = CURRENT_TIMESTAMP`

	_, err := s.db.Exec(query, telegramID, username, firstName, lastName)
	if err != nil {
		return nil, fmt.Errorf("ошибка создания пользователя: %v", err)
	}

	// Получаем созданного пользователя
	return s.GetUserByTelegramID(telegramID)
}

// GetUserByTelegramID получает пользователя по Telegram ID
func (s *Service) GetUserByTelegramID(telegramID int64) (*models.User, error) {
	query := `SELECT id, telegram_id, username, first_name, last_name, 
			  player_tag, clan_tag, is_active, joined_at, last_activity 
			  FROM users WHERE telegram_id = ?`

	row := s.db.QueryRow(query, telegramID)

	var user models.User
	var playerTag, clanTag sql.NullString
	err := row.Scan(
		&user.ID,
		&user.TelegramID,
		&user.Username,
		&user.FirstName,
		&user.LastName,
		&playerTag,
		&clanTag,
		&user.IsActive,
		&user.JoinedAt,
		&user.LastActivity,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil // Пользователь не найден
		}
		return nil, fmt.Errorf("ошибка получения пользователя: %v", err)
	}

	if playerTag.Valid {
		user.PlayerTag = playerTag.String
	}
	if clanTag.Valid {
		user.ClanTag = clanTag.String
	}

	return &user, nil
}

// UpdateUserPlayerTag обновляет тег игрока пользователя
func (s *Service) UpdateUserPlayerTag(telegramID int64, playerTag string) error {
	query := `UPDATE users SET player_tag = ?, last_activity = CURRENT_TIMESTAMP WHERE telegram_id = ?`
	
	_, err := s.db.Exec(query, playerTag, telegramID)
	if err != nil {
		return fmt.Errorf("ошибка обновления тега игрока: %v", err)
	}
	
	return nil
}

// CreateSubscription создает подписку
func (s *Service) CreateSubscription(subscription *models.Subscription) error {
	query := `INSERT INTO subscriptions (telegram_id, subscription_type, start_date, end_date, payment_id, amount)
			  VALUES (?, ?, ?, ?, ?, ?)`

	_, err := s.db.Exec(query,
		subscription.TelegramID,
		subscription.SubscriptionType,
		subscription.StartDate,
		subscription.EndDate,
		subscription.PaymentID,
		subscription.Amount,
	)

	if err != nil {
		return fmt.Errorf("ошибка создания подписки: %v", err)
	}

	return nil
}

// GetActiveSubscription получает активную подписку пользователя
func (s *Service) GetActiveSubscription(telegramID int64) (*models.Subscription, error) {
	query := `SELECT id, telegram_id, subscription_type, start_date, end_date, 
			  is_active, payment_id, amount, created_at 
			  FROM subscriptions 
			  WHERE telegram_id = ? AND is_active = 1 AND end_date > ? 
			  ORDER BY end_date DESC LIMIT 1`

	row := s.db.QueryRow(query, telegramID, time.Now())

	var subscription models.Subscription
	var paymentID sql.NullString
	
	err := row.Scan(
		&subscription.ID,
		&subscription.TelegramID,
		&subscription.SubscriptionType,
		&subscription.StartDate,
		&subscription.EndDate,
		&subscription.IsActive,
		&paymentID,
		&subscription.Amount,
		&subscription.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil // Активная подписка не найдена
		}
		return nil, fmt.Errorf("ошибка получения подписки: %v", err)
	}

	if paymentID.Valid {
		subscription.PaymentID = paymentID.String
	}

	return &subscription, nil
}

// CreateWar создает запись о войне
func (s *Service) CreateWar(war *models.War) (int64, error) {
	query := `INSERT INTO wars (clan_tag, opponent_tag, opponent_name, team_size, state, 
			  preparation_start, start_time, end_time, clan_stars, opponent_stars, 
			  clan_destruction, opponent_destruction) 
			  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	result, err := s.db.Exec(query,
		war.ClanTag,
		war.OpponentTag,
		war.OpponentName,
		war.TeamSize,
		war.State,
		war.PreparationStart,
		war.StartTime,
		war.EndTime,
		war.ClanStars,
		war.OpponentStars,
		war.ClanDestruction,
		war.OpponentDestruction,
	)

	if err != nil {
		return 0, fmt.Errorf("ошибка создания войны: %v", err)
	}

	return result.LastInsertId()
}

// GetWarByTags получает войну по тегам кланов
func (s *Service) GetWarByTags(clanTag, opponentTag string, startTime time.Time) (*models.War, error) {
	query := `SELECT id, clan_tag, opponent_tag, opponent_name, team_size, state,
			  preparation_start, start_time, end_time, clan_stars, opponent_stars,
			  clan_destruction, opponent_destruction, is_notified, created_at, updated_at
			  FROM wars 
			  WHERE clan_tag = ? AND opponent_tag = ? AND start_time = ?`

	row := s.db.QueryRow(query, clanTag, opponentTag, startTime)

	var war models.War
	err := row.Scan(
		&war.ID,
		&war.ClanTag,
		&war.OpponentTag,
		&war.OpponentName,
		&war.TeamSize,
		&war.State,
		&war.PreparationStart,
		&war.StartTime,
		&war.EndTime,
		&war.ClanStars,
		&war.OpponentStars,
		&war.ClanDestruction,
		&war.OpponentDestruction,
		&war.IsNotified,
		&war.CreatedAt,
		&war.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, fmt.Errorf("ошибка получения войны: %v", err)
	}

	return &war, nil
}

// UpdateLastActivity обновляет время последней активности пользователя
func (s *Service) UpdateLastActivity(telegramID int64) error {
	query := `UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE telegram_id = ?`
	
	_, err := s.db.Exec(query, telegramID)
	if err != nil {
		return fmt.Errorf("ошибка обновления активности: %v", err)
	}
	
	return nil
}