package api

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// CocApiClient клиент для работы с API Clash of Clans
type CocApiClient struct {
	baseURL   string
	apiToken  string
	client    *http.Client
	apiErrors []APIError
}

// APIError структура для трекинга ошибок API
type APIError struct {
	Endpoint  string    `json:"endpoint"`
	Status    int       `json:"status"`
	Message   string    `json:"message"`
	Timestamp time.Time `json:"timestamp"`
}

// NewCocApiClient создает новый экземпляр клиента COC API
func NewCocApiClient(baseURL, apiToken string) *CocApiClient {
	if baseURL == "" {
		baseURL = "https://api.clashofclans.com/v1"
	}

	return &CocApiClient{
		baseURL:  baseURL,
		apiToken: apiToken,
		client: &http.Client{
			Timeout: 15 * time.Second,
			Transport: &http.Transport{
				MaxIdleConns:        100,
				MaxIdleConnsPerHost: 30,
				IdleConnTimeout:     300 * time.Second,
			},
		},
		apiErrors: make([]APIError, 0),
	}
}

// makeRequest выполняет HTTP запрос к API
func (c *CocApiClient) makeRequest(endpoint string, trackErrors bool) (map[string]interface{}, error) {
	fullURL := c.baseURL + endpoint

	req, err := http.NewRequest("GET", fullURL, nil)
	if err != nil {
		return nil, fmt.Errorf("ошибка создания запроса: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.apiToken)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("ошибка выполнения запроса: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == 403 {
		log.Println("ОШИБКА 403: API ключ недействителен или ваш IP изменился. " +
			"Проверьте настройки на developer.clashofclans.com")
		if trackErrors {
			c.trackError(endpoint, 403, "API key invalid or IP changed")
		}
		return nil, fmt.Errorf("403 Forbidden: неверный API ключ")
	}

	if resp.StatusCode == 404 {
		log.Printf("Ресурс не найден: %s", fullURL)
		if trackErrors {
			c.trackError(endpoint, 404, "Resource not found")
		}
		return nil, fmt.Errorf("404 Not Found")
	}

	if resp.StatusCode != 200 {
		log.Printf("Неожиданный статус ответа: %d для %s", resp.StatusCode, fullURL)
		if trackErrors {
			c.trackError(endpoint, resp.StatusCode, "Unexpected status code")
		}
		return nil, fmt.Errorf("неожиданный статус: %d", resp.StatusCode)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("ошибка декодирования JSON: %w", err)
	}

	return result, nil
}

// trackError отслеживает ошибки API
func (c *CocApiClient) trackError(endpoint string, status int, message string) {
	c.apiErrors = append(c.apiErrors, APIError{
		Endpoint:  endpoint,
		Status:    status,
		Message:   message,
		Timestamp: time.Now(),
	})

	// Ограничиваем размер списка ошибок
	if len(c.apiErrors) > 100 {
		c.apiErrors = c.apiErrors[len(c.apiErrors)-100:]
	}
}

// GetAPIErrors возвращает список последних ошибок API
func (c *CocApiClient) GetAPIErrors() []APIError {
	return c.apiErrors
}

// GetPlayerInfo получает информацию об игроке
func (c *CocApiClient) GetPlayerInfo(playerTag string) (map[string]interface{}, error) {
	// Форматируем и валидируем тег
	formattedTag := FormatPlayerTag(playerTag)
	valid, errMsg := ValidatePlayerTag(formattedTag)
	if !valid {
		return nil, fmt.Errorf("невалидный тег игрока: %s", errMsg)
	}

	// URL-кодируем тег (удаляем # и кодируем)
	encodedTag := url.PathEscape(formattedTag)
	endpoint := "/players/" + encodedTag

	data, err := c.makeRequest(endpoint, true)
	if err != nil {
		return nil, fmt.Errorf("ошибка получения данных игрока: %w", err)
	}

	return data, nil
}

// GetClanInfo получает информацию о клане
func (c *CocApiClient) GetClanInfo(clanTag string) (map[string]interface{}, error) {
	// Форматируем и валидируем тег
	formattedTag := FormatClanTag(clanTag)
	valid, errMsg := ValidateClanTag(formattedTag)
	if !valid {
		return nil, fmt.Errorf("невалидный тег клана: %s", errMsg)
	}

	// URL-кодируем тег
	encodedTag := url.PathEscape(formattedTag)
	endpoint := "/clans/" + encodedTag

	data, err := c.makeRequest(endpoint, true)
	if err != nil {
		return nil, fmt.Errorf("ошибка получения данных клана: %w", err)
	}

	return data, nil
}

// GetClanMembers получает список участников клана
func (c *CocApiClient) GetClanMembers(clanTag string) ([]map[string]interface{}, error) {
	clanData, err := c.GetClanInfo(clanTag)
	if err != nil {
		return nil, err
	}

	members := ExtractMemberList(clanData)
	return members, nil
}

// GetClanCurrentWar получает информацию о текущей войне клана
func (c *CocApiClient) GetClanCurrentWar(clanTag string) (map[string]interface{}, error) {
	// Форматируем и валидируем тег
	formattedTag := FormatClanTag(clanTag)
	valid, errMsg := ValidateClanTag(formattedTag)
	if !valid {
		return nil, fmt.Errorf("невалидный тег клана: %s", errMsg)
	}

	// URL-кодируем тег
	encodedTag := url.PathEscape(formattedTag)
	endpoint := "/clans/" + encodedTag + "/currentwar"

	data, err := c.makeRequest(endpoint, true)
	if err != nil {
		return nil, fmt.Errorf("ошибка получения текущей войны: %w", err)
	}

	return data, nil
}

// GetClanWarLog получает лог войн клана
func (c *CocApiClient) GetClanWarLog(clanTag string) (map[string]interface{}, error) {
	// Форматируем и валидируем тег
	formattedTag := FormatClanTag(clanTag)
	valid, errMsg := ValidateClanTag(formattedTag)
	if !valid {
		return nil, fmt.Errorf("невалидный тег клана: %s", errMsg)
	}

	// URL-кодируем тег
	encodedTag := url.PathEscape(formattedTag)
	endpoint := "/clans/" + encodedTag + "/warlog"

	data, err := c.makeRequest(endpoint, true)
	if err != nil {
		return nil, fmt.Errorf("ошибка получения лога войн: %w", err)
	}

	return data, nil
}

// GetClanWarLeagueGroup получает информацию о группе Лиги войн кланов
func (c *CocApiClient) GetClanWarLeagueGroup(clanTag string) (map[string]interface{}, error) {
	// Форматируем и валидируем тег
	formattedTag := FormatClanTag(clanTag)
	valid, errMsg := ValidateClanTag(formattedTag)
	if !valid {
		return nil, fmt.Errorf("невалидный тег клана: %s", errMsg)
	}

	// URL-кодируем тег
	encodedTag := url.PathEscape(formattedTag)
	endpoint := "/clans/" + encodedTag + "/currentwar/leaguegroup"

	data, err := c.makeRequest(endpoint, false) // Не трекаем ошибки для CWL
	if err != nil {
		return nil, fmt.Errorf("ошибка получения группы CWL: %w", err)
	}

	return data, nil
}

// GetCWLWarInfo получает информацию о конкретной войне в CWL
func (c *CocApiClient) GetCWLWarInfo(warTag string) (map[string]interface{}, error) {
	// URL-кодируем тег войны
	encodedTag := url.PathEscape(warTag)
	endpoint := "/clanwarleagues/wars/" + encodedTag

	data, err := c.makeRequest(endpoint, false) // Не трекаем ошибки для CWL
	if err != nil {
		return nil, fmt.Errorf("ошибка получения информации о войне CWL: %w", err)
	}

	return data, nil
}

// Close закрывает соединения клиента
func (c *CocApiClient) Close() {
	// В Go HTTP клиент автоматически управляет соединениями
	// Но можно явно очистить транспорт если нужно
	if transport, ok := c.client.Transport.(*http.Transport); ok {
		transport.CloseIdleConnections()
	}
}

// ==================== УТИЛИТЫ ДЛЯ РАБОТЫ С ТЕГАМИ ====================

// FormatClanTag форматирует тег клана
func FormatClanTag(tag string) string {
	// Удаляем пробелы и приводим к верхнему регистру
	tag = strings.ReplaceAll(tag, " ", "")
	tag = strings.ToUpper(tag)
	// Заменяем O на 0 (частая ошибка)
	tag = strings.ReplaceAll(tag, "O", "0")

	// Добавляем # если его нет
	if !strings.HasPrefix(tag, "#") {
		tag = "#" + tag
	}

	return tag
}

// FormatPlayerTag форматирует тег игрока
func FormatPlayerTag(tag string) string {
	// Удаляем пробелы и приводим к верхнему регистру
	tag = strings.ReplaceAll(tag, " ", "")
	tag = strings.ToUpper(tag)
	// Заменяем O на 0 (частая ошибка)
	tag = strings.ReplaceAll(tag, "O", "0")

	// Добавляем # если его нет
	if !strings.HasPrefix(tag, "#") {
		tag = "#" + tag
	}

	return tag
}

// IsClanTag проверяет, является ли тег тегом клана
func IsClanTag(tag string) bool {
	// Убираем #, пробелы и приводим к верхнему регистру
	cleanTag := strings.ReplaceAll(tag, "#", "")
	cleanTag = strings.ReplaceAll(cleanTag, " ", "")
	cleanTag = strings.ToUpper(cleanTag)

	// Теги кланов обычно 8-9 символов
	return len(cleanTag) >= 8 && len(cleanTag) <= 9
}

// IsPlayerTag проверяет, является ли тег тегом игрока
func IsPlayerTag(tag string) bool {
	// Убираем #, пробелы и приводим к верхнему регистру
	cleanTag := strings.ReplaceAll(tag, "#", "")
	cleanTag = strings.ReplaceAll(cleanTag, " ", "")
	cleanTag = strings.ToUpper(cleanTag)

	// Теги игроков обычно 8-10 символов
	return len(cleanTag) >= 8 && len(cleanTag) <= 10
}

// ValidatePlayerTag проверяет валидность тега игрока
// Возвращает: (валидность, сообщение об ошибке)
func ValidatePlayerTag(tag string) (bool, string) {
	if tag == "" {
		return false, "Тег не может быть пустым"
	}

	cleanTag := strings.ReplaceAll(tag, "#", "")
	cleanTag = strings.ReplaceAll(cleanTag, " ", "")
	cleanTag = strings.ToUpper(cleanTag)

	// Проверяем длину
	if len(cleanTag) < 8 {
		return false, "Тег слишком короткий (должен быть минимум 8 символов)"
	}
	if len(cleanTag) > 10 {
		return false, "Тег слишком длинный (должен быть максимум 10 символов)"
	}

	// Проверяем на недопустимые символы
	validChars := "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	for _, ch := range cleanTag {
		if !strings.ContainsRune(validChars, ch) {
			return false, "Тег содержит недопустимые символы"
		}
	}

	// Предупреждение, если похоже на тег клана
	if len(cleanTag) == 9 {
		return true, "Внимание: тег из 9 символов может быть тегом клана. " +
			"Если поиск не дает результатов, попробуйте поиск по клану."
	}

	return true, ""
}

// ValidateClanTag проверяет валидность тега клана
// Возвращает: (валидность, сообщение об ошибке)
func ValidateClanTag(tag string) (bool, string) {
	if tag == "" {
		return false, "Тег не может быть пустым"
	}

	cleanTag := strings.ReplaceAll(tag, "#", "")
	cleanTag = strings.ReplaceAll(cleanTag, " ", "")
	cleanTag = strings.ToUpper(cleanTag)

	// Проверяем длину
	if len(cleanTag) < 8 {
		return false, "Тег слишком короткий (должен быть минимум 8 символов)"
	}
	if len(cleanTag) > 10 {
		return false, "Тег слишком длинный (должен быть максимум 10 символов)"
	}

	// Проверяем на недопустимые символы
	validChars := "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	for _, ch := range cleanTag {
		if !strings.ContainsRune(validChars, ch) {
			return false, "Тег содержит недопустимые символы"
		}
	}

	return true, ""
}

// ==================== УТИЛИТЫ ДЛЯ РАБОТЫ С ДАННЫМИ ====================

// DetermineWarResult определяет результат войны
func DetermineWarResult(clanStars, opponentStars int) string {
	if clanStars > opponentStars {
		return "win"
	} else if clanStars < opponentStars {
		return "lose"
	}
	return "tie"
}

// ExtractMemberList извлекает список участников из данных клана
func ExtractMemberList(clanData map[string]interface{}) []map[string]interface{} {
	if clanData == nil {
		return []map[string]interface{}{}
	}

	memberListRaw, exists := clanData["memberList"]
	if !exists {
		return []map[string]interface{}{}
	}

	memberList, ok := memberListRaw.([]interface{})
	if !ok {
		return []map[string]interface{}{}
	}

	result := make([]map[string]interface{}, 0, len(memberList))
	for _, member := range memberList {
		if m, ok := member.(map[string]interface{}); ok {
			result = append(result, m)
		}
	}

	return result
}

// IsWarEnded проверяет, завершена ли война
func IsWarEnded(warData map[string]interface{}) bool {
	if warData == nil {
		return false
	}

	state, exists := warData["state"]
	if !exists {
		return false
	}

	stateStr, ok := state.(string)
	if !ok {
		return false
	}

	return stateStr == "warEnded"
}

// IsWarInPreparation проверяет, находится ли война в стадии подготовки
func IsWarInPreparation(warData map[string]interface{}) bool {
	if warData == nil {
		return false
	}

	state, exists := warData["state"]
	if !exists {
		return false
	}

	stateStr, ok := state.(string)
	if !ok {
		return false
	}

	return stateStr == "preparation"
}

// IsCWLActive проверяет, активна ли Лига войн кланов
func IsCWLActive(leagueGroup map[string]interface{}) bool {
	if leagueGroup == nil {
		return false
	}

	state, exists := leagueGroup["state"]
	if !exists {
		return false
	}

	stateStr, ok := state.(string)
	if !ok {
		return false
	}

	// CWL активна если state не "notInWar"
	return stateStr != "notInWar"
}
