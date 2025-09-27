package database

import (
	"fmt"
	"time"

	"github.com/sirupsen/logrus"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"

	"clashbot-go/internal/models"
)

// DatabaseService provides database operations - exact copy from Python database.py
type DatabaseService struct {
	db     *gorm.DB
	dbPath string
	logger *logrus.Logger
}

// NewDatabaseService creates a new database service instance
func NewDatabaseService(dbPath string) (*DatabaseService, error) {
	if dbPath == "" {
		dbPath = "clashbot.db"
	}

	// Configure GORM logger to match our logging level
	gormLogger := logger.Default.LogMode(logger.Warn)

	db, err := gorm.Open(sqlite.Open(dbPath), &gorm.Config{
		Logger: gormLogger,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	service := &DatabaseService{
		db:     db,
		dbPath: dbPath,
		logger: logrus.StandardLogger(),
	}

	// Auto-migrate all models
	if err := service.migrate(); err != nil {
		return nil, fmt.Errorf("failed to migrate database: %w", err)
	}

	service.logger.Info("Database service initialized successfully")
	return service, nil
}

// migrate runs database migrations - equivalent to create_tables in Python
func (ds *DatabaseService) migrate() error {
	return ds.db.AutoMigrate(
		&models.User{},
		&models.UserProfile{},
		&models.Subscription{},
		&models.WarToSave{},
		&models.AttackData{},
		&models.BuildingSnapshot{},
		&models.BuildingTracker{},
		&models.BuildingUpgrade{},
		&models.LinkedClan{},
		&Notification{},
	)
}

// Close closes the database connection
func (ds *DatabaseService) Close() error {
	sqlDB, err := ds.db.DB()
	if err != nil {
		return err
	}
	return sqlDB.Close()
}

// ============================================================================
// USER OPERATIONS - exact copy from Python database.py
// ============================================================================

// SaveUser saves or updates a user - exact copy from save_user()
func (ds *DatabaseService) SaveUser(telegramID int64, username, firstName, lastName string, playerTag string, isBot bool, languageCode string) error {
	user := models.User{
		TelegramID:   telegramID,
		Username:     username,
		FirstName:    firstName,
		LastName:     lastName,
		PlayerTag:    playerTag,
		IsBot:        isBot,
		LanguageCode: languageCode,
	}

	// Use GORM's Upsert functionality
	result := ds.db.Where("telegram_id = ?", telegramID).Assign(user).FirstOrCreate(&user)
	if result.Error != nil {
		ds.logger.Errorf("Error saving user %d: %v", telegramID, result.Error)
		return result.Error
	}

	ds.logger.Debugf("User %d saved successfully", telegramID)
	return nil
}

// FindUser finds a user by telegram ID - exact copy from find_user()
func (ds *DatabaseService) FindUser(telegramID int64) (*models.User, error) {
	var user models.User
	result := ds.db.Where("telegram_id = ?", telegramID).First(&user)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, nil // User not found
		}
		ds.logger.Errorf("Error finding user %d: %v", telegramID, result.Error)
		return nil, result.Error
	}
	return &user, nil
}

// UserExists checks if a user exists - exact copy from user_exists()
func (ds *DatabaseService) UserExists(telegramID int64) (bool, error) {
	var count int64
	result := ds.db.Model(&models.User{}).Where("telegram_id = ?", telegramID).Count(&count)
	if result.Error != nil {
		ds.logger.Errorf("Error checking user existence %d: %v", telegramID, result.Error)
		return false, result.Error
	}
	return count > 0, nil
}

// UpdateUserTag updates a user's player tag - exact copy from update_user_tag()
func (ds *DatabaseService) UpdateUserTag(telegramID int64, playerTag string) error {
	result := ds.db.Model(&models.User{}).Where("telegram_id = ?", telegramID).Update("player_tag", playerTag)
	if result.Error != nil {
		ds.logger.Errorf("Error updating user tag for %d: %v", telegramID, result.Error)
		return result.Error
	}
	return nil
}

// DeleteUser deletes a user - exact copy from delete_user()
func (ds *DatabaseService) DeleteUser(telegramID int64) error {
	result := ds.db.Where("telegram_id = ?", telegramID).Delete(&models.User{})
	if result.Error != nil {
		ds.logger.Errorf("Error deleting user %d: %v", telegramID, result.Error)
		return result.Error
	}
	return nil
}

// ============================================================================
// USER PROFILES OPERATIONS - exact copy from Python database.py
// ============================================================================

// SaveUserProfile saves or updates a user profile - exact copy from save_user_profile()  
func (ds *DatabaseService) SaveUserProfile(telegramID int64, playerTag, playerName string, isPrimary bool) (*models.UserProfile, error) {
	profile := models.UserProfile{
		TelegramID: telegramID,
		PlayerTag:  playerTag,
		PlayerName: playerName,
		IsPrimary:  isPrimary,
		IsActive:   true,
	}

	// If this is set as primary, unset all other primary profiles for this user
	if isPrimary {
		if err := ds.unsetAllPrimaryProfiles(telegramID); err != nil {
			return nil, err
		}
	}

	result := ds.db.Where("telegram_id = ? AND player_tag = ?", telegramID, playerTag).Assign(profile).FirstOrCreate(&profile)
	if result.Error != nil {
		ds.logger.Errorf("Error saving user profile for %d: %v", telegramID, result.Error)
		return nil, result.Error
	}

	ds.logger.Debugf("User profile saved for %d: %s", telegramID, playerTag)
	return &profile, nil
}

// unsetAllPrimaryProfiles unsets all primary profiles for a user
func (ds *DatabaseService) unsetAllPrimaryProfiles(telegramID int64) error {
	result := ds.db.Model(&models.UserProfile{}).Where("telegram_id = ?", telegramID).Update("is_primary", false)
	return result.Error
}

// GetUserProfiles gets all profiles for a user - exact copy from get_user_profiles()
func (ds *DatabaseService) GetUserProfiles(telegramID int64) ([]models.UserProfile, error) {
	var profiles []models.UserProfile
	result := ds.db.Where("telegram_id = ? AND is_active = ?", telegramID, true).Order("is_primary DESC, created_at ASC").Find(&profiles)
	if result.Error != nil {
		ds.logger.Errorf("Error getting user profiles for %d: %v", telegramID, result.Error)
		return nil, result.Error
	}
	return profiles, nil
}

// GetPrimaryProfile gets the primary profile for a user - exact copy from get_primary_profile()
func (ds *DatabaseService) GetPrimaryProfile(telegramID int64) (*models.UserProfile, error) {
	var profile models.UserProfile
	result := ds.db.Where("telegram_id = ? AND is_primary = ? AND is_active = ?", telegramID, true, true).First(&profile)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			// Try to get any active profile
			result = ds.db.Where("telegram_id = ? AND is_active = ?", telegramID, true).First(&profile)
			if result.Error != nil {
				if result.Error == gorm.ErrRecordNotFound {
					return nil, nil
				}
				return nil, result.Error
			}
		} else {
			return nil, result.Error
		}
	}
	return &profile, nil
}

// SetPrimaryProfile sets a profile as primary - exact copy from set_primary_profile()
func (ds *DatabaseService) SetPrimaryProfile(telegramID int64, playerTag string) error {
	// First unset all primary profiles
	if err := ds.unsetAllPrimaryProfiles(telegramID); err != nil {
		return err
	}

	// Then set the specified profile as primary
	result := ds.db.Model(&models.UserProfile{}).Where("telegram_id = ? AND player_tag = ?", telegramID, playerTag).Update("is_primary", true)
	if result.Error != nil {
		ds.logger.Errorf("Error setting primary profile for %d: %v", telegramID, result.Error)
		return result.Error
	}
	return nil
}

// DeleteUserProfile deletes a user profile - exact copy from delete_user_profile()
func (ds *DatabaseService) DeleteUserProfile(telegramID int64, playerTag string) error {
	result := ds.db.Where("telegram_id = ? AND player_tag = ?", telegramID, playerTag).Delete(&models.UserProfile{})
	if result.Error != nil {
		ds.logger.Errorf("Error deleting user profile for %d: %v", telegramID, result.Error)
		return result.Error
	}
	return nil
}

// GetProfileCount gets the number of profiles for a user - exact copy from get_profile_count()
func (ds *DatabaseService) GetProfileCount(telegramID int64) (int, error) {
	var count int64
	result := ds.db.Model(&models.UserProfile{}).Where("telegram_id = ? AND is_active = ?", telegramID, true).Count(&count)
	if result.Error != nil {
		ds.logger.Errorf("Error getting profile count for %d: %v", telegramID, result.Error)
		return 0, result.Error
	}
	return int(count), nil
}

// ============================================================================
// SUBSCRIPTION OPERATIONS - exact copy from Python database.py
// ============================================================================

// SaveSubscription saves a subscription - exact copy from save_subscription()
func (ds *DatabaseService) SaveSubscription(subscription *models.Subscription) error {
	result := ds.db.Save(subscription)
	if result.Error != nil {
		ds.logger.Errorf("Error saving subscription for %d: %v", subscription.TelegramID, result.Error)
		return result.Error
	}
	return nil
}

// GetSubscription gets active subscription for a user - exact copy from get_subscription()
func (ds *DatabaseService) GetSubscription(telegramID int64) (*models.Subscription, error) {
	var subscription models.Subscription
	result := ds.db.Where("telegram_id = ? AND status = ?", telegramID, models.SubscriptionActive).Order("end_date DESC").First(&subscription)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, nil
		}
		ds.logger.Errorf("Error getting subscription for %d: %v", telegramID, result.Error)
		return nil, result.Error
	}
	
	// Check if subscription has expired
	if subscription.IsExpired() {
		subscription.Status = models.SubscriptionExpired
		ds.SaveSubscription(&subscription)
		return nil, nil
	}
	
	return &subscription, nil
}

// ExtendSubscription extends an existing subscription - exact copy from extend_subscription()
func (ds *DatabaseService) ExtendSubscription(telegramID int64, duration time.Duration, paymentID string, amount float64) error {
	subscription, err := ds.GetSubscription(telegramID)
	if err != nil {
		return err
	}

	if subscription != nil {
		// Extend existing subscription
		subscription.Extend(duration)
		subscription.PaymentID = paymentID
		subscription.PaymentAmount = amount
	} else {
		// Create new subscription
		subscription = &models.Subscription{
			TelegramID:      telegramID,
			SubscriptionType: models.Premium1Month, // Default
			Status:          models.SubscriptionActive,
			StartDate:       time.Now(),
			EndDate:         time.Now().Add(duration),
			PaymentID:       paymentID,
			PaymentAmount:   amount,
			PaymentCurrency: "RUB",
		}
	}

	return ds.SaveSubscription(subscription)
}

// DeactivateSubscription deactivates a subscription - exact copy from deactivate_subscription()
func (ds *DatabaseService) DeactivateSubscription(telegramID int64) error {
	result := ds.db.Model(&models.Subscription{}).Where("telegram_id = ?", telegramID).Update("status", models.SubscriptionCanceled)
	if result.Error != nil {
		ds.logger.Errorf("Error deactivating subscription for %d: %v", telegramID, result.Error)
		return result.Error
	}
	return nil
}

// ============================================================================
// WAR OPERATIONS - exact copy from Python database.py
// ============================================================================

// SaveWar saves a war - exact copy from save_war()
func (ds *DatabaseService) SaveWar(war *models.WarToSave) error {
	result := ds.db.Save(war)
	if result.Error != nil {
		ds.logger.Errorf("Error saving war: %v", result.Error)
		return result.Error
	}
	return nil
}

// WarExists checks if a war exists - exact copy from war_exists()
func (ds *DatabaseService) WarExists(endTime time.Time) (bool, error) {
	var count int64
	result := ds.db.Model(&models.WarToSave{}).Where("end_time = ?", endTime).Count(&count)
	if result.Error != nil {
		ds.logger.Errorf("Error checking war existence: %v", result.Error)
		return false, result.Error
	}
	return count > 0, nil
}

// GetRecentWars gets recent wars - exact copy from get_recent_wars()
func (ds *DatabaseService) GetRecentWars(limit int, isCWLOnly bool) ([]models.WarToSave, error) {
	var wars []models.WarToSave
	query := ds.db.Order("end_time DESC").Limit(limit)
	
	if isCWLOnly {
		query = query.Where("is_cwl_war = ?", true)
	}
	
	result := query.Find(&wars)
	if result.Error != nil {
		ds.logger.Errorf("Error getting recent wars: %v", result.Error)
		return nil, result.Error
	}
	return wars, nil
}

// GetWarByEndTime gets a war by end time - exact copy from get_war_by_end_time()
func (ds *DatabaseService) GetWarByEndTime(endTime time.Time) (*models.WarToSave, error) {
	var war models.WarToSave
	result := ds.db.Where("end_time = ?", endTime).First(&war)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, nil
		}
		ds.logger.Errorf("Error getting war by end time: %v", result.Error)
		return nil, result.Error
	}
	return &war, nil
}

// SaveAttack saves an attack - exact copy from save_attack()
func (ds *DatabaseService) SaveAttack(attack *models.AttackData) error {
	result := ds.db.Save(attack)
	if result.Error != nil {
		ds.logger.Errorf("Error saving attack: %v", result.Error)
		return result.Error
	}
	return nil
}

// GetWarAttacks gets attacks for a war - exact copy from get_war_attacks()
func (ds *DatabaseService) GetWarAttacks(warEndTime time.Time) ([]models.AttackData, error) {
	var attacks []models.AttackData
	result := ds.db.Where("war_end_time = ?", warEndTime).Order("attack_order ASC").Find(&attacks)
	if result.Error != nil {
		ds.logger.Errorf("Error getting war attacks: %v", result.Error)
		return nil, result.Error
	}
	return attacks, nil
}

// CalculateWarViolations calculates war violations - exact copy from calculate_war_violations()
func (ds *DatabaseService) CalculateWarViolations(warEndTime time.Time) (int, error) {
	var count int64
	// Count attacks where defender position is lower than attacker position (violation)
	result := ds.db.Model(&models.AttackData{}).
		Where("war_end_time = ? AND defender_map_position < attacker_map_position", warEndTime).
		Count(&count)
	if result.Error != nil {
		ds.logger.Errorf("Error calculating war violations: %v", result.Error)
		return 0, result.Error
	}
	return int(count), nil
}

// ============================================================================
// BUILDING TRACKER OPERATIONS - exact copy from Python database.py  
// ============================================================================

// SaveBuildingTracker saves a building tracker - exact copy from save_building_tracker()
func (ds *DatabaseService) SaveBuildingTracker(tracker *models.BuildingTracker) error {
	result := ds.db.Save(tracker)
	if result.Error != nil {
		ds.logger.Errorf("Error saving building tracker: %v", result.Error)
		return result.Error
	}
	return nil
}

// GetBuildingTracker gets a building tracker - exact copy from get_building_tracker()
func (ds *DatabaseService) GetBuildingTracker(telegramID int64, playerTag string) (*models.BuildingTracker, error) {
	var tracker models.BuildingTracker
	result := ds.db.Where("telegram_id = ? AND player_tag = ?", telegramID, playerTag).First(&tracker)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, nil
		}
		ds.logger.Errorf("Error getting building tracker: %v", result.Error)
		return nil, result.Error
	}
	return &tracker, nil
}

// GetActiveBuildingTrackers gets all active building trackers - exact copy from get_active_building_trackers()
func (ds *DatabaseService) GetActiveBuildingTrackers() ([]models.BuildingTracker, error) {
	var trackers []models.BuildingTracker
	result := ds.db.Where("is_active = ?", true).Find(&trackers)
	if result.Error != nil {
		ds.logger.Errorf("Error getting active building trackers: %v", result.Error)
		return nil, result.Error
	}
	return trackers, nil
}

// ToggleBuildingTracker toggles building tracker status - exact copy from toggle_building_tracker()
func (ds *DatabaseService) ToggleBuildingTracker(telegramID int64, playerTag string) (bool, error) {
	tracker, err := ds.GetBuildingTracker(telegramID, playerTag)
	if err != nil {
		return false, err
	}

	if tracker == nil {
		// Create new tracker
		tracker = &models.BuildingTracker{
			TelegramID:      telegramID,
			PlayerTag:       playerTag,
			IsActive:        true,
			NotifyUpgrades:  true,
			NotifyFinish:    true,
		}
		if err := ds.SaveBuildingTracker(tracker); err != nil {
			return false, err
		}
		return true, nil
	} else {
		// Toggle existing tracker
		tracker.IsActive = !tracker.IsActive
		if err := ds.SaveBuildingTracker(tracker); err != nil {
			return false, err
		}
		return tracker.IsActive, nil
	}
}

// IsTrackingActive checks if tracking is active for a player - exact copy from is_tracking_active()
func (ds *DatabaseService) IsTrackingActive(telegramID int64, playerTag string) (bool, error) {
	tracker, err := ds.GetBuildingTracker(telegramID, playerTag)
	if err != nil {
		return false, err
	}
	return tracker != nil && tracker.IsActive, nil
}

// SaveBuildingSnapshot saves a building snapshot - exact copy from save_building_snapshot()
func (ds *DatabaseService) SaveBuildingSnapshot(snapshot *models.BuildingSnapshot) error {
	result := ds.db.Save(snapshot)
	if result.Error != nil {
		ds.logger.Errorf("Error saving building snapshot: %v", result.Error)
		return result.Error
	}
	return nil
}

// GetLatestBuildingSnapshot gets the latest building snapshot - exact copy from get_latest_building_snapshot()
func (ds *DatabaseService) GetLatestBuildingSnapshot(telegramID int64, playerTag string) (*models.BuildingSnapshot, error) {
	var snapshot models.BuildingSnapshot
	result := ds.db.Where("telegram_id = ? AND player_tag = ?", telegramID, playerTag).
		Order("snapshot_time DESC").First(&snapshot)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, nil
		}
		ds.logger.Errorf("Error getting latest building snapshot: %v", result.Error)
		return nil, result.Error
	}
	return &snapshot, nil
}

// SaveBuildingUpgrade saves a building upgrade - exact copy from save_building_upgrade()
func (ds *DatabaseService) SaveBuildingUpgrade(upgrade *models.BuildingUpgrade) error {
	result := ds.db.Save(upgrade)
	if result.Error != nil {
		ds.logger.Errorf("Error saving building upgrade: %v", result.Error)
		return result.Error
	}
	return nil
}

// ============================================================================
// LINKED CLANS OPERATIONS - exact copy from Python database.py
// ============================================================================

// SaveLinkedClan saves a linked clan - exact copy from save_linked_clan()
func (ds *DatabaseService) SaveLinkedClan(linkedClan *models.LinkedClan) error {
	result := ds.db.Save(linkedClan)
	if result.Error != nil {
		ds.logger.Errorf("Error saving linked clan: %v", result.Error)
		return result.Error
	}
	return nil
}

// GetLinkedClans gets linked clans for a user - exact copy from get_linked_clans()
func (ds *DatabaseService) GetLinkedClans(telegramID int64) ([]models.LinkedClan, error) {
	var clans []models.LinkedClan
	result := ds.db.Where("telegram_id = ? AND is_active = ?", telegramID, true).
		Order("is_primary DESC, linked_at ASC").Find(&clans)
	if result.Error != nil {
		ds.logger.Errorf("Error getting linked clans: %v", result.Error)
		return nil, result.Error
	}
	return clans, nil
}

// RemoveLinkedClan removes a linked clan - exact copy from remove_linked_clan()
func (ds *DatabaseService) RemoveLinkedClan(telegramID int64, clanTag string) error {
	result := ds.db.Where("telegram_id = ? AND clan_tag = ?", telegramID, clanTag).Delete(&models.LinkedClan{})
	if result.Error != nil {
		ds.logger.Errorf("Error removing linked clan: %v", result.Error)
		return result.Error
	}
	return nil
}

// ============================================================================
// NOTIFICATION OPERATIONS - exact copy from Python database.py
// ============================================================================

// Notification represents a notification setting
type Notification struct {
	TelegramID int64 `gorm:"primaryKey"`
	IsEnabled  bool  `gorm:"not null;default:true"`
	CreatedAt  time.Time
	UpdatedAt  time.Time
}

func (Notification) TableName() string {
	return "notifications"
}

// IsNotificationsEnabled checks if notifications are enabled - exact copy from is_notifications_enabled()
func (ds *DatabaseService) IsNotificationsEnabled(telegramID int64) (bool, error) {
	var notification Notification
	result := ds.db.Where("telegram_id = ?", telegramID).First(&notification)
	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return true, nil // Default to enabled
		}
		ds.logger.Errorf("Error checking notifications: %v", result.Error)
		return false, result.Error
	}
	return notification.IsEnabled, nil
}

// EnableNotifications enables notifications - exact copy from enable_notifications()
func (ds *DatabaseService) EnableNotifications(telegramID int64) error {
	notification := Notification{
		TelegramID: telegramID,
		IsEnabled:  true,
	}
	result := ds.db.Where("telegram_id = ?", telegramID).Assign(notification).FirstOrCreate(&notification)
	if result.Error != nil {
		ds.logger.Errorf("Error enabling notifications: %v", result.Error)
		return result.Error
	}
	return nil
}

// DisableNotifications disables notifications - exact copy from disable_notifications()
func (ds *DatabaseService) DisableNotifications(telegramID int64) error {
	result := ds.db.Model(&Notification{}).Where("telegram_id = ?", telegramID).Update("is_enabled", false)
	if result.Error != nil {
		ds.logger.Errorf("Error disabling notifications: %v", result.Error)
		return result.Error
	}
	return nil
}

// ToggleNotifications toggles notifications - exact copy from toggle_notifications()
func (ds *DatabaseService) ToggleNotifications(telegramID int64) (bool, error) {
	enabled, err := ds.IsNotificationsEnabled(telegramID)
	if err != nil {
		return false, err
	}

	if enabled {
		err = ds.DisableNotifications(telegramID)
		return false, err
	} else {
		err = ds.EnableNotifications(telegramID)
		return true, err
	}
}

// GetNotificationUsers gets users with notifications enabled - exact copy from get_notification_users()
func (ds *DatabaseService) GetNotificationUsers() ([]int64, error) {
	var notifications []Notification
	result := ds.db.Where("is_enabled = ?", true).Find(&notifications)
	if result.Error != nil {
		ds.logger.Errorf("Error getting notification users: %v", result.Error)
		return nil, result.Error
	}

	var userIDs []int64
	for _, notification := range notifications {
		userIDs = append(userIDs, notification.TelegramID)
	}
	return userIDs, nil
}