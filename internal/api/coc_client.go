package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// CocAPIClient клиент для работы с API Clash of Clans
type CocAPIClient struct {
	baseURL    string
	apiToken   string
	httpClient *http.Client
}

// PlayerInfo представляет информацию об игроке
type PlayerInfo struct {
	Tag                string `json:"tag"`
	Name               string `json:"name"`
	TownHallLevel      int    `json:"townHallLevel"`
	ExpLevel           int    `json:"expLevel"`
	Trophies           int    `json:"trophies"`
	BestTrophies       int    `json:"bestTrophies"`
	WarStars           int    `json:"warStars"`
	AttackWins         int    `json:"attackWins"`
	DefenseWins        int    `json:"defenseWins"`
	DonationsReceived  int    `json:"donationsReceived"`
	DonationsGiven     int    `json:"donations"`
	Clan               *ClanRef `json:"clan,omitempty"`
}

// ClanInfo представляет информацию о клане
type ClanInfo struct {
	Tag               string `json:"tag"`
	Name              string `json:"name"`
	Type              string `json:"type"`
	Description       string `json:"description"`
	Location          *Location `json:"location,omitempty"`
	ClanLevel         int    `json:"clanLevel"`
	ClanPoints        int    `json:"clanPoints"`
	ClanVersusPoints  int    `json:"clanVersusPoints"`
	RequiredTrophies  int    `json:"requiredTrophies"`
	WarFrequency      string `json:"warFrequency"`
	WarWinStreak      int    `json:"warWinStreak"`
	WarWins           int    `json:"warWins"`
	WarTies           int    `json:"warTies,omitempty"`
	WarLosses         int    `json:"warLosses,omitempty"`
	IsWarLogPublic    bool   `json:"isWarLogPublic"`
	Members           int    `json:"members"`
	MemberList        []ClanMember `json:"memberList,omitempty"`
}

// ClanRef представляет ссылку на клан
type ClanRef struct {
	Tag         string `json:"tag"`
	Name        string `json:"name"`
	ClanLevel   int    `json:"clanLevel"`
	BadgeUrls   *BadgeUrls `json:"badgeUrls,omitempty"`
}

// ClanMember представляет участника клана
type ClanMember struct {
	Tag                 string `json:"tag"`
	Name                string `json:"name"`
	Role                string `json:"role"`
	ExpLevel            int    `json:"expLevel"`
	League              *League `json:"league,omitempty"`
	Trophies            int    `json:"trophies"`
	ClanRank            int    `json:"clanRank"`
	PreviousClanRank    int    `json:"previousClanRank"`
	Donations           int    `json:"donations"`
	DonationsReceived   int    `json:"donationsReceived"`
}

// Location представляет локацию
type Location struct {
	ID          int    `json:"id"`
	Name        string `json:"name"`
	IsCountry   bool   `json:"isCountry"`
	CountryCode string `json:"countryCode,omitempty"`
}

// League представляет лигу
type League struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
	IconUrls *IconUrls `json:"iconUrls,omitempty"`
}

// BadgeUrls представляет URL'ы значков
type BadgeUrls struct {
	Small  string `json:"small"`
	Large  string `json:"large"`
	Medium string `json:"medium"`
}

// IconUrls представляет URL'ы иконок
type IconUrls struct {
	Small  string `json:"small"`
	Tiny   string `json:"tiny"`
	Medium string `json:"medium"`
}

// WarInfo представляет информацию о войне
type WarInfo struct {
	State           string    `json:"state"`
	TeamSize        int       `json:"teamSize"`
	PreparationStartTime string `json:"preparationStartTime"`
	StartTime       string    `json:"startTime"`
	EndTime         string    `json:"endTime"`
	Clan            *WarClan  `json:"clan"`
	Opponent        *WarClan  `json:"opponent"`
}

// WarClan представляет клан в войне
type WarClan struct {
	Tag               string `json:"tag"`
	Name              string `json:"name"`
	ClanLevel         int    `json:"clanLevel"`
	Attacks           int    `json:"attacks"`
	Stars             int    `json:"stars"`
	DestructionPercentage float64 `json:"destructionPercentage"`
	Members           []WarMember `json:"members"`
}

// WarMember представляет участника войны
type WarMember struct {
	Tag                string `json:"tag"`
	Name               string `json:"name"`
	MapPosition        int    `json:"mapPosition"`
	TownhallLevel      int    `json:"townhallLevel"`
	OpponentAttacks    int    `json:"opponentAttacks"`
	BestOpponentAttack *Attack `json:"bestOpponentAttack,omitempty"`
	Attacks            []Attack `json:"attacks,omitempty"`
}

// Attack представляет атаку
type Attack struct {
	AttackerTag              string  `json:"attackerTag"`
	DefenderTag              string  `json:"defenderTag"`
	Stars                    int     `json:"stars"`
	DestructionPercentage    float64 `json:"destructionPercentage"`
	Order                    int     `json:"order"`
	Duration                 int     `json:"duration"`
}

// NewCocAPIClient создает новый клиент API
func NewCocAPIClient(baseURL, apiToken string) *CocAPIClient {
	return &CocAPIClient{
		baseURL:  baseURL,
		apiToken: apiToken,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// makeRequest выполняет HTTP запрос к API
func (c *CocAPIClient) makeRequest(endpoint string) ([]byte, error) {
	url := c.baseURL + endpoint
	
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("ошибка создания запроса: %v", err)
	}
	
	req.Header.Set("Authorization", "Bearer "+c.apiToken)
	req.Header.Set("Accept", "application/json")
	
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("ошибка выполнения запроса: %v", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode == 403 {
		return nil, fmt.Errorf("ОШИБКА 403: API ключ недействителен или ваш IP изменился")
	}
	
	if resp.StatusCode == 404 {
		return nil, fmt.Errorf("ресурс не найден: %s", url)
	}
	
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("HTTP %d при запросе к %s", resp.StatusCode, url)
	}
	
	result := make([]byte, 0)
	buf := make([]byte, 1024)
	for {
		n, err := resp.Body.Read(buf)
		if n > 0 {
			result = append(result, buf[:n]...)
		}
		if err != nil {
			break
		}
	}
	
	return result, nil
}

// GetPlayerInfo получает информацию об игроке
func (c *CocAPIClient) GetPlayerInfo(playerTag string) (*PlayerInfo, error) {
	// Валидация и форматирование тега
	formattedTag, err := FormatPlayerTag(playerTag)
	if err != nil {
		return nil, err
	}
	
	endpoint := fmt.Sprintf("/players/%s", url.QueryEscape(formattedTag))
	
	data, err := c.makeRequest(endpoint)
	if err != nil {
		return nil, err
	}
	
	var playerInfo PlayerInfo
	if err := json.Unmarshal(data, &playerInfo); err != nil {
		return nil, fmt.Errorf("ошибка парсинга данных игрока: %v", err)
	}
	
	return &playerInfo, nil
}

// GetClanInfo получает информацию о клане
func (c *CocAPIClient) GetClanInfo(clanTag string) (*ClanInfo, error) {
	// Валидация и форматирование тега
	formattedTag, err := FormatClanTag(clanTag)
	if err != nil {
		return nil, err
	}
	
	endpoint := fmt.Sprintf("/clans/%s", url.QueryEscape(formattedTag))
	
	data, err := c.makeRequest(endpoint)
	if err != nil {
		return nil, err
	}
	
	var clanInfo ClanInfo
	if err := json.Unmarshal(data, &clanInfo); err != nil {
		return nil, fmt.Errorf("ошибка парсинга данных клана: %v", err)
	}
	
	return &clanInfo, nil
}

// GetClanCurrentWar получает информацию о текущей войне клана
func (c *CocAPIClient) GetClanCurrentWar(clanTag string) (*WarInfo, error) {
	formattedTag, err := FormatClanTag(clanTag)
	if err != nil {
		return nil, err
	}
	
	endpoint := fmt.Sprintf("/clans/%s/currentwar", url.QueryEscape(formattedTag))
	
	data, err := c.makeRequest(endpoint)
	if err != nil {
		return nil, err
	}
	
	var warInfo WarInfo
	if err := json.Unmarshal(data, &warInfo); err != nil {
		return nil, fmt.Errorf("ошибка парсинга данных войны: %v", err)
	}
	
	return &warInfo, nil
}

// FormatPlayerTag форматирует тег игрока
func FormatPlayerTag(tag string) (string, error) {
	if tag == "" {
		return "", fmt.Errorf("тег игрока не может быть пустым")
	}
	
	// Удаляем пробелы
	tag = strings.TrimSpace(tag)
	
	// Добавляем # если его нет
	if !strings.HasPrefix(tag, "#") {
		tag = "#" + tag
	}
	
	// Проверяем длину
	if len(tag) < 4 || len(tag) > 15 {
		return "", fmt.Errorf("неверная длина тега игрока: %d символов", len(tag))
	}
	
	return strings.ToUpper(tag), nil
}

// FormatClanTag форматирует тег клана
func FormatClanTag(tag string) (string, error) {
	if tag == "" {
		return "", fmt.Errorf("тег клана не может быть пустым")
	}
	
	// Удаляем пробелы
	tag = strings.TrimSpace(tag)
	
	// Добавляем # если его нет
	if !strings.HasPrefix(tag, "#") {
		tag = "#" + tag
	}
	
	// Проверяем длину
	if len(tag) < 4 || len(tag) > 15 {
		return "", fmt.Errorf("неверная длина тега клана: %d символов", len(tag))
	}
	
	return strings.ToUpper(tag), nil
}