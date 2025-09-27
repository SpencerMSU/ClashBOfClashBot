package utils

// BuildingInfo represents information about a building level
type BuildingInfo struct {
	Name           string            `json:"name"`
	Level          int               `json:"level"`
	UpgradeCost    int64             `json:"upgrade_cost"`
	UpgradeTime    int               `json:"upgrade_time"` // in minutes
	ResourceType   string            `json:"resource_type"`
	THRequired     int               `json:"th_required"`
	MaxLevel       int               `json:"max_level"`
	BuildingType   string            `json:"building_type"`
	Village        string            `json:"village"` // main or builder
}

// BuildingData contains all building information - exact copy from Python building_data.py
var BuildingData = map[string]map[int]BuildingInfo{
	// DEFENSE BUILDINGS
	"cannon": {
		1:  {Name: "Пушка", Level: 1, UpgradeCost: 250, UpgradeTime: 0, ResourceType: "gold", THRequired: 1, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		2:  {Name: "Пушка", Level: 2, UpgradeCost: 1000, UpgradeTime: 15, ResourceType: "gold", THRequired: 1, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		3:  {Name: "Пушка", Level: 3, UpgradeCost: 4000, UpgradeTime: 120, ResourceType: "gold", THRequired: 2, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		4:  {Name: "Пушка", Level: 4, UpgradeCost: 16000, UpgradeTime: 480, ResourceType: "gold", THRequired: 3, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		5:  {Name: "Пушка", Level: 5, UpgradeCost: 50000, UpgradeTime: 720, ResourceType: "gold", THRequired: 4, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		6:  {Name: "Пушка", Level: 6, UpgradeCost: 100000, UpgradeTime: 1440, ResourceType: "gold", THRequired: 5, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		7:  {Name: "Пушка", Level: 7, UpgradeCost: 180000, UpgradeTime: 2880, ResourceType: "gold", THRequired: 6, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		8:  {Name: "Пушка", Level: 8, UpgradeCost: 360000, UpgradeTime: 4320, ResourceType: "gold", THRequired: 8, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		9:  {Name: "Пушка", Level: 9, UpgradeCost: 680000, UpgradeTime: 5760, ResourceType: "gold", THRequired: 9, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		10: {Name: "Пушка", Level: 10, UpgradeCost: 1360000, UpgradeTime: 8640, ResourceType: "gold", THRequired: 10, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		11: {Name: "Пушка", Level: 11, UpgradeCost: 2000000, UpgradeTime: 10080, ResourceType: "gold", THRequired: 11, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		12: {Name: "Пушка", Level: 12, UpgradeCost: 2400000, UpgradeTime: 11520, ResourceType: "gold", THRequired: 12, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		13: {Name: "Пушка", Level: 13, UpgradeCost: 3200000, UpgradeTime: 12960, ResourceType: "gold", THRequired: 13, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		14: {Name: "Пушка", Level: 14, UpgradeCost: 4000000, UpgradeTime: 14400, ResourceType: "gold", THRequired: 14, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		15: {Name: "Пушка", Level: 15, UpgradeCost: 5200000, UpgradeTime: 15840, ResourceType: "gold", THRequired: 15, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		16: {Name: "Пушка", Level: 16, UpgradeCost: 6800000, UpgradeTime: 17280, ResourceType: "gold", THRequired: 16, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		17: {Name: "Пушка", Level: 17, UpgradeCost: 8800000, UpgradeTime: 18720, ResourceType: "gold", THRequired: 17, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		18: {Name: "Пушка", Level: 18, UpgradeCost: 11400000, UpgradeTime: 20160, ResourceType: "gold", THRequired: 18, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		19: {Name: "Пушка", Level: 19, UpgradeCost: 14800000, UpgradeTime: 21600, ResourceType: "gold", THRequired: 19, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		20: {Name: "Пушка", Level: 20, UpgradeCost: 19200000, UpgradeTime: 23040, ResourceType: "gold", THRequired: 20, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		21: {Name: "Пушка", Level: 21, UpgradeCost: 24800000, UpgradeTime: 24480, ResourceType: "gold", THRequired: 21, MaxLevel: 21, BuildingType: "defense", Village: "main"},
	},

	"archer_tower": {
		1:  {Name: "Лучница", Level: 1, UpgradeCost: 1000, UpgradeTime: 0, ResourceType: "gold", THRequired: 2, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		2:  {Name: "Лучница", Level: 2, UpgradeCost: 2000, UpgradeTime: 60, ResourceType: "gold", THRequired: 2, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		3:  {Name: "Лучница", Level: 3, UpgradeCost: 5000, UpgradeTime: 300, ResourceType: "gold", THRequired: 3, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		4:  {Name: "Лучница", Level: 4, UpgradeCost: 20000, UpgradeTime: 720, ResourceType: "gold", THRequired: 4, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		5:  {Name: "Лучница", Level: 5, UpgradeCost: 80000, UpgradeTime: 1440, ResourceType: "gold", THRequired: 5, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		6:  {Name: "Лучница", Level: 6, UpgradeCost: 180000, UpgradeTime: 2880, ResourceType: "gold", THRequired: 6, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		7:  {Name: "Лучница", Level: 7, UpgradeCost: 360000, UpgradeTime: 4320, ResourceType: "gold", THRequired: 7, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		8:  {Name: "Лучница", Level: 8, UpgradeCost: 720000, UpgradeTime: 5760, ResourceType: "gold", THRequired: 8, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		9:  {Name: "Лучница", Level: 9, UpgradeCost: 1360000, UpgradeTime: 8640, ResourceType: "gold", THRequired: 9, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		10: {Name: "Лучница", Level: 10, UpgradeCost: 2000000, UpgradeTime: 10080, ResourceType: "gold", THRequired: 10, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		11: {Name: "Лучница", Level: 11, UpgradeCost: 2400000, UpgradeTime: 11520, ResourceType: "gold", THRequired: 11, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		12: {Name: "Лучница", Level: 12, UpgradeCost: 3200000, UpgradeTime: 12960, ResourceType: "gold", THRequired: 12, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		13: {Name: "Лучница", Level: 13, UpgradeCost: 4000000, UpgradeTime: 14400, ResourceType: "gold", THRequired: 13, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		14: {Name: "Лучница", Level: 14, UpgradeCost: 5200000, UpgradeTime: 15840, ResourceType: "gold", THRequired: 14, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		15: {Name: "Лучница", Level: 15, UpgradeCost: 6800000, UpgradeTime: 17280, ResourceType: "gold", THRequired: 15, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		16: {Name: "Лучница", Level: 16, UpgradeCost: 8800000, UpgradeTime: 18720, ResourceType: "gold", THRequired: 16, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		17: {Name: "Лучница", Level: 17, UpgradeCost: 11400000, UpgradeTime: 20160, ResourceType: "gold", THRequired: 17, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		18: {Name: "Лучница", Level: 18, UpgradeCost: 14800000, UpgradeTime: 21600, ResourceType: "gold", THRequired: 18, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		19: {Name: "Лучница", Level: 19, UpgradeCost: 19200000, UpgradeTime: 23040, ResourceType: "gold", THRequired: 19, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		20: {Name: "Лучница", Level: 20, UpgradeCost: 24800000, UpgradeTime: 24480, ResourceType: "gold", THRequired: 20, MaxLevel: 21, BuildingType: "defense", Village: "main"},
		21: {Name: "Лучница", Level: 21, UpgradeCost: 32000000, UpgradeTime: 25920, ResourceType: "gold", THRequired: 21, MaxLevel: 21, BuildingType: "defense", Village: "main"},
	},

	"town_hall": {
		1:  {Name: "Ратуша", Level: 1, UpgradeCost: 0, UpgradeTime: 0, ResourceType: "gold", THRequired: 1, MaxLevel: 21, BuildingType: "main", Village: "main"},
		2:  {Name: "Ратуша", Level: 2, UpgradeCost: 1000, UpgradeTime: 60, ResourceType: "gold", THRequired: 1, MaxLevel: 21, BuildingType: "main", Village: "main"},
		3:  {Name: "Ратуша", Level: 3, UpgradeCost: 4000, UpgradeTime: 300, ResourceType: "gold", THRequired: 2, MaxLevel: 21, BuildingType: "main", Village: "main"},
		4:  {Name: "Ратуша", Level: 4, UpgradeCost: 25000, UpgradeTime: 1440, ResourceType: "gold", THRequired: 3, MaxLevel: 21, BuildingType: "main", Village: "main"},
		5:  {Name: "Ратуша", Level: 5, UpgradeCost: 150000, UpgradeTime: 2880, ResourceType: "gold", THRequired: 4, MaxLevel: 21, BuildingType: "main", Village: "main"},
		6:  {Name: "Ратуша", Level: 6, UpgradeCost: 500000, UpgradeTime: 4320, ResourceType: "gold", THRequired: 5, MaxLevel: 21, BuildingType: "main", Village: "main"},
		7:  {Name: "Ратуша", Level: 7, UpgradeCost: 1000000, UpgradeTime: 5760, ResourceType: "gold", THRequired: 6, MaxLevel: 21, BuildingType: "main", Village: "main"},
		8:  {Name: "Ратуша", Level: 8, UpgradeCost: 2000000, UpgradeTime: 8640, ResourceType: "gold", THRequired: 7, MaxLevel: 21, BuildingType: "main", Village: "main"},
		9:  {Name: "Ратуша", Level: 9, UpgradeCost: 3000000, UpgradeTime: 11520, ResourceType: "gold", THRequired: 8, MaxLevel: 21, BuildingType: "main", Village: "main"},
		10: {Name: "Ратуша", Level: 10, UpgradeCost: 4000000, UpgradeTime: 14400, ResourceType: "gold", THRequired: 9, MaxLevel: 21, BuildingType: "main", Village: "main"},
		11: {Name: "Ратуша", Level: 11, UpgradeCost: 5000000, UpgradeTime: 17280, ResourceType: "gold", THRequired: 10, MaxLevel: 21, BuildingType: "main", Village: "main"},
		12: {Name: "Ратуша", Level: 12, UpgradeCost: 7000000, UpgradeTime: 20160, ResourceType: "gold", THRequired: 11, MaxLevel: 21, BuildingType: "main", Village: "main"},
		13: {Name: "Ратуша", Level: 13, UpgradeCost: 8500000, UpgradeTime: 25920, ResourceType: "gold", THRequired: 12, MaxLevel: 21, BuildingType: "main", Village: "main"},
		14: {Name: "Ратуша", Level: 14, UpgradeCost: 12000000, UpgradeTime: 28800, ResourceType: "gold", THRequired: 13, MaxLevel: 21, BuildingType: "main", Village: "main"},
		15: {Name: "Ратуша", Level: 15, UpgradeCost: 16000000, UpgradeTime: 31680, ResourceType: "gold", THRequired: 14, MaxLevel: 21, BuildingType: "main", Village: "main"},
		16: {Name: "Ратуша", Level: 16, UpgradeCost: 20000000, UpgradeTime: 34560, ResourceType: "gold", THRequired: 15, MaxLevel: 21, BuildingType: "main", Village: "main"},
		17: {Name: "Ратуша", Level: 17, UpgradeCost: 24000000, UpgradeTime: 37440, ResourceType: "gold", THRequired: 16, MaxLevel: 21, BuildingType: "main", Village: "main"},
		18: {Name: "Ратуша", Level: 18, UpgradeCost: 28000000, UpgradeTime: 40320, ResourceType: "gold", THRequired: 17, MaxLevel: 21, BuildingType: "main", Village: "main"},
		19: {Name: "Ратуша", Level: 19, UpgradeCost: 32000000, UpgradeTime: 43200, ResourceType: "gold", THRequired: 18, MaxLevel: 21, BuildingType: "main", Village: "main"},
		20: {Name: "Ратуша", Level: 20, UpgradeCost: 36000000, UpgradeTime: 46080, ResourceType: "gold", THRequired: 19, MaxLevel: 21, BuildingType: "main", Village: "main"},
		21: {Name: "Ратуша", Level: 21, UpgradeCost: 40000000, UpgradeTime: 48960, ResourceType: "gold", THRequired: 20, MaxLevel: 21, BuildingType: "main", Village: "main"},
	},

	// RESOURCE BUILDINGS
	"gold_mine": {
		1:  {Name: "Золотая шахта", Level: 1, UpgradeCost: 150, UpgradeTime: 0, ResourceType: "gold", THRequired: 1, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		2:  {Name: "Золотая шахта", Level: 2, UpgradeCost: 300, UpgradeTime: 5, ResourceType: "gold", THRequired: 1, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		3:  {Name: "Золотая шахта", Level: 3, UpgradeCost: 700, UpgradeTime: 30, ResourceType: "gold", THRequired: 2, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		4:  {Name: "Золотая шахта", Level: 4, UpgradeCost: 1400, UpgradeTime: 120, ResourceType: "gold", THRequired: 2, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		5:  {Name: "Золотая шахта", Level: 5, UpgradeCost: 3000, UpgradeTime: 240, ResourceType: "gold", THRequired: 3, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		6:  {Name: "Золотая шахта", Level: 6, UpgradeCost: 7000, UpgradeTime: 480, ResourceType: "gold", THRequired: 4, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		7:  {Name: "Золотая шахта", Level: 7, UpgradeCost: 14000, UpgradeTime: 720, ResourceType: "gold", THRequired: 5, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		8:  {Name: "Золотая шахта", Level: 8, UpgradeCost: 28000, UpgradeTime: 1440, ResourceType: "gold", THRequired: 6, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		9:  {Name: "Золотая шахта", Level: 9, UpgradeCost: 56000, UpgradeTime: 2880, ResourceType: "gold", THRequired: 7, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		10: {Name: "Золотая шахта", Level: 10, UpgradeCost: 84000, UpgradeTime: 4320, ResourceType: "gold", THRequired: 8, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		11: {Name: "Золотая шахта", Level: 11, UpgradeCost: 168000, UpgradeTime: 5760, ResourceType: "gold", THRequired: 8, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		12: {Name: "Золотая шахта", Level: 12, UpgradeCost: 336000, UpgradeTime: 8640, ResourceType: "gold", THRequired: 9, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		13: {Name: "Золотая шахта", Level: 13, UpgradeCost: 672000, UpgradeTime: 11520, ResourceType: "gold", THRequired: 10, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		14: {Name: "Золотая шахта", Level: 14, UpgradeCost: 1344000, UpgradeTime: 14400, ResourceType: "gold", THRequired: 11, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		15: {Name: "Золотая шахта", Level: 15, UpgradeCost: 2688000, UpgradeTime: 17280, ResourceType: "gold", THRequired: 12, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		16: {Name: "Золотая шахта", Level: 16, UpgradeCost: 4500000, UpgradeTime: 20160, ResourceType: "gold", THRequired: 13, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		17: {Name: "Золотая шахта", Level: 17, UpgradeCost: 9000000, UpgradeTime: 23040, ResourceType: "gold", THRequired: 14, MaxLevel: 17, BuildingType: "resource", Village: "main"},
	},

	"elixir_collector": {
		1:  {Name: "Накопитель эликсира", Level: 1, UpgradeCost: 150, UpgradeTime: 0, ResourceType: "elixir", THRequired: 1, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		2:  {Name: "Накопитель эликсира", Level: 2, UpgradeCost: 300, UpgradeTime: 5, ResourceType: "elixir", THRequired: 1, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		3:  {Name: "Накопитель эликсира", Level: 3, UpgradeCost: 700, UpgradeTime: 30, ResourceType: "elixir", THRequired: 2, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		4:  {Name: "Накопитель эликсира", Level: 4, UpgradeCost: 1400, UpgradeTime: 120, ResourceType: "elixir", THRequired: 2, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		5:  {Name: "Накопитель эликсира", Level: 5, UpgradeCost: 3000, UpgradeTime: 240, ResourceType: "elixir", THRequired: 3, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		6:  {Name: "Накопитель эликсира", Level: 6, UpgradeCost: 7000, UpgradeTime: 480, ResourceType: "elixir", THRequired: 4, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		7:  {Name: "Накопитель эликсира", Level: 7, UpgradeCost: 14000, UpgradeTime: 720, ResourceType: "elixir", THRequired: 5, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		8:  {Name: "Накопитель эликсира", Level: 8, UpgradeCost: 28000, UpgradeTime: 1440, ResourceType: "elixir", THRequired: 6, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		9:  {Name: "Накопитель эликсира", Level: 9, UpgradeCost: 56000, UpgradeTime: 2880, ResourceType: "elixir", THRequired: 7, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		10: {Name: "Накопитель эликсира", Level: 10, UpgradeCost: 84000, UpgradeTime: 4320, ResourceType: "elixir", THRequired: 8, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		11: {Name: "Накопитель эликсира", Level: 11, UpgradeCost: 168000, UpgradeTime: 5760, ResourceType: "elixir", THRequired: 8, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		12: {Name: "Накопитель эликсира", Level: 12, UpgradeCost: 336000, UpgradeTime: 8640, ResourceType: "elixir", THRequired: 9, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		13: {Name: "Накопитель эликсира", Level: 13, UpgradeCost: 672000, UpgradeTime: 11520, ResourceType: "elixir", THRequired: 10, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		14: {Name: "Накопитель эликсира", Level: 14, UpgradeCost: 1344000, UpgradeTime: 14400, ResourceType: "elixir", THRequired: 11, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		15: {Name: "Накопитель эликсира", Level: 15, UpgradeCost: 2688000, UpgradeTime: 17280, ResourceType: "elixir", THRequired: 12, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		16: {Name: "Накопитель эликсира", Level: 16, UpgradeCost: 4500000, UpgradeTime: 20160, ResourceType: "elixir", THRequired: 13, MaxLevel: 17, BuildingType: "resource", Village: "main"},
		17: {Name: "Накопитель эликсира", Level: 17, UpgradeCost: 9000000, UpgradeTime: 23040, ResourceType: "elixir", THRequired: 14, MaxLevel: 17, BuildingType: "resource", Village: "main"},
	},

	// ARMY BUILDINGS  
	"laboratory": {
		1:  {Name: "Лаборатория", Level: 1, UpgradeCost: 25000, UpgradeTime: 0, ResourceType: "elixir", THRequired: 3, MaxLevel: 13, BuildingType: "army", Village: "main"},
		2:  {Name: "Лаборатория", Level: 2, UpgradeCost: 50000, UpgradeTime: 360, ResourceType: "elixir", THRequired: 5, MaxLevel: 13, BuildingType: "army", Village: "main"},
		3:  {Name: "Лаборатория", Level: 3, UpgradeCost: 100000, UpgradeTime: 720, ResourceType: "elixir", THRequired: 6, MaxLevel: 13, BuildingType: "army", Village: "main"},
		4:  {Name: "Лаборатория", Level: 4, UpgradeCost: 200000, UpgradeTime: 1440, ResourceType: "elixir", THRequired: 7, MaxLevel: 13, BuildingType: "army", Village: "main"},
		5:  {Name: "Лаборатория", Level: 5, UpgradeCost: 500000, UpgradeTime: 2880, ResourceType: "elixir", THRequired: 8, MaxLevel: 13, BuildingType: "army", Village: "main"},
		6:  {Name: "Лаборатория", Level: 6, UpgradeCost: 1000000, UpgradeTime: 4320, ResourceType: "elixir", THRequired: 9, MaxLevel: 13, BuildingType: "army", Village: "main"},
		7:  {Name: "Лаборатория", Level: 7, UpgradeCost: 1500000, UpgradeTime: 5760, ResourceType: "elixir", THRequired: 10, MaxLevel: 13, BuildingType: "army", Village: "main"},
		8:  {Name: "Лаборатория", Level: 8, UpgradeCost: 2000000, UpgradeTime: 8640, ResourceType: "elixir", THRequired: 11, MaxLevel: 13, BuildingType: "army", Village: "main"},
		9:  {Name: "Лаборатория", Level: 9, UpgradeCost: 3000000, UpgradeTime: 11520, ResourceType: "elixir", THRequired: 12, MaxLevel: 13, BuildingType: "army", Village: "main"},
		10: {Name: "Лаборатория", Level: 10, UpgradeCost: 4000000, UpgradeTime: 14400, ResourceType: "elixir", THRequired: 13, MaxLevel: 13, BuildingType: "army", Village: "main"},
		11: {Name: "Лаборатория", Level: 11, UpgradeCost: 9000000, UpgradeTime: 17280, ResourceType: "elixir", THRequired: 14, MaxLevel: 13, BuildingType: "army", Village: "main"},
		12: {Name: "Лаборатория", Level: 12, UpgradeCost: 14000000, UpgradeTime: 20160, ResourceType: "elixir", THRequired: 15, MaxLevel: 13, BuildingType: "army", Village: "main"},
		13: {Name: "Лаборатория", Level: 13, UpgradeCost: 20000000, UpgradeTime: 23040, ResourceType: "elixir", THRequired: 16, MaxLevel: 13, BuildingType: "army", Village: "main"},
	},
}

// GetBuildingInfo returns building information for a specific level - exact copy from Python
func GetBuildingInfo(buildingType string, level int) *BuildingInfo {
	if building, exists := BuildingData[buildingType]; exists {
		if info, exists := building[level]; exists {
			return &info
		}
	}
	return nil
}

// GetUpgradeCost returns the cost to upgrade a building - exact copy from Python
func GetUpgradeCost(buildingType string, level int) int64 {
	info := GetBuildingInfo(buildingType, level+1) // Next level cost
	if info != nil {
		return info.UpgradeCost
	}
	return 0
}

// GetUpgradeTime returns the time to upgrade a building in minutes - exact copy from Python
func GetUpgradeTime(buildingType string, level int) int {
	info := GetBuildingInfo(buildingType, level+1) // Next level time
	if info != nil {
		return info.UpgradeTime
	}
	return 0
}

// GetMaxLevel returns the maximum level for a building - exact copy from Python
func GetMaxLevel(buildingType string) int {
	if building, exists := BuildingData[buildingType]; exists {
		maxLevel := 0
		for level := range building {
			if level > maxLevel {
				maxLevel = level
			}
		}
		return maxLevel
	}
	return 0
}

// GetBuildingTypes returns all available building types
func GetBuildingTypes() []string {
	var types []string
	for buildingType := range BuildingData {
		types = append(types, buildingType)
	}
	return types
}

// GetBuildingsByType returns buildings filtered by type
func GetBuildingsByType(buildingType string) map[string]map[int]BuildingInfo {
	result := make(map[string]map[int]BuildingInfo)
	for name, levels := range BuildingData {
		for _, info := range levels {
			if info.BuildingType == buildingType {
				if result[name] == nil {
					result[name] = make(map[int]BuildingInfo)
				}
				result[name][info.Level] = info
				break
			}
		}
	}
	return result
}

// IsMaxLevel checks if a building is at maximum level
func IsMaxLevel(buildingType string, level int) bool {
	return level >= GetMaxLevel(buildingType)
}

// GetResourceType returns the resource type needed for upgrade
func GetResourceType(buildingType string) string {
	if building, exists := BuildingData[buildingType]; exists {
		for _, info := range building {
			return info.ResourceType
		}
	}
	return "unknown"
}

// GetTHRequirement returns the Town Hall level required for this building level
func GetTHRequirement(buildingType string, level int) int {
	info := GetBuildingInfo(buildingType, level)
	if info != nil {
		return info.THRequired
	}
	return 1
}