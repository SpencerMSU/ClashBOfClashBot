// Package services предоставляет бизнес-логику и сервисы бота
package services

import (
	"context"
	"log"
	"sync"
	"time"

	"ClashBOfClashBot/internal/api"
	"ClashBOfClashBot/internal/database"
	"ClashBOfClashBot/internal/models"
)

// WarArchiver - сервис архивации войн и уведомлений
type WarArchiver struct {
	clanTag                 string
	dbService               *database.DatabaseService
	cocClient               *api.CocApiClient
	botInstance             interface{} // Telegram bot instance
	isRunning               bool
	mutex                   sync.RWMutex
	ctx                     context.Context
	cancel                  context.CancelFunc
	notifiedWarStartTime    string
	lastKnownWarEndTime     string
	checkInterval           time.Duration
	donationSnapshotInterval time.Duration
	lastDonationSnapshot    *time.Time
}

// NewWarArchiver создает новый экземпляр WarArchiver
func NewWarArchiver(clanTag string, dbService *database.DatabaseService, cocClient *api.CocApiClient, botInstance interface{}) *WarArchiver {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &WarArchiver{
		clanTag:                 clanTag,
		dbService:               dbService,
		cocClient:               cocClient,
		botInstance:             botInstance,
		isRunning:               false,
		ctx:                     ctx,
		cancel:                  cancel,
		checkInterval:           15 * time.Minute,  // 15 минут
		donationSnapshotInterval: 6 * time.Hour,    // 6 часов
	}
}

// Start запускает сервис архивации
func (w *WarArchiver) Start() error {
	w.mutex.Lock()
	defer w.mutex.Unlock()

	if w.isRunning {
		log.Println("[Архиватор] Уже запущен")
		return nil
	}

	w.isRunning = true
	log.Printf("[Архиватор] Сервис архивации войн запущен для клана %s", w.clanTag)

	// Запускаем основной цикл в горутине
	go w.archiveLoop()

	return nil
}

// Stop останавливает сервис архивации
func (w *WarArchiver) Stop() error {
	w.mutex.Lock()
	defer w.mutex.Unlock()

	if !w.isRunning {
		log.Println("[Архиватор] Уже остановлен")
		return nil
	}

	w.isRunning = false
	w.cancel()
	log.Println("[Архиватор] Сервис архивации войн остановлен")

	return nil
}

// archiveLoop основной цикл архивации
func (w *WarArchiver) archiveLoop() {
	// При первом запуске проверяем журнал войн
	if err := w.checkWarLogForPastWars(); err != nil {
		log.Printf("[Архиватор] Ошибка при проверке журнала войн: %v", err)
	}

	ticker := time.NewTicker(w.checkInterval)
	defer ticker.Stop()

	for {
		select {
		case <-w.ctx.Done():
			return
		case <-ticker.C:
			// Проверяем текущую войну
			if err := w.checkCurrentWar(); err != nil {
				log.Printf("[Архиватор] Ошибка при проверке текущей войны: %v", err)
			}

			// Проверяем снимки донатов
			if err := w.checkDonationSnapshots(); err != nil {
				log.Printf("[Архиватор] Ошибка при проверке снимков донатов: %v", err)
			}
		}
	}
}

// checkWarLogForPastWars проверяет журнал войн на наличие непроцессированных войн
func (w *WarArchiver) checkWarLogForPastWars() error {
	log.Printf("[Архиватор] Проверка журнала войн для клана %s", w.clanTag)

	warLog, err := w.cocClient.GetClanWarLog(w.clanTag)
	if err != nil {
		return err
	}

	items, ok := warLog["items"].([]interface{})
	if !ok {
		log.Printf("[Архиватор] Журнал войн недоступен для клана %s", w.clanTag)
		return nil
	}

	log.Printf("[Архиватор] Найдено %d войн в журнале", len(items))

	processedCount := 0
	for _, item := range items {
		warEntry, ok := item.(map[string]interface{})
		if !ok {
			continue
		}

		// Проверяем, что война завершена
		result, ok := warEntry["result"].(string)
		if !ok || (result != "win" && result != "lose" && result != "tie") {
			continue
		}

		endTime, ok := warEntry["endTime"].(string)
		if !ok || endTime == "" {
			continue
		}

		// Проверяем, не сохранена ли уже эта война
		exists, err := w.dbService.WarExists(endTime)
		if err != nil {
			log.Printf("[Архиватор] Ошибка при проверке существования войны: %v", err)
			continue
		}
		if exists {
			continue
		}

		// Извлекаем данные о клане и противнике
		clanData, ok := warEntry["clan"].(map[string]interface{})
		if !ok {
			continue
		}

		opponentData, ok := warEntry["opponent"].(map[string]interface{})
		if !ok {
			continue
		}

		// Собираем информацию о войне
		opponentName := "Неизвестный противник"
		if name, ok := opponentData["name"].(string); ok {
			opponentName = name
		}

		teamSize := 0
		if size, ok := warEntry["teamSize"].(float64); ok {
			teamSize = int(size)
		} else if members, ok := clanData["members"].([]interface{}); ok {
			teamSize = len(members)
		}

		clanStars := int(getFloatValue(clanData, "stars"))
		opponentStars := int(getFloatValue(opponentData, "stars"))
		clanDestruction := getFloatValue(clanData, "destructionPercentage")
		opponentDestruction := getFloatValue(opponentData, "destructionPercentage")

		// Анализируем атаки
		clanAttacksUsed, totalViolations, _ := w.analyzeAttacks(clanData)

		// Создаем объект войны для сохранения
		warToSave := models.NewWarToSave(
			endTime,
			opponentName,
			teamSize,
			clanStars,
			opponentStars,
			clanDestruction,
			opponentDestruction,
			clanAttacksUsed,
			result,
			false, // is_cwl_war - в журнале обычно ЛВК войны не отображаются
			totalViolations,
		)

		// Сохраняем в базу данных
		if err := w.dbService.SaveWar(warToSave); err != nil {
			log.Printf("[Архиватор] Ошибка при сохранении войны: %v", err)
			continue
		}

		processedCount++
		log.Printf("[Архиватор] Война против %s (завершена %s) добавлена из журнала", opponentName, endTime)
	}

	if processedCount > 0 {
		log.Printf("[Архиватор] Обработано %d войн из журнала", processedCount)
	} else {
		log.Println("[Архиватор] Все войны из журнала уже обработаны")
	}

	return nil
}

// checkCurrentWar проверяет текущую войну
func (w *WarArchiver) checkCurrentWar() error {
	log.Printf("[Архиватор] Проверка текущей войны для клана %s", w.clanTag)

	currentWar, err := w.cocClient.GetClanCurrentWar(w.clanTag)
	if err != nil {
		log.Printf("[Архиватор] Ошибка при получении текущей войны: %v", err)
		return err
	}

	if currentWar == nil {
		log.Printf("[Архиватор] Не удалось получить информацию о текущей войне для %s", w.clanTag)
		return nil
	}

	warState, ok := currentWar["state"].(string)
	if !ok {
		return nil
	}

	// Проверяем на уведомления о начале войны
	if warState == "preparation" {
		if err := w.checkWarStartNotification(currentWar); err != nil {
			log.Printf("[Архиватор] Ошибка при проверке уведомления о начале войны: %v", err)
		}
	}

	// Проверяем завершенные войны
	if warState == "warEnded" {
		if err := w.checkCompletedWar(currentWar); err != nil {
			log.Printf("[Архиватор] Ошибка при проверке завершенной войны: %v", err)
		}
	}

	return nil
}

// checkWarStartNotification проверяет и отправляет уведомления о начале войны
func (w *WarArchiver) checkWarStartNotification(warData map[string]interface{}) error {
	startTimeStr, ok := warData["startTime"].(string)
	if !ok || startTimeStr == "" {
		return nil
	}

	// Если уже отправляли уведомление для этой войны
	if startTimeStr == w.notifiedWarStartTime {
		return nil
	}

	// Парсим время начала войны
	startTime, err := time.Parse(time.RFC3339, startTimeStr)
	if err != nil {
		return err
	}

	now := time.Now().UTC()

	// Проверяем, что война начнется менее чем через час
	timeUntilStart := startTime.Sub(now)
	if timeUntilStart <= time.Hour && timeUntilStart > 0 {
		if err := w.sendWarStartNotification(warData); err != nil {
			return err
		}
		w.notifiedWarStartTime = startTimeStr
	}

	return nil
}

// sendWarStartNotification отправляет уведомление о начале войны
func (w *WarArchiver) sendWarStartNotification(warData map[string]interface{}) error {
	if w.botInstance == nil {
		return nil
	}

	// Извлекаем данные о противнике
	opponentName := "Неизвестный противник"
	if opponent, ok := warData["opponent"].(map[string]interface{}); ok {
		if name, ok := opponent["name"].(string); ok {
			opponentName = name
		}
	}

	// Извлекаем размеры команд
	clanSize := 0
	opponentSize := 0
	if clan, ok := warData["clan"].(map[string]interface{}); ok {
		if members, ok := clan["members"].([]interface{}); ok {
			clanSize = len(members)
		}
	}
	if opponent, ok := warData["opponent"].(map[string]interface{}); ok {
		if members, ok := opponent["members"].([]interface{}); ok {
			opponentSize = len(members)
		}
	}

	// Получаем список подписанных пользователей
	subscribedUsers, err := w.dbService.GetSubscribedUsers()
	if err != nil {
		return err
	}

	log.Printf("[Архиватор] Скоро начнется война! Отправка уведомлений %d пользователям...", len(subscribedUsers))

	// Здесь должна быть логика отправки уведомлений через Telegram Bot
	// Но так как это интерфейс, реализация будет в основном боте

	return nil
}

// checkCompletedWar проверяет и сохраняет завершенную войну
func (w *WarArchiver) checkCompletedWar(warData map[string]interface{}) error {
	endTime, ok := warData["endTime"].(string)
	if !ok || endTime == "" {
		return nil
	}

	// Проверяем, не сохраняли ли мы уже эту войну
	exists, err := w.dbService.WarExists(endTime)
	if err != nil {
		return err
	}
	if exists {
		return nil
	}

	// Если это та же война, что мы уже обработали
	if endTime == w.lastKnownWarEndTime {
		return nil
	}

	log.Printf("[Архиватор] Обнаружена новая завершенная война: %s", endTime)

	// Проверяем, является ли это войной ЛВК
	isCWLWar, err := w.isCWLWar()
	if err != nil {
		log.Printf("[Архиватор] Ошибка при проверке ЛВК: %v", err)
		isCWLWar = false
	}

	// Анализируем и сохраняем войну
	if err := w.analyzeAndSaveWar(warData, isCWLWar); err != nil {
		return err
	}

	w.lastKnownWarEndTime = endTime

	return nil
}

// isCWLWar проверяет, является ли текущая война частью ЛВК
func (w *WarArchiver) isCWLWar() (bool, error) {
	leagueGroup, err := w.cocClient.GetClanWarLeagueGroup(w.clanTag)
	if err != nil {
		return false, err
	}

	return api.IsCWLActive(leagueGroup), nil
}

// analyzeAndSaveWar анализирует и сохраняет войну
func (w *WarArchiver) analyzeAndSaveWar(warData map[string]interface{}, isCWLWar bool) error {
	clanData, ok := warData["clan"].(map[string]interface{})
	if !ok {
		return nil
	}

	opponentData, ok := warData["opponent"].(map[string]interface{})
	if !ok {
		return nil
	}

	// Основная информация о войне
	endTime, _ := warData["endTime"].(string)

	opponentName := "Неизвестный противник"
	if name, ok := opponentData["name"].(string); ok {
		opponentName = name
	}

	teamSize := 0
	if members, ok := clanData["members"].([]interface{}); ok {
		teamSize = len(members)
	}

	clanStars := int(getFloatValue(clanData, "stars"))
	opponentStars := int(getFloatValue(opponentData, "stars"))
	clanDestruction := getFloatValue(clanData, "destructionPercentage")
	opponentDestruction := getFloatValue(opponentData, "destructionPercentage")

	// Подсчет использованных атак и нарушений
	clanAttacksUsed, totalViolations, _ := w.analyzeAttacks(clanData)

	// Определение результата
	result := api.DetermineWarResult(clanStars, opponentStars)

	// Создание объекта войны для сохранения
	warToSave := models.NewWarToSave(
		endTime,
		opponentName,
		teamSize,
		clanStars,
		opponentStars,
		clanDestruction,
		opponentDestruction,
		clanAttacksUsed,
		result,
		isCWLWar,
		totalViolations,
	)

	// Сохранение в базу данных
	if err := w.dbService.SaveWar(warToSave); err != nil {
		log.Printf("[Архиватор] Ошибка при сохранении войны против %s: %v", opponentName, err)
		return err
	}

	warType := "КВ"
	if isCWLWar {
		warType = "ЛВК"
	}
	log.Printf("[Архиватор] Война против %s сохранена. Является %s: %v", opponentName, warType, isCWLWar)

	return nil
}

// analyzeAttacks анализирует атаки клана
func (w *WarArchiver) analyzeAttacks(clanData map[string]interface{}) (int, int, map[string][]models.AttackData) {
	members, ok := clanData["members"].([]interface{})
	if !ok {
		return 0, 0, make(map[string][]models.AttackData)
	}

	totalAttacksUsed := 0
	totalViolations := 0
	attacksByMember := make(map[string][]models.AttackData)

	for _, m := range members {
		member, ok := m.(map[string]interface{})
		if !ok {
			continue
		}

		memberTag, _ := member["tag"].(string)
		memberName, _ := member["name"].(string)

		attacks, ok := member["attacks"].([]interface{})
		if !ok {
			attacks = []interface{}{}
		}

		totalAttacksUsed += len(attacks)

		// Анализ нарушений
		memberViolations := w.analyzeMemberViolations(member, attacks)
		totalViolations += memberViolations

		// Сохранение атак участника
		if len(attacks) > 0 {
			memberAttacks := make([]models.AttackData, 0, len(attacks))
			for _, a := range attacks {
				attack, ok := a.(map[string]interface{})
				if !ok {
					continue
				}

				attackData := models.AttackData{
					AttackerName: memberName,
					DefenderTag:  getStringValue(attack, "defenderTag"),
					Stars:        int(getFloatValue(attack, "stars")),
					Destruction:  getFloatValue(attack, "destructionPercentage"),
					Order:        int(getFloatValue(attack, "order")),
					Timestamp:    0, // API не предоставляет timestamp
					IsViolation:  0, // Требует дополнительного анализа
				}
				memberAttacks = append(memberAttacks, attackData)
			}
			attacksByMember[memberTag] = memberAttacks
		}
	}

	return totalAttacksUsed, totalViolations, attacksByMember
}

// analyzeMemberViolations анализирует нарушения участника
func (w *WarArchiver) analyzeMemberViolations(member map[string]interface{}, attacks []interface{}) int {
	violations := 0

	// Простая проверка: если участник не использовал все атаки
	expectedAttacks := 2 // Обычно в КВ каждый участник может атаковать 2 раза
	if len(attacks) < expectedAttacks {
		violations += expectedAttacks - len(attacks)
	}

	return violations
}

// checkDonationSnapshots проверяет и создает снимки донатов
func (w *WarArchiver) checkDonationSnapshots() error {
	// Проверяем, нужно ли создавать снимок
	now := time.Now()
	if w.lastDonationSnapshot != nil {
		timeSinceLastSnapshot := now.Sub(*w.lastDonationSnapshot)
		if timeSinceLastSnapshot < w.donationSnapshotInterval {
			return nil
		}
	}

	log.Println("[Архиватор] Создание снимка донатов")

	// Получаем информацию о клане
	clanInfo, err := w.cocClient.GetClanInfo(w.clanTag)
	if err != nil {
		return err
	}

	members, ok := clanInfo["memberList"].([]interface{})
	if !ok {
		return nil
	}

	// Сохраняем снимки для каждого участника
	for _, m := range members {
		member, ok := m.(map[string]interface{})
		if !ok {
			continue
		}

		memberTag, _ := member["tag"].(string)
		donations := int(getFloatValue(member, "donations"))
		donationsReceived := int(getFloatValue(member, "donationsReceived"))

		// Сохраняем снимок
		if err := w.dbService.SaveDonationSnapshot(memberTag, donations, donationsReceived); err != nil {
			log.Printf("[Архиватор] Ошибка при сохранении снимка донатов для %s: %v", memberTag, err)
		}
	}

	w.lastDonationSnapshot = &now
	log.Println("[Архиватор] Снимок донатов создан")

	return nil
}

// SetBotInstance устанавливает экземпляр бота
func (w *WarArchiver) SetBotInstance(botInstance interface{}) {
	w.botInstance = botInstance
}

// Вспомогательные функции для извлечения значений из map[string]interface{}

func getFloatValue(data map[string]interface{}, key string) float64 {
	if val, ok := data[key].(float64); ok {
		return val
	}
	return 0.0
}

func getStringValue(data map[string]interface{}, key string) string {
	if val, ok := data[key].(string); ok {
		return val
	}
	return ""
}
