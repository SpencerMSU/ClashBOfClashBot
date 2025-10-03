// Package utils предоставляет утилиты для бота
package utils

import (
	"fmt"
	"strconv"
	"strings"
)

// BuildingLevel представляет информацию об уровне здания
type BuildingLevel struct {
	Cost     int    `json:"cost"`
	Currency string `json:"currency"`
	Time     string `json:"time"`
	THLevel  int    `json:"th_level"`
}

// BuildingInfo представляет информацию о здании
type BuildingInfo struct {
	Name   string                   `json:"name"`
	Levels map[int]BuildingLevel `json:"levels"`
}

// BuildingData содержит данные о всех зданиях Clash of Clans
var BuildingData = map[string]BuildingInfo{
	// ОБОРОНИТЕЛЬНЫЕ ЗДАНИЯ
	"archer_tower": {
		Name: "Башня лучниц",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 1000, Currency: "gold", Time: "1m", THLevel: 2},
			2:  {Cost: 2000, Currency: "gold", Time: "15m", THLevel: 2},
			3:  {Cost: 5000, Currency: "gold", Time: "2h", THLevel: 3},
			4:  {Cost: 20000, Currency: "gold", Time: "6h", THLevel: 4},
			5:  {Cost: 80000, Currency: "gold", Time: "12h", THLevel: 5},
			6:  {Cost: 180000, Currency: "gold", Time: "1d", THLevel: 6},
			7:  {Cost: 360000, Currency: "gold", Time: "2d", THLevel: 7},
			8:  {Cost: 720000, Currency: "gold", Time: "3d", THLevel: 8},
			9:  {Cost: 1500000, Currency: "gold", Time: "4d", THLevel: 9},
			10: {Cost: 2200000, Currency: "gold", Time: "5d", THLevel: 10},
			11: {Cost: 3200000, Currency: "gold", Time: "6d", THLevel: 11},
			12: {Cost: 4500000, Currency: "gold", Time: "7d", THLevel: 12},
			13: {Cost: 6000000, Currency: "gold", Time: "8d", THLevel: 13},
			14: {Cost: 8500000, Currency: "gold", Time: "10d", THLevel: 14},
			15: {Cost: 12000000, Currency: "gold", Time: "12d", THLevel: 15},
			16: {Cost: 16000000, Currency: "gold", Time: "14d", THLevel: 16},
		},
	},
	"cannon": {
		Name: "Пушка",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 250, Currency: "gold", Time: "1m", THLevel: 1},
			2:  {Cost: 1000, Currency: "gold", Time: "15m", THLevel: 1},
			3:  {Cost: 4000, Currency: "gold", Time: "45m", THLevel: 2},
			4:  {Cost: 16000, Currency: "gold", Time: "4h", THLevel: 3},
			5:  {Cost: 50000, Currency: "gold", Time: "8h", THLevel: 4},
			6:  {Cost: 100000, Currency: "gold", Time: "12h", THLevel: 5},
			7:  {Cost: 200000, Currency: "gold", Time: "1d", THLevel: 6},
			8:  {Cost: 400000, Currency: "gold", Time: "2d", THLevel: 7},
			9:  {Cost: 800000, Currency: "gold", Time: "3d", THLevel: 8},
			10: {Cost: 1600000, Currency: "gold", Time: "4d", THLevel: 9},
			11: {Cost: 2400000, Currency: "gold", Time: "5d", THLevel: 10},
			12: {Cost: 3200000, Currency: "gold", Time: "6d", THLevel: 11},
			13: {Cost: 4200000, Currency: "gold", Time: "7d", THLevel: 12},
			14: {Cost: 5600000, Currency: "gold", Time: "8d", THLevel: 13},
			15: {Cost: 7500000, Currency: "gold", Time: "10d", THLevel: 14},
			16: {Cost: 10000000, Currency: "gold", Time: "12d", THLevel: 15},
			17: {Cost: 13000000, Currency: "gold", Time: "14d", THLevel: 16},
		},
	},
	"mortar": {
		Name: "Мортира",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 8000, Currency: "gold", Time: "5h", THLevel: 3},
			2:  {Cost: 32000, Currency: "gold", Time: "8h", THLevel: 4},
			3:  {Cost: 120000, Currency: "gold", Time: "12h", THLevel: 5},
			4:  {Cost: 400000, Currency: "gold", Time: "1d", THLevel: 6},
			5:  {Cost: 800000, Currency: "gold", Time: "2d", THLevel: 7},
			6:  {Cost: 1600000, Currency: "gold", Time: "3d", THLevel: 8},
			7:  {Cost: 2400000, Currency: "gold", Time: "4d", THLevel: 9},
			8:  {Cost: 3200000, Currency: "gold", Time: "5d", THLevel: 10},
			9:  {Cost: 4200000, Currency: "gold", Time: "7d", THLevel: 11},
			10: {Cost: 5600000, Currency: "gold", Time: "8d", THLevel: 12},
			11: {Cost: 7500000, Currency: "gold", Time: "10d", THLevel: 13},
			12: {Cost: 10000000, Currency: "gold", Time: "12d", THLevel: 14},
			13: {Cost: 13000000, Currency: "gold", Time: "14d", THLevel: 15},
		},
	},
	"air_defense": {
		Name: "Воздушная защита",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 22500, Currency: "gold", Time: "4h", THLevel: 4},
			2:  {Cost: 90000, Currency: "gold", Time: "8h", THLevel: 5},
			3:  {Cost: 270000, Currency: "gold", Time: "12h", THLevel: 6},
			4:  {Cost: 500000, Currency: "gold", Time: "1d", THLevel: 7},
			5:  {Cost: 1000000, Currency: "gold", Time: "2d", THLevel: 8},
			6:  {Cost: 1800000, Currency: "gold", Time: "3d", THLevel: 9},
			7:  {Cost: 2800000, Currency: "gold", Time: "4d", THLevel: 10},
			8:  {Cost: 3800000, Currency: "gold", Time: "6d", THLevel: 11},
			9:  {Cost: 5000000, Currency: "gold", Time: "8d", THLevel: 12},
			10: {Cost: 6500000, Currency: "gold", Time: "10d", THLevel: 13},
			11: {Cost: 8500000, Currency: "gold", Time: "12d", THLevel: 14},
			12: {Cost: 11000000, Currency: "gold", Time: "14d", THLevel: 15},
		},
	},
	"wizard_tower": {
		Name: "Башня магов",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 180000, Currency: "gold", Time: "12h", THLevel: 5},
			2:  {Cost: 360000, Currency: "gold", Time: "1d", THLevel: 6},
			3:  {Cost: 650000, Currency: "gold", Time: "2d", THLevel: 7},
			4:  {Cost: 1300000, Currency: "gold", Time: "3d", THLevel: 8},
			5:  {Cost: 2000000, Currency: "gold", Time: "4d", THLevel: 9},
			6:  {Cost: 2600000, Currency: "gold", Time: "5d", THLevel: 10},
			7:  {Cost: 3400000, Currency: "gold", Time: "6d", THLevel: 11},
			8:  {Cost: 4400000, Currency: "gold", Time: "8d", THLevel: 12},
			9:  {Cost: 5800000, Currency: "gold", Time: "10d", THLevel: 13},
			10: {Cost: 7500000, Currency: "gold", Time: "12d", THLevel: 14},
			11: {Cost: 10000000, Currency: "gold", Time: "14d", THLevel: 15},
		},
	},
	"x_bow": {
		Name: "X-Лук",
		Levels: map[int]BuildingLevel{
			1: {Cost: 3000000, Currency: "gold", Time: "7d", THLevel: 9},
			2: {Cost: 4500000, Currency: "gold", Time: "8d", THLevel: 9},
			3: {Cost: 6000000, Currency: "gold", Time: "9d", THLevel: 9},
			4: {Cost: 7500000, Currency: "gold", Time: "10d", THLevel: 10},
			5: {Cost: 9000000, Currency: "gold", Time: "11d", THLevel: 10},
			6: {Cost: 11000000, Currency: "gold", Time: "12d", THLevel: 11},
			7: {Cost: 13000000, Currency: "gold", Time: "13d", THLevel: 12},
			8: {Cost: 15000000, Currency: "gold", Time: "14d", THLevel: 13},
		},
	},
	"inferno_tower": {
		Name: "Адская башня",
		Levels: map[int]BuildingLevel{
			1: {Cost: 5000000, Currency: "gold", Time: "7d", THLevel: 10},
			2: {Cost: 6500000, Currency: "gold", Time: "8d", THLevel: 10},
			3: {Cost: 8000000, Currency: "gold", Time: "9d", THLevel: 10},
			4: {Cost: 10000000, Currency: "gold", Time: "10d", THLevel: 11},
			5: {Cost: 12000000, Currency: "gold", Time: "11d", THLevel: 11},
			6: {Cost: 14000000, Currency: "gold", Time: "12d", THLevel: 12},
			7: {Cost: 16000000, Currency: "gold", Time: "13d", THLevel: 13},
		},
	},
	"eagle_artillery": {
		Name: "Орлиная артиллерия",
		Levels: map[int]BuildingLevel{
			1: {Cost: 8000000, Currency: "gold", Time: "10d", THLevel: 11},
			2: {Cost: 10000000, Currency: "gold", Time: "11d", THLevel: 11},
			3: {Cost: 12000000, Currency: "gold", Time: "12d", THLevel: 11},
			4: {Cost: 14000000, Currency: "gold", Time: "13d", THLevel: 12},
			5: {Cost: 16000000, Currency: "gold", Time: "14d", THLevel: 13},
		},
	},
	"scattershot": {
		Name: "Рассеивающая пушка",
		Levels: map[int]BuildingLevel{
			1: {Cost: 12000000, Currency: "gold", Time: "13d", THLevel: 13},
			2: {Cost: 14000000, Currency: "gold", Time: "14d", THLevel: 13},
			3: {Cost: 16000000, Currency: "gold", Time: "15d", THLevel: 14},
		},
	},
	// РЕСУРСНЫЕ ЗДАНИЯ
	"gold_mine": {
		Name: "Золотой рудник",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 150, Currency: "elixir", Time: "10s", THLevel: 1},
			2:  {Cost: 300, Currency: "elixir", Time: "5m", THLevel: 1},
			3:  {Cost: 700, Currency: "elixir", Time: "15m", THLevel: 2},
			4:  {Cost: 1400, Currency: "elixir", Time: "30m", THLevel: 2},
			5:  {Cost: 3000, Currency: "elixir", Time: "1h", THLevel: 3},
			6:  {Cost: 7000, Currency: "elixir", Time: "2h", THLevel: 3},
			7:  {Cost: 14000, Currency: "elixir", Time: "4h", THLevel: 4},
			8:  {Cost: 28000, Currency: "elixir", Time: "6h", THLevel: 5},
			9:  {Cost: 56000, Currency: "elixir", Time: "12h", THLevel: 6},
			10: {Cost: 84000, Currency: "elixir", Time: "1d", THLevel: 7},
			11: {Cost: 168000, Currency: "elixir", Time: "2d", THLevel: 8},
			12: {Cost: 336000, Currency: "elixir", Time: "3d", THLevel: 9},
			13: {Cost: 672000, Currency: "elixir", Time: "4d", THLevel: 10},
			14: {Cost: 1100000, Currency: "elixir", Time: "5d", THLevel: 11},
		},
	},
	"elixir_collector": {
		Name: "Насос эликсира",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 150, Currency: "gold", Time: "10s", THLevel: 1},
			2:  {Cost: 300, Currency: "gold", Time: "5m", THLevel: 1},
			3:  {Cost: 700, Currency: "gold", Time: "15m", THLevel: 2},
			4:  {Cost: 1400, Currency: "gold", Time: "30m", THLevel: 2},
			5:  {Cost: 3000, Currency: "gold", Time: "1h", THLevel: 3},
			6:  {Cost: 7000, Currency: "gold", Time: "2h", THLevel: 3},
			7:  {Cost: 14000, Currency: "gold", Time: "4h", THLevel: 4},
			8:  {Cost: 28000, Currency: "gold", Time: "6h", THLevel: 5},
			9:  {Cost: 56000, Currency: "gold", Time: "12h", THLevel: 6},
			10: {Cost: 84000, Currency: "gold", Time: "1d", THLevel: 7},
			11: {Cost: 168000, Currency: "gold", Time: "2d", THLevel: 8},
			12: {Cost: 336000, Currency: "gold", Time: "3d", THLevel: 9},
			13: {Cost: 672000, Currency: "gold", Time: "4d", THLevel: 10},
			14: {Cost: 1100000, Currency: "gold", Time: "5d", THLevel: 11},
		},
	},
	"dark_elixir_drill": {
		Name: "Бур темного эликсира",
		Levels: map[int]BuildingLevel{
			1: {Cost: 1000000, Currency: "elixir", Time: "1d", THLevel: 7},
			2: {Cost: 1500000, Currency: "elixir", Time: "2d", THLevel: 8},
			3: {Cost: 2000000, Currency: "elixir", Time: "3d", THLevel: 8},
			4: {Cost: 2500000, Currency: "elixir", Time: "4d", THLevel: 9},
			5: {Cost: 3000000, Currency: "elixir", Time: "5d", THLevel: 9},
			6: {Cost: 3500000, Currency: "elixir", Time: "6d", THLevel: 10},
			7: {Cost: 4000000, Currency: "elixir", Time: "7d", THLevel: 11},
		},
	},
	// ХРАНИЛИЩА
	"gold_storage": {
		Name: "Хранилище золота",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 300, Currency: "elixir", Time: "10s", THLevel: 1},
			2:  {Cost: 750, Currency: "elixir", Time: "15m", THLevel: 2},
			3:  {Cost: 1500, Currency: "elixir", Time: "30m", THLevel: 2},
			4:  {Cost: 3000, Currency: "elixir", Time: "1h", THLevel: 3},
			5:  {Cost: 6000, Currency: "elixir", Time: "2h", THLevel: 3},
			6:  {Cost: 12000, Currency: "elixir", Time: "4h", THLevel: 4},
			7:  {Cost: 25000, Currency: "elixir", Time: "6h", THLevel: 5},
			8:  {Cost: 50000, Currency: "elixir", Time: "12h", THLevel: 6},
			9:  {Cost: 100000, Currency: "elixir", Time: "1d", THLevel: 7},
			10: {Cost: 250000, Currency: "elixir", Time: "2d", THLevel: 8},
			11: {Cost: 500000, Currency: "elixir", Time: "3d", THLevel: 9},
			12: {Cost: 1000000, Currency: "elixir", Time: "4d", THLevel: 10},
			13: {Cost: 1500000, Currency: "elixir", Time: "5d", THLevel: 11},
			14: {Cost: 2000000, Currency: "elixir", Time: "6d", THLevel: 12},
			15: {Cost: 2500000, Currency: "elixir", Time: "7d", THLevel: 13},
			16: {Cost: 3000000, Currency: "elixir", Time: "8d", THLevel: 14},
		},
	},
	"elixir_storage": {
		Name: "Хранилище эликсира",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 300, Currency: "gold", Time: "10s", THLevel: 1},
			2:  {Cost: 750, Currency: "gold", Time: "15m", THLevel: 2},
			3:  {Cost: 1500, Currency: "gold", Time: "30m", THLevel: 2},
			4:  {Cost: 3000, Currency: "gold", Time: "1h", THLevel: 3},
			5:  {Cost: 6000, Currency: "gold", Time: "2h", THLevel: 3},
			6:  {Cost: 12000, Currency: "gold", Time: "4h", THLevel: 4},
			7:  {Cost: 25000, Currency: "gold", Time: "6h", THLevel: 5},
			8:  {Cost: 50000, Currency: "gold", Time: "12h", THLevel: 6},
			9:  {Cost: 100000, Currency: "gold", Time: "1d", THLevel: 7},
			10: {Cost: 250000, Currency: "gold", Time: "2d", THLevel: 8},
			11: {Cost: 500000, Currency: "gold", Time: "3d", THLevel: 9},
			12: {Cost: 1000000, Currency: "gold", Time: "4d", THLevel: 10},
			13: {Cost: 1500000, Currency: "gold", Time: "5d", THLevel: 11},
			14: {Cost: 2000000, Currency: "gold", Time: "6d", THLevel: 12},
			15: {Cost: 2500000, Currency: "gold", Time: "7d", THLevel: 13},
			16: {Cost: 3000000, Currency: "gold", Time: "8d", THLevel: 14},
		},
	},
	"dark_elixir_storage": {
		Name: "Хранилище темного эликсира",
		Levels: map[int]BuildingLevel{
			1: {Cost: 600000, Currency: "elixir", Time: "1d", THLevel: 7},
			2: {Cost: 1200000, Currency: "elixir", Time: "2d", THLevel: 8},
			3: {Cost: 1800000, Currency: "elixir", Time: "3d", THLevel: 8},
			4: {Cost: 2400000, Currency: "elixir", Time: "4d", THLevel: 9},
			5: {Cost: 3000000, Currency: "elixir", Time: "5d", THLevel: 9},
			6: {Cost: 3600000, Currency: "elixir", Time: "6d", THLevel: 10},
			7: {Cost: 4200000, Currency: "elixir", Time: "7d", THLevel: 11},
			8: {Cost: 5400000, Currency: "elixir", Time: "8d", THLevel: 12},
		},
	},
	// ГЕРОЕВ
	"barbarian_king": {
		Name: "Король варваров",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 10000, Currency: "dark_elixir", Time: "0s", THLevel: 7},
			5:  {Cost: 12000, Currency: "dark_elixir", Time: "12h", THLevel: 7},
			10: {Cost: 15000, Currency: "dark_elixir", Time: "1d", THLevel: 8},
			15: {Cost: 20000, Currency: "dark_elixir", Time: "2d", THLevel: 9},
			20: {Cost: 25000, Currency: "dark_elixir", Time: "2d 12h", THLevel: 9},
			25: {Cost: 30000, Currency: "dark_elixir", Time: "3d", THLevel: 10},
			30: {Cost: 35000, Currency: "dark_elixir", Time: "3d 12h", THLevel: 10},
			40: {Cost: 50000, Currency: "dark_elixir", Time: "4d", THLevel: 11},
			50: {Cost: 80000, Currency: "dark_elixir", Time: "5d", THLevel: 12},
			60: {Cost: 120000, Currency: "dark_elixir", Time: "6d", THLevel: 13},
			70: {Cost: 160000, Currency: "dark_elixir", Time: "7d", THLevel: 13},
			75: {Cost: 180000, Currency: "dark_elixir", Time: "7d 12h", THLevel: 14},
			80: {Cost: 200000, Currency: "dark_elixir", Time: "8d", THLevel: 14},
			85: {Cost: 230000, Currency: "dark_elixir", Time: "8d 12h", THLevel: 15},
			90: {Cost: 260000, Currency: "dark_elixir", Time: "9d", THLevel: 15},
			95: {Cost: 300000, Currency: "dark_elixir", Time: "9d 12h", THLevel: 16},
		},
	},
	"archer_queen": {
		Name: "Королева лучниц",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 40000, Currency: "dark_elixir", Time: "0s", THLevel: 9},
			5:  {Cost: 45000, Currency: "dark_elixir", Time: "12h", THLevel: 9},
			10: {Cost: 50000, Currency: "dark_elixir", Time: "1d", THLevel: 9},
			15: {Cost: 55000, Currency: "dark_elixir", Time: "1d 12h", THLevel: 9},
			20: {Cost: 60000, Currency: "dark_elixir", Time: "2d", THLevel: 10},
			25: {Cost: 65000, Currency: "dark_elixir", Time: "2d 12h", THLevel: 10},
			30: {Cost: 70000, Currency: "dark_elixir", Time: "3d", THLevel: 10},
			40: {Cost: 90000, Currency: "dark_elixir", Time: "4d", THLevel: 11},
			50: {Cost: 120000, Currency: "dark_elixir", Time: "5d", THLevel: 12},
			60: {Cost: 160000, Currency: "dark_elixir", Time: "6d", THLevel: 13},
			70: {Cost: 200000, Currency: "dark_elixir", Time: "7d", THLevel: 13},
			75: {Cost: 220000, Currency: "dark_elixir", Time: "7d 12h", THLevel: 14},
			80: {Cost: 240000, Currency: "dark_elixir", Time: "8d", THLevel: 14},
			85: {Cost: 270000, Currency: "dark_elixir", Time: "8d 12h", THLevel: 15},
			90: {Cost: 300000, Currency: "dark_elixir", Time: "9d", THLevel: 15},
			95: {Cost: 340000, Currency: "dark_elixir", Time: "9d 12h", THLevel: 16},
		},
	},
	"grand_warden": {
		Name: "Великий страж",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 6000000, Currency: "elixir", Time: "0s", THLevel: 11},
			5:  {Cost: 7000000, Currency: "elixir", Time: "1d", THLevel: 11},
			10: {Cost: 8000000, Currency: "elixir", Time: "2d", THLevel: 11},
			20: {Cost: 10000000, Currency: "elixir", Time: "4d", THLevel: 11},
			30: {Cost: 12000000, Currency: "elixir", Time: "5d", THLevel: 12},
			40: {Cost: 14000000, Currency: "elixir", Time: "6d", THLevel: 12},
			50: {Cost: 16000000, Currency: "elixir", Time: "7d", THLevel: 13},
			55: {Cost: 17000000, Currency: "elixir", Time: "7d 12h", THLevel: 14},
			60: {Cost: 18000000, Currency: "elixir", Time: "8d", THLevel: 14},
			65: {Cost: 19000000, Currency: "elixir", Time: "8d 12h", THLevel: 15},
		},
	},
	"royal_champion": {
		Name: "Королевский чемпион",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 120000, Currency: "dark_elixir", Time: "0s", THLevel: 13},
			5:  {Cost: 140000, Currency: "dark_elixir", Time: "2d", THLevel: 13},
			10: {Cost: 160000, Currency: "dark_elixir", Time: "4d", THLevel: 13},
			15: {Cost: 180000, Currency: "dark_elixir", Time: "5d", THLevel: 13},
			20: {Cost: 200000, Currency: "dark_elixir", Time: "6d", THLevel: 14},
			25: {Cost: 230000, Currency: "dark_elixir", Time: "7d", THLevel: 14},
			30: {Cost: 260000, Currency: "dark_elixir", Time: "8d", THLevel: 15},
			40: {Cost: 320000, Currency: "dark_elixir", Time: "9d", THLevel: 16},
			45: {Cost: 360000, Currency: "dark_elixir", Time: "9d 12h", THLevel: 16},
		},
	},
	// СТЕНЫ
	"walls": {
		Name: "Стены",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 50, Currency: "gold", Time: "0s", THLevel: 2},
			2:  {Cost: 1000, Currency: "gold", Time: "0s", THLevel: 2},
			3:  {Cost: 5000, Currency: "gold", Time: "0s", THLevel: 3},
			4:  {Cost: 10000, Currency: "gold", Time: "0s", THLevel: 4},
			5:  {Cost: 30000, Currency: "gold", Time: "0s", THLevel: 5},
			6:  {Cost: 75000, Currency: "gold", Time: "0s", THLevel: 6},
			7:  {Cost: 200000, Currency: "gold", Time: "0s", THLevel: 7},
			8:  {Cost: 500000, Currency: "gold", Time: "0s", THLevel: 8},
			9:  {Cost: 1000000, Currency: "gold", Time: "0s", THLevel: 9},
			10: {Cost: 3000000, Currency: "gold", Time: "0s", THLevel: 10},
			11: {Cost: 4000000, Currency: "gold", Time: "0s", THLevel: 11},
			12: {Cost: 5000000, Currency: "gold", Time: "0s", THLevel: 12},
			13: {Cost: 6000000, Currency: "gold", Time: "0s", THLevel: 13},
			14: {Cost: 7000000, Currency: "gold", Time: "0s", THLevel: 14},
			15: {Cost: 8000000, Currency: "gold", Time: "0s", THLevel: 15},
			16: {Cost: 9000000, Currency: "gold", Time: "0s", THLevel: 16},
		},
	},
	// ВОЕННЫЕ ЗДАНИЯ
	"army_camp": {
		Name: "Военный лагерь",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 250, Currency: "elixir", Time: "5m", THLevel: 1},
			2:  {Cost: 2500, Currency: "elixir", Time: "15m", THLevel: 2},
			3:  {Cost: 10000, Currency: "elixir", Time: "45m", THLevel: 3},
			4:  {Cost: 100000, Currency: "elixir", Time: "6h", THLevel: 4},
			5:  {Cost: 250000, Currency: "elixir", Time: "12h", THLevel: 5},
			6:  {Cost: 750000, Currency: "elixir", Time: "1d", THLevel: 7},
			7:  {Cost: 2250000, Currency: "elixir", Time: "3d", THLevel: 8},
			8:  {Cost: 6000000, Currency: "elixir", Time: "5d", THLevel: 9},
			9:  {Cost: 9000000, Currency: "elixir", Time: "7d", THLevel: 10},
			10: {Cost: 12000000, Currency: "elixir", Time: "9d", THLevel: 11},
			11: {Cost: 15000000, Currency: "elixir", Time: "11d", THLevel: 12},
			12: {Cost: 18000000, Currency: "elixir", Time: "13d", THLevel: 15},
		},
	},
	"barracks": {
		Name: "Казарма",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 200, Currency: "elixir", Time: "1m", THLevel: 1},
			2:  {Cost: 1000, Currency: "elixir", Time: "5m", THLevel: 1},
			3:  {Cost: 4000, Currency: "elixir", Time: "15m", THLevel: 2},
			4:  {Cost: 16000, Currency: "elixir", Time: "1h", THLevel: 3},
			5:  {Cost: 80000, Currency: "elixir", Time: "4h", THLevel: 4},
			6:  {Cost: 240000, Currency: "elixir", Time: "8h", THLevel: 5},
			7:  {Cost: 700000, Currency: "elixir", Time: "12h", THLevel: 6},
			8:  {Cost: 1500000, Currency: "elixir", Time: "1d", THLevel: 7},
			9:  {Cost: 2000000, Currency: "elixir", Time: "2d", THLevel: 8},
			10: {Cost: 3000000, Currency: "elixir", Time: "3d", THLevel: 9},
			11: {Cost: 4000000, Currency: "elixir", Time: "4d", THLevel: 10},
			12: {Cost: 5000000, Currency: "elixir", Time: "5d", THLevel: 11},
			13: {Cost: 7000000, Currency: "elixir", Time: "7d", THLevel: 12},
			14: {Cost: 10000000, Currency: "elixir", Time: "9d", THLevel: 13},
		},
	},
	"laboratory": {
		Name: "Лаборатория",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 25000, Currency: "elixir", Time: "6h", THLevel: 3},
			2:  {Cost: 50000, Currency: "elixir", Time: "12h", THLevel: 4},
			3:  {Cost: 100000, Currency: "elixir", Time: "1d", THLevel: 5},
			4:  {Cost: 200000, Currency: "elixir", Time: "2d", THLevel: 6},
			5:  {Cost: 400000, Currency: "elixir", Time: "3d", THLevel: 7},
			6:  {Cost: 800000, Currency: "elixir", Time: "4d", THLevel: 8},
			7:  {Cost: 1600000, Currency: "elixir", Time: "5d", THLevel: 9},
			8:  {Cost: 3200000, Currency: "elixir", Time: "6d", THLevel: 10},
			9:  {Cost: 6400000, Currency: "elixir", Time: "7d", THLevel: 11},
			10: {Cost: 8500000, Currency: "elixir", Time: "8d", THLevel: 12},
			11: {Cost: 11000000, Currency: "elixir", Time: "9d", THLevel: 13},
			12: {Cost: 14000000, Currency: "elixir", Time: "10d", THLevel: 14},
			13: {Cost: 17000000, Currency: "elixir", Time: "11d", THLevel: 15},
		},
	},
	"clan_castle": {
		Name: "Замок клана",
		Levels: map[int]BuildingLevel{
			1:  {Cost: 10000, Currency: "gold", Time: "4h", THLevel: 3},
			2:  {Cost: 100000, Currency: "gold", Time: "8h", THLevel: 4},
			3:  {Cost: 400000, Currency: "gold", Time: "1d", THLevel: 5},
			4:  {Cost: 1000000, Currency: "gold", Time: "2d", THLevel: 6},
			5:  {Cost: 2000000, Currency: "gold", Time: "3d", THLevel: 8},
			6:  {Cost: 4000000, Currency: "gold", Time: "5d", THLevel: 9},
			7:  {Cost: 6000000, Currency: "gold", Time: "7d", THLevel: 10},
			8:  {Cost: 8000000, Currency: "gold", Time: "9d", THLevel: 11},
			9:  {Cost: 10000000, Currency: "gold", Time: "11d", THLevel: 12},
			10: {Cost: 13000000, Currency: "gold", Time: "13d", THLevel: 13},
			11: {Cost: 16000000, Currency: "gold", Time: "15d", THLevel: 14},
		},
	},
}

// FormatCurrency форматирует валюту для отображения
func FormatCurrency(amount int, currency string) string {
	currencySymbols := map[string]string{
		"gold":         "🟡",
		"elixir":       "💜",
		"dark_elixir": "⚫",
	}

	symbol := currencySymbols[currency]
	if symbol == "" {
		symbol = ""
	}

	if amount >= 1000000 {
		return fmt.Sprintf("%dМ %s", amount/1000000, symbol)
	} else if amount >= 1000 {
		return fmt.Sprintf("%dК %s", amount/1000, symbol)
	}
	return fmt.Sprintf("%d %s", amount, symbol)
}

// FormatTime форматирует время для отображения
func FormatTime(timeStr string) string {
	if timeStr == "0s" {
		return "Мгновенно"
	}

	timeStr = strings.TrimSpace(timeStr)

	// Обрабатываем составное время типа "2d 12h"
	if strings.Contains(timeStr, " ") {
		parts := strings.Split(timeStr, " ")
		formatted := make([]string, 0, len(parts))
		for _, part := range parts {
			formatted = append(formatted, formatSingleTime(part))
		}
		return strings.Join(formatted, " ")
	}

	return formatSingleTime(timeStr)
}

func formatSingleTime(timeStr string) string {
	if strings.HasSuffix(timeStr, "m") {
		return strings.TrimSuffix(timeStr, "m") + " мин"
	}
	if strings.HasSuffix(timeStr, "h") {
		return strings.TrimSuffix(timeStr, "h") + " ч"
	}
	if strings.HasSuffix(timeStr, "d") {
		return strings.TrimSuffix(timeStr, "d") + " дн"
	}
	return timeStr
}

// GetBuildingInfo получает информацию о здании
func GetBuildingInfo(buildingID string) (BuildingInfo, bool) {
	info, exists := BuildingData[buildingID]
	return info, exists
}

// GetBuildingLevelInfo получает информацию об уровне здания
func GetBuildingLevelInfo(buildingID string, level int) (BuildingLevel, bool) {
	building, exists := BuildingData[buildingID]
	if !exists {
		return BuildingLevel{}, false
	}

	levelInfo, exists := building.Levels[level]
	return levelInfo, exists
}

// GetUpgradeCost возвращает стоимость улучшения здания
func GetUpgradeCost(buildingID string, level int) (int, string, bool) {
	levelInfo, exists := GetBuildingLevelInfo(buildingID, level)
	if !exists {
		return 0, "", false
	}
	return levelInfo.Cost, levelInfo.Currency, true
}

// GetUpgradeTime возвращает время улучшения здания
func GetUpgradeTime(buildingID string, level int) (string, bool) {
	levelInfo, exists := GetBuildingLevelInfo(buildingID, level)
	if !exists {
		return "", false
	}
	return levelInfo.Time, true
}

// ParseTimeString парсит строку времени в секунды
func ParseTimeString(timeStr string) int {
	if timeStr == "0s" {
		return 0
	}

	totalSeconds := 0

	// Обрабатываем составное время типа "2d 12h"
	parts := strings.Split(timeStr, " ")
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part == "" {
			continue
		}

		if strings.HasSuffix(part, "m") {
			val, err := strconv.Atoi(strings.TrimSuffix(part, "m"))
			if err == nil {
				totalSeconds += val * 60
			}
		} else if strings.HasSuffix(part, "h") {
			val, err := strconv.Atoi(strings.TrimSuffix(part, "h"))
			if err == nil {
				totalSeconds += val * 3600
			}
		} else if strings.HasSuffix(part, "d") {
			val, err := strconv.Atoi(strings.TrimSuffix(part, "d"))
			if err == nil {
				totalSeconds += val * 86400
			}
		}
	}

	return totalSeconds
}
