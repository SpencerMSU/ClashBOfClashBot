package services

import (
	"context"
	"fmt"
	"net/url"
	"regexp"
	"strings"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/sirupsen/logrus"
	"golang.org/x/time/rate"
)

// CocApiClient provides Clash of Clans API access - exact copy from Python coc_api.py
type CocApiClient struct {
	client    *resty.Client
	apiToken  string
	baseURL   string
	limiter   *rate.Limiter
	logger    *logrus.Logger
}

// NewCocApiClient creates a new Clash of Clans API client
func NewCocApiClient(apiToken, baseURL string) *CocApiClient {
	if baseURL == "" {
		baseURL = "https://api.clashofclans.com/v1"
	}

	client := resty.New()
	client.SetTimeout(30 * time.Second)
	client.SetHeader("Authorization", "Bearer "+apiToken)
	client.SetHeader("Accept", "application/json")

	// Rate limiter: 1000 requests per second as per COC API limits
	limiter := rate.NewLimiter(rate.Limit(1000), 1000)

	return &CocApiClient{
		client:   client,
		apiToken: apiToken,
		baseURL:  baseURL,
		limiter:  limiter,
		logger:   logrus.StandardLogger(),
	}
}

// ============================================================================
// PLAYER OPERATIONS - exact copy from Python coc_api.py
// ============================================================================

// Player represents a player from COC API
type Player struct {
	Tag              string                 `json:"tag"`
	Name             string                 `json:"name"`
	TownHallLevel    int                    `json:"townHallLevel"`
	ExpLevel         int                    `json:"expLevel"`
	Trophies         int                    `json:"trophies"`
	BestTrophies     int                    `json:"bestTrophies"`
	WarStars         int                    `json:"warStars"`
	AttackWins       int                    `json:"attackWins"`
	DefenseWins      int                    `json:"defenseWins"`
	BuilderHallLevel int                    `json:"builderHallLevel"`
	Donations        int                    `json:"donations"`
	DonationsReceived int                   `json:"donationsReceived"`
	Clan             *PlayerClan            `json:"clan,omitempty"`
	League           *League                `json:"league,omitempty"`
	Achievements     []Achievement          `json:"achievements"`
	Heroes           []Hero                 `json:"heroes"`
	Troops           []Troop                `json:"troops"`
	Spells           []Spell                `json:"spells"`
	Buildings        []Building             `json:"buildings"`
}

type PlayerClan struct {
	Tag       string `json:"tag"`
	Name      string `json:"name"`
	ClanLevel int    `json:"clanLevel"`
	BadgeURLs Badge  `json:"badgeUrls"`
}

type League struct {
	ID        int   `json:"id"`
	Name      string `json:"name"`
	IconURLs  Badge `json:"iconUrls"`
}

type Badge struct {
	Small  string `json:"small"`
	Large  string `json:"large"`
	Medium string `json:"medium"`
}

type Achievement struct {
	Name           string `json:"name"`
	Stars          int    `json:"stars"`
	Value          int    `json:"value"`
	Target         int    `json:"target"`
	Info           string `json:"info"`
	CompletionInfo string `json:"completionInfo"`
	Village        string `json:"village"`
}

type Hero struct {
	Name     string `json:"name"`
	Level    int    `json:"level"`
	MaxLevel int    `json:"maxLevel"`
	Village  string `json:"village"`
}

type Troop struct {
	Name     string `json:"name"`
	Level    int    `json:"level"`
	MaxLevel int    `json:"maxLevel"`
	Village  string `json:"village"`
}

type Spell struct {
	Name     string `json:"name"`
	Level    int    `json:"level"`
	MaxLevel int    `json:"maxLevel"`
	Village  string `json:"village"`
}

type Building struct {
	Name     string `json:"name"`
	Level    int    `json:"level"`
	MaxLevel int    `json:"maxLevel"`
	Village  string `json:"village"`
}

// GetPlayer gets player information - exact copy from get_player()
func (coc *CocApiClient) GetPlayer(playerTag string) (*Player, error) {
	// Wait for rate limiter with context
	ctx := context.Background()
	err := coc.limiter.Wait(ctx)
	if err != nil {
		return nil, fmt.Errorf("rate limiter error: %w", err)
	}

	formattedTag := FormatPlayerTag(playerTag)
	encodedTag := url.QueryEscape(formattedTag)
	
	var player Player
	resp, err := coc.client.R().
		SetResult(&player).
		Get(fmt.Sprintf("%s/players/%s", coc.baseURL, encodedTag))

	if err != nil {
		coc.logger.Errorf("Error fetching player %s: %v", playerTag, err)
		return nil, fmt.Errorf("network error: %w", err)
	}

	if resp.StatusCode() == 404 {
		return nil, fmt.Errorf("player not found: %s", playerTag)
	}

	if resp.StatusCode() != 200 {
		coc.logger.Errorf("COC API error for player %s: %d - %s", playerTag, resp.StatusCode(), resp.String())
		return nil, fmt.Errorf("API error: %d", resp.StatusCode())
	}

	coc.logger.Debugf("Player %s fetched successfully", playerTag)
	return &player, nil
}

// GetPlayerWithRetry gets player with retry logic - exact copy from get_player_with_retry()
func (coc *CocApiClient) GetPlayerWithRetry(playerTag string, maxRetries int) (*Player, error) {
	var lastErr error
	
	for i := 0; i < maxRetries; i++ {
		player, err := coc.GetPlayer(playerTag)
		if err == nil {
			return player, nil
		}
		
		lastErr = err
		if i < maxRetries-1 {
			// Wait before retry
			time.Sleep(time.Second * time.Duration(i+1))
		}
	}
	
	return nil, fmt.Errorf("failed after %d retries: %w", maxRetries, lastErr)
}

// ============================================================================
// CLAN OPERATIONS - exact copy from Python coc_api.py
// ============================================================================

// Clan represents a clan from COC API
type Clan struct {
	Tag                   string       `json:"tag"`
	Name                  string       `json:"name"`
	Type                  string       `json:"type"`
	Description           string       `json:"description"`
	Location              *Location    `json:"location,omitempty"`
	BadgeURLs             Badge        `json:"badgeUrls"`
	ClanLevel             int          `json:"clanLevel"`
	ClanPoints            int          `json:"clanPoints"`
	ClanVersusPoints      int          `json:"clanVersusPoints"`
	RequiredTrophies      int          `json:"requiredTrophies"`
	WarFrequency          string       `json:"warFrequency"`
	WarWinStreak          int          `json:"warWinStreak"`
	WarWins               int          `json:"warWins"`
	WarTies               int          `json:"warTies"`
	WarLosses             int          `json:"warLosses"`
	IsWarLogPublic        bool         `json:"isWarLogPublic"`
	WarLeague             *WarLeague   `json:"warLeague,omitempty"`
	Members               int          `json:"members"`
	MemberList            []ClanMember `json:"memberList"`
	Labels                []Label      `json:"labels"`
	RequiredVersusTrophies int         `json:"requiredVersusTrophies"`
	RequiredTownhallLevel int          `json:"requiredTownhallLevel"`
}

type Location struct {
	ID          int    `json:"id"`
	Name        string `json:"name"`
	IsCountry   bool   `json:"isCountry"`
	CountryCode string `json:"countryCode"`
}

type WarLeague struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

type ClanMember struct {
	Tag              string      `json:"tag"`
	Name             string      `json:"name"`
	Role             string      `json:"role"`
	ExpLevel         int         `json:"expLevel"`
	League           *League     `json:"league,omitempty"`
	Trophies         int         `json:"trophies"`
	VersusTrophies   int         `json:"versusTrophies"`
	ClanRank         int         `json:"clanRank"`
	PreviousClanRank int         `json:"previousClanRank"`
	Donations        int         `json:"donations"`
	DonationsReceived int        `json:"donationsReceived"`
}

type Label struct {
	ID       int   `json:"id"`
	Name     string `json:"name"`
	IconURLs Badge `json:"iconUrls"`
}

// GetClan gets clan information - exact copy from get_clan()
func (coc *CocApiClient) GetClan(clanTag string) (*Clan, error) {
	// Wait for rate limiter with context
	ctx := context.Background()
	err := coc.limiter.Wait(ctx)
	if err != nil {
		return nil, fmt.Errorf("rate limiter error: %w", err)
	}

	formattedTag := FormatClanTag(clanTag)
	encodedTag := url.QueryEscape(formattedTag)
	
	var clan Clan
	resp, err := coc.client.R().
		SetResult(&clan).
		Get(fmt.Sprintf("%s/clans/%s", coc.baseURL, encodedTag))

	if err != nil {
		coc.logger.Errorf("Error fetching clan %s: %v", clanTag, err)
		return nil, fmt.Errorf("network error: %w", err)
	}

	if resp.StatusCode() == 404 {
		return nil, fmt.Errorf("clan not found: %s", clanTag)
	}

	if resp.StatusCode() != 200 {
		coc.logger.Errorf("COC API error for clan %s: %d - %s", clanTag, resp.StatusCode(), resp.String())
		return nil, fmt.Errorf("API error: %d", resp.StatusCode())
	}

	coc.logger.Debugf("Clan %s fetched successfully", clanTag)
	return &clan, nil
}

// GetClanMembers gets clan members - exact copy from get_clan_members()
func (coc *CocApiClient) GetClanMembers(clanTag string) ([]ClanMember, error) {
	clan, err := coc.GetClan(clanTag)
	if err != nil {
		return nil, err
	}
	return clan.MemberList, nil
}

// ============================================================================
// WAR OPERATIONS - exact copy from Python coc_api.py
// ============================================================================

// WarInfo represents current war information
type WarInfo struct {
	State          string    `json:"state"`
	TeamSize       int       `json:"teamSize"`
	PreparationStartTime string `json:"preparationStartTime"`
	StartTime      string    `json:"startTime"`
	EndTime        string    `json:"endTime"`
	Clan           WarClan   `json:"clan"`
	Opponent       WarClan   `json:"opponent"`
}

type WarClan struct {
	Tag                string      `json:"tag"`
	Name               string      `json:"name"`
	BadgeURLs          Badge       `json:"badgeUrls"`
	ClanLevel          int         `json:"clanLevel"`
	Attacks            int         `json:"attacks"`
	Stars              int         `json:"stars"`
	DestructionPercentage float64  `json:"destructionPercentage"`
	Members            []WarMember `json:"members"`
}

type WarMember struct {
	Tag                string      `json:"tag"`
	Name               string      `json:"name"`
	TownhallLevel      int         `json:"townhallLevel"`
	MapPosition        int         `json:"mapPosition"`
	Attacks            []WarAttack `json:"attacks"`
	OpponentAttacks    int         `json:"opponentAttacks"`
	BestOpponentAttack *WarAttack  `json:"bestOpponentAttack,omitempty"`
}

type WarAttack struct {
	AttackerTag              string  `json:"attackerTag"`
	DefenderTag              string  `json:"defenderTag"`
	Stars                    int     `json:"stars"`
	DestructionPercentage    float64 `json:"destructionPercentage"`
	Order                    int     `json:"order"`
	Duration                 int     `json:"duration"`
}

// GetClanCurrentWar gets current war information - exact copy from get_clan_current_war()
func (coc *CocApiClient) GetClanCurrentWar(clanTag string) (*WarInfo, error) {
	// Wait for rate limiter with context
	ctx := context.Background()
	err := coc.limiter.Wait(ctx)
	if err != nil {
		return nil, fmt.Errorf("rate limiter error: %w", err)
	}

	formattedTag := FormatClanTag(clanTag)
	encodedTag := url.QueryEscape(formattedTag)
	
	var war WarInfo
	resp, err := coc.client.R().
		SetResult(&war).
		Get(fmt.Sprintf("%s/clans/%s/currentwar", coc.baseURL, encodedTag))

	if err != nil {
		coc.logger.Errorf("Error fetching current war for clan %s: %v", clanTag, err)
		return nil, fmt.Errorf("network error: %w", err)
	}

	if resp.StatusCode() == 404 {
		return nil, fmt.Errorf("clan not found: %s", clanTag)
	}

	if resp.StatusCode() != 200 {
		coc.logger.Errorf("COC API error for current war %s: %d - %s", clanTag, resp.StatusCode(), resp.String())
		return nil, fmt.Errorf("API error: %d", resp.StatusCode())
	}

	coc.logger.Debugf("Current war for clan %s fetched successfully", clanTag)
	return &war, nil
}

// ============================================================================
// VALIDATION AND FORMATTING - exact copy from Python coc_api.py
// ============================================================================

var (
	playerTagRegex = regexp.MustCompile(`^#[0-9A-Z]{8,9}$`)
	clanTagRegex   = regexp.MustCompile(`^#[0-9A-Z]{8,9}$`)
)

// ValidatePlayerTag validates a player tag - exact copy from validate_player_tag()
func ValidatePlayerTag(tag string) bool {
	formattedTag := FormatPlayerTag(tag)
	return playerTagRegex.MatchString(formattedTag)
}

// ValidateClanTag validates a clan tag - exact copy from validate_clan_tag()
func ValidateClanTag(tag string) bool {
	formattedTag := FormatClanTag(tag)
	return clanTagRegex.MatchString(formattedTag)
}

// FormatPlayerTag formats a player tag - exact copy from format_player_tag()
func FormatPlayerTag(tag string) string {
	// Remove spaces and convert to uppercase
	formatted := strings.ToUpper(strings.ReplaceAll(tag, " ", ""))
	
	// Add # if not present
	if !strings.HasPrefix(formatted, "#") {
		formatted = "#" + formatted
	}
	
	return formatted
}

// FormatClanTag formats a clan tag - exact copy from format_clan_tag()
func FormatClanTag(tag string) string {
	// Same logic as player tag
	return FormatPlayerTag(tag)
}

// IsPlayerTag determines if a tag is a player tag - exact copy from is_player_tag()
func IsPlayerTag(tag string) bool {
	return ValidatePlayerTag(tag)
}

// IsClanTag determines if a tag is a clan tag - exact copy from is_clan_tag()
func IsClanTag(tag string) bool {
	return ValidateClanTag(tag)
}

// ============================================================================
// WAR UTILITIES - exact copy from Python coc_api.py
// ============================================================================

// IsWarEnded checks if war has ended - exact copy from is_war_ended()
func IsWarEnded(war *WarInfo) bool {
	return war.State == "warEnded"
}

// IsWarInPreparation checks if war is in preparation - exact copy from is_war_in_preparation()
func IsWarInPreparation(war *WarInfo) bool {
	return war.State == "preparation"
}

// IsWarActive checks if war is currently active - exact copy from is_war_active()
func IsWarActive(war *WarInfo) bool {
	return war.State == "inWar"
}

// Close closes the API client
func (coc *CocApiClient) Close() {
	// No explicit cleanup needed for HTTP client
}