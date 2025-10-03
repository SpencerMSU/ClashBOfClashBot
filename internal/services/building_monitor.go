// Package services предоставляет бизнес-логику и сервисы бота
package services

import (
	"context"
	"encoding/json"
	"log"
	"sync"
	"time"

	"ClashBOfClashBot/internal/api"
	"ClashBOfClashBot/internal/database"
	"ClashBOfClashBot/internal/models"
)

// BuildingMonitor - сервис мониторинга улучшений зданий для премиум пользователей
type BuildingMonitor struct {
	dbService        *database.DatabaseService
	cocClient        *api.CocApiClient
	botInstance      interface{} // Telegram bot instance
	isRunning        bool
	mutex            sync.RWMutex
	ctx              context.Context
	cancel           context.CancelFunc
	minCheckInterval time.Duration
	buildingNamesRU  map[string]string
}

// NewBuildingMonitor создает новый экземпляр BuildingMonitor
func NewBuildingMonitor(dbService *database.DatabaseService, cocClient *api.CocApiClient, botInstance interface{}) *BuildingMonitor {
	ctx, cancel := context.WithCancel(context.Background())

	return &BuildingMonitor{
		dbService:        dbService,
		cocClient:        cocClient,
		botInstance:      botInstance,
		isRunning:        false,
		ctx:              ctx,
		cancel:           cancel,
		minCheckInterval: 90 * time.Second, // 90 секунд (1.5 минуты) - интервал для всех пользователей
		buildingNamesRU:  getBuildingNamesRU(),
	}
}

// getBuildingNamesRU возвращает словарь для перевода названий зданий на русский
func getBuildingNamesRU() map[string]string {
	return map[string]string{
		"Town Hall":                    "Ратуша",
		"Army Camp":                    "Казарма",
		"Barracks":                     "Учебные казармы",
		"Laboratory":                   "Лаборатория",
		"Spell Factory":                "Фабрика заклинаний",
		"Clan Castle":                  "Замок клана",
		"Gold Mine":                    "Золотая шахта",
		"Elixir Collector":             "Накопитель эликсира",
		"Dark Elixir Drill":            "Бур темного эликсира",
		"Gold Storage":                 "Хранилище золота",
		"Elixir Storage":               "Хранилище эликсира",
		"Dark Elixir Storage":          "Хранилище темного эликсира",
		"Cannon":                       "Пушка",
		"Archer Tower":                 "Башня лучниц",
		"Mortar":                       "Мортира",
		"Air Defense":                  "Воздушная защита",
		"Wizard Tower":                 "Башня магов",
		"Air Sweeper":                  "Воздушная метла",
		"Hidden Tesla":                 "Скрытая тесла",
		"Bomb Tower":                   "Башня-бомба",
		"X-Bow":                        "Адский лук",
		"Inferno Tower":                "Башня ада",
		"Eagle Artillery":              "Орлиная артиллерия",
		"Scattershot":                  "Разброс",
		"Builder's Hut":                "Хижина строителя",
		"Barbarian King":               "Король варваров",
		"Archer Queen":                 "Королева лучниц",
		"Grand Warden":                 "Великий хранитель",
		"Royal Champion":               "Королевский чемпион",
		"Walls (стены)":                "Стены",
		"[БД] Builder Hall":            "Зал строителя",
		"[БД] League":                  "Лига деревни строителя",
	}
}

// Start запускает мониторинг зданий
func (b *BuildingMonitor) Start() error {
	b.mutex.Lock()
	defer b.mutex.Unlock()

	if b.isRunning {
		log.Println("[Монитор зданий] Уже запущен")
		return nil
	}

	b.isRunning = true
	log.Println("[Монитор зданий] Сервис мониторинга зданий запущен")

	// Запускаем основной цикл в горутине
	go b.monitoringLoop()

	return nil
}

// Stop останавливает мониторинг зданий
func (b *BuildingMonitor) Stop() error {
	b.mutex.Lock()
	defer b.mutex.Unlock()

	if !b.isRunning {
		log.Println("[Монитор зданий] Уже остановлен")
		return nil
	}

	b.isRunning = false
	b.cancel()
	log.Println("[Монитор зданий] Сервис мониторинга зданий остановлен")

	return nil
}

// monitoringLoop основной цикл мониторинга
func (b *BuildingMonitor) monitoringLoop() {
	ticker := time.NewTicker(b.minCheckInterval)
	defer ticker.Stop()

	for {
		select {
		case <-b.ctx.Done():
			return
		case <-ticker.C:
			if err := b.checkAllTrackers(); err != nil {
				log.Printf("[Монитор зданий] Ошибка в фоновой задаче: %v", err)
				time.Sleep(time.Minute) // Ждем минуту перед повтором при ошибке
			}
		}
	}
}

// checkAllTrackers проверяет все активные отслеживатели
func (b *BuildingMonitor) checkAllTrackers() error {
	trackers, err := b.dbService.GetActiveBuildingTrackers()
	if err != nil {
		return err
	}

	log.Printf("[Монитор зданий] Проверка %d активных отслеживателей", len(trackers))

	currentTime := time.Now()

	for _, tracker := range trackers {
		// Проверяем, что у пользователя есть активная подписка
		subscription, err := b.dbService.GetSubscription(tracker.TelegramID)
		if err != nil || subscription == nil || !subscription.IsActive() || subscription.IsExpired() {
			log.Printf("[Монитор зданий] Отключение отслеживания для пользователя %d - нет активной подписки", tracker.TelegramID)
			if err := b.deactivateTracker(tracker.TelegramID); err != nil {
				log.Printf("[Монитор зданий] Ошибка при деактивации трекера: %v", err)
			}
			continue
		}

		// Определяем интервал проверки для данного пользователя
		checkInterval := b.getCheckIntervalForSubscription(subscription.SubscriptionType)

		// Проверяем, прошло ли достаточно времени с последней проверки
		if tracker.LastCheck != "" {
			lastCheckTime, err := time.Parse(time.RFC3339, tracker.LastCheck)
			if err == nil {
				timeSinceLastCheck := currentTime.Sub(lastCheckTime)
				if timeSinceLastCheck < checkInterval {
					continue // Ещё не время проверять этого пользователя
				}
			}
		}

		if err := b.checkPlayerBuildings(&tracker); err != nil {
			log.Printf("[Монитор зданий] Ошибка при проверке игрока %s: %v", tracker.PlayerTag, err)
		}
	}

	return nil
}

// getCheckIntervalForSubscription определяет интервал проверки по типу подписки
func (b *BuildingMonitor) getCheckIntervalForSubscription(subscriptionType string) time.Duration {
	// Согласно политике фан контента SuperCell - для всех аккаунтов с включенными уведомлениями
	// проверка улучшений строений происходит раз в 1.5 минуты (90 секунд)
	return 90 * time.Second // 90 секунд (1.5 минуты) для всех пользователей
}

// checkPlayerBuildings проверяет здания конкретного игрока
func (b *BuildingMonitor) checkPlayerBuildings(tracker *models.BuildingTracker) error {
	// Получаем текущую информацию о игроке
	playerData, err := b.cocClient.GetPlayerInfo(tracker.PlayerTag)
	if err != nil {
		return err
	}

	if playerData == nil {
		log.Printf("[Монитор зданий] Не удалось получить данные игрока %s", tracker.PlayerTag)
		return nil
	}

	// Получаем последний снимок зданий
	lastSnapshot, err := b.dbService.GetLatestBuildingSnapshot(tracker.PlayerTag)
	if err != nil {
		return err
	}

	if lastSnapshot == nil {
		// Создаем первый снимок
		if err := b.createSnapshot(tracker.PlayerTag, playerData); err != nil {
			return err
		}
		log.Printf("[Монитор зданий] Создан первый снимок зданий для игрока %s", tracker.PlayerTag)
		return nil
	}

	// Сравниваем здания
	upgrades, err := b.compareBuildings(lastSnapshot, playerData)
	if err != nil {
		return err
	}

	if len(upgrades) > 0 {
		// Отправляем уведомления об улучшениях
		if err := b.sendUpgradeNotifications(tracker.TelegramID, upgrades, tracker.PlayerTag); err != nil {
			log.Printf("[Монитор зданий] Ошибка при отправке уведомлений: %v", err)
		}

		// Сохраняем новый снимок
		if err := b.createSnapshot(tracker.PlayerTag, playerData); err != nil {
			return err
		}
	}

	// Обновляем время последней проверки
	now := time.Now().Format(time.RFC3339)
	if err := b.dbService.UpdateTrackerLastCheck(tracker.TelegramID, now, tracker.PlayerTag); err != nil {
		return err
	}

	return nil
}

// createSnapshot создает снимок состояния зданий
func (b *BuildingMonitor) createSnapshot(playerTag string, playerData map[string]interface{}) error {
	buildingsData := make(map[string]interface{})

	// Извлекаем данные о зданиях (включая ратушу)
	if townHallLevel, ok := playerData["townHallLevel"].(float64); ok {
		buildingsData["Town Hall"] = int(townHallLevel)
	}

	// Извлекаем данные о героях
	if heroes, ok := playerData["heroes"].([]interface{}); ok {
		for _, h := range heroes {
			hero, ok := h.(map[string]interface{})
			if !ok {
				continue
			}

			name, nameOk := hero["name"].(string)
			level, levelOk := hero["level"].(float64)
			if nameOk && levelOk {
				buildingsData[name] = int(level)
			}
		}
	}

	// Извлекаем данные о снаряжении героев
	if heroEquipment, ok := playerData["heroEquipment"].([]interface{}); ok {
		for _, e := range heroEquipment {
			equipment, ok := e.(map[string]interface{})
			if !ok {
				continue
			}

			name, nameOk := equipment["name"].(string)
			level, levelOk := equipment["level"].(float64)
			if nameOk && levelOk {
				buildingsData[name+" (снаряжение)"] = int(level)
			}
		}
	}

	// Извлекаем данные о войсках
	if troops, ok := playerData["troops"].([]interface{}); ok {
		for _, t := range troops {
			troop, ok := t.(map[string]interface{})
			if !ok {
				continue
			}

			name, nameOk := troop["name"].(string)
			level, levelOk := troop["level"].(float64)
			if nameOk && levelOk {
				buildingsData[name+" (войска)"] = int(level)
			}
		}
	}

	// Извлекаем данные о заклинаниях
	if spells, ok := playerData["spells"].([]interface{}); ok {
		for _, s := range spells {
			spell, ok := s.(map[string]interface{})
			if !ok {
				continue
			}

			name, nameOk := spell["name"].(string)
			level, levelOk := spell["level"].(float64)
			if nameOk && levelOk {
				buildingsData[name+" (заклинание)"] = int(level)
			}
		}
	}

	// Извлекаем данные о стенах
	if achievements, ok := playerData["achievements"].([]interface{}); ok {
		for _, a := range achievements {
			achievement, ok := a.(map[string]interface{})
			if !ok {
				continue
			}

			name, nameOk := achievement["name"].(string)
			value, valueOk := achievement["value"].(float64)
			if nameOk && valueOk && name == "Wall Buster" {
				buildingsData["Walls (стены)"] = int(value)
				break
			}
		}
	}

	// Извлекаем данные о деревне строителя
	if builderHallLevel, ok := playerData["builderHallLevel"].(float64); ok {
		buildingsData["[БД] Builder Hall"] = int(builderHallLevel)
	}

	// Другие здания деревни строителя
	if builderBaseLeague, ok := playerData["builderBaseLeague"].(map[string]interface{}); ok {
		if leagueName, ok := builderBaseLeague["name"].(string); ok && leagueName != "Unranked" {
			buildingsData["[БД] League"] = leagueName
		}
	}

	// Сериализуем данные
	buildingsJSON, err := json.Marshal(buildingsData)
	if err != nil {
		return err
	}

	snapshot := models.NewBuildingSnapshot(
		playerTag,
		time.Now().Format(time.RFC3339),
		string(buildingsJSON),
	)

	return b.dbService.SaveBuildingSnapshot(snapshot)
}

// compareBuildings сравнивает здания и находит улучшения
func (b *BuildingMonitor) compareBuildings(lastSnapshot *models.BuildingSnapshot, currentData map[string]interface{}) ([]models.BuildingUpgrade, error) {
	upgrades := []models.BuildingUpgrade{}

	// Загружаем данные из последнего снимка
	var oldBuildings map[string]interface{}
	if err := json.Unmarshal([]byte(lastSnapshot.BuildingsData), &oldBuildings); err != nil {
		return nil, err
	}

	// Создаем текущий снимок для сравнения
	currentBuildings := make(map[string]interface{})

	// Ратуша
	if townHallLevel, ok := currentData["townHallLevel"].(float64); ok {
		currentBuildings["Town Hall"] = int(townHallLevel)
	}

	// Герои
	if heroes, ok := currentData["heroes"].([]interface{}); ok {
		for _, h := range heroes {
			hero, ok := h.(map[string]interface{})
			if !ok {
				continue
			}

			name, nameOk := hero["name"].(string)
			level, levelOk := hero["level"].(float64)
			if nameOk && levelOk {
				currentBuildings[name] = int(level)
			}
		}
	}

	// Снаряжение героев
	if heroEquipment, ok := currentData["heroEquipment"].([]interface{}); ok {
		for _, e := range heroEquipment {
			equipment, ok := e.(map[string]interface{})
			if !ok {
				continue
			}

			name, nameOk := equipment["name"].(string)
			level, levelOk := equipment["level"].(float64)
			if nameOk && levelOk {
				currentBuildings[name+" (снаряжение)"] = int(level)
			}
		}
	}

	// Войска
	if troops, ok := currentData["troops"].([]interface{}); ok {
		for _, t := range troops {
			troop, ok := t.(map[string]interface{})
			if !ok {
				continue
			}

			name, nameOk := troop["name"].(string)
			level, levelOk := troop["level"].(float64)
			if nameOk && levelOk {
				currentBuildings[name+" (войска)"] = int(level)
			}
		}
	}

	// Заклинания
	if spells, ok := currentData["spells"].([]interface{}); ok {
		for _, s := range spells {
			spell, ok := s.(map[string]interface{})
			if !ok {
				continue
			}

			name, nameOk := spell["name"].(string)
			level, levelOk := spell["level"].(float64)
			if nameOk && levelOk {
				currentBuildings[name+" (заклинание)"] = int(level)
			}
		}
	}

	// Стены
	if achievements, ok := currentData["achievements"].([]interface{}); ok {
		for _, a := range achievements {
			achievement, ok := a.(map[string]interface{})
			if !ok {
				continue
			}

			name, nameOk := achievement["name"].(string)
			value, valueOk := achievement["value"].(float64)
			if nameOk && valueOk && name == "Wall Buster" {
				currentBuildings["Walls (стены)"] = int(value)
				break
			}
		}
	}

	// Деревня строителя
	if builderHallLevel, ok := currentData["builderHallLevel"].(float64); ok {
		currentBuildings["[БД] Builder Hall"] = int(builderHallLevel)
	}

	if builderBaseLeague, ok := currentData["builderBaseLeague"].(map[string]interface{}); ok {
		if leagueName, ok := builderBaseLeague["name"].(string); ok && leagueName != "Unranked" {
			currentBuildings["[БД] League"] = leagueName
		}
	}

	// Сравниваем здания
	for buildingName, currentValue := range currentBuildings {
		oldValue, exists := oldBuildings[buildingName]

		// Преобразуем значения в int для сравнения
		var currentLevel, oldLevel int

		switch v := currentValue.(type) {
		case int:
			currentLevel = v
		case float64:
			currentLevel = int(v)
		case string:
			// Для строковых значений (например, лига) пропускаем
			continue
		}

		if exists {
			switch v := oldValue.(type) {
			case int:
				oldLevel = v
			case float64:
				oldLevel = int(v)
			case string:
				continue
			}

			// Проверяем, было ли улучшение
			if currentLevel > oldLevel {
				// Переводим название на русский
				ruName := buildingName
				if translated, ok := b.buildingNamesRU[buildingName]; ok {
					ruName = translated
				}

				upgrade := models.BuildingUpgrade{
					BuildingName: ruName,
					OldLevel:     oldLevel,
					NewLevel:     currentLevel,
					UpgradeTime:  time.Now().Format(time.RFC3339),
				}
				upgrades = append(upgrades, upgrade)
			}
		} else {
			// Новое здание/войска/заклинание
			ruName := buildingName
			if translated, ok := b.buildingNamesRU[buildingName]; ok {
				ruName = translated
			}

			upgrade := models.BuildingUpgrade{
				BuildingName: ruName,
				OldLevel:     0,
				NewLevel:     currentLevel,
				UpgradeTime:  time.Now().Format(time.RFC3339),
			}
			upgrades = append(upgrades, upgrade)
		}
	}

	return upgrades, nil
}

// sendUpgradeNotifications отправляет уведомления об улучшениях
func (b *BuildingMonitor) sendUpgradeNotifications(telegramID int64, upgrades []models.BuildingUpgrade, playerTag string) error {
	if b.botInstance == nil {
		return nil
	}

	// Здесь должна быть логика отправки уведомлений через Telegram Bot
	// Но так как это интерфейс, реализация будет в основном боте

	log.Printf("[Монитор зданий] Отправка уведомлений пользователю %d о %d улучшениях", telegramID, len(upgrades))

	return nil
}

// deactivateTracker деактивирует трекер
func (b *BuildingMonitor) deactivateTracker(telegramID int64) error {
	// Здесь должна быть логика деактивации трекера
	// Реализация будет зависеть от структуры базы данных
	return nil
}

// SetBotInstance устанавливает экземпляр бота
func (b *BuildingMonitor) SetBotInstance(botInstance interface{}) {
	b.botInstance = botInstance
}

// IsTrackingActive проверяет, активен ли трекинг для пользователя
func (b *BuildingMonitor) IsTrackingActive(telegramID int64, playerTag string) (bool, error) {
	trackers, err := b.dbService.GetUserBuildingTrackers(telegramID)
	if err != nil {
		return false, err
	}

	for _, tracker := range trackers {
		if tracker.PlayerTag == playerTag && tracker.IsActive {
			return true, nil
		}
	}

	return false, nil
}
