"""
Данные о стоимости и времени улучшения зданий в Clash of Clans
Данные актуальны на декабрь 2024
"""

# Общие данные для зданий
BUILDING_DATA = {
    # Оборонительные здания
    "archer_tower": {
        "name": "Башня лучниц",
        "levels": {
            1: {"cost": 1000, "currency": "gold", "time": "1m", "th_level": 2},
            2: {"cost": 2000, "currency": "gold", "time": "15m", "th_level": 2},
            3: {"cost": 5000, "currency": "gold", "time": "2h", "th_level": 3},
            4: {"cost": 20000, "currency": "gold", "time": "6h", "th_level": 4},
            5: {"cost": 80000, "currency": "gold", "time": "12h", "th_level": 5},
            6: {"cost": 180000, "currency": "gold", "time": "1d", "th_level": 6},
            7: {"cost": 360000, "currency": "gold", "time": "2d", "th_level": 7},
            8: {"cost": 720000, "currency": "gold", "time": "3d", "th_level": 8},
            9: {"cost": 1500000, "currency": "gold", "time": "4d", "th_level": 9},
            10: {"cost": 2200000, "currency": "gold", "time": "5d", "th_level": 10},
            11: {"cost": 3200000, "currency": "gold", "time": "6d", "th_level": 11},
            12: {"cost": 4500000, "currency": "gold", "time": "7d", "th_level": 12},
            13: {"cost": 6000000, "currency": "gold", "time": "8d", "th_level": 13},
            14: {"cost": 8500000, "currency": "gold", "time": "10d", "th_level": 14},
            15: {"cost": 12000000, "currency": "gold", "time": "12d", "th_level": 15},
            16: {"cost": 16000000, "currency": "gold", "time": "14d", "th_level": 16}
        }
    },
    
    "cannon": {
        "name": "Пушка",
        "levels": {
            1: {"cost": 250, "currency": "gold", "time": "1m", "th_level": 1},
            2: {"cost": 1000, "currency": "gold", "time": "15m", "th_level": 1},
            3: {"cost": 4000, "currency": "gold", "time": "45m", "th_level": 2},
            4: {"cost": 16000, "currency": "gold", "time": "4h", "th_level": 3},
            5: {"cost": 50000, "currency": "gold", "time": "8h", "th_level": 4},
            6: {"cost": 100000, "currency": "gold", "time": "12h", "th_level": 5},
            7: {"cost": 200000, "currency": "gold", "time": "1d", "th_level": 6},
            8: {"cost": 400000, "currency": "gold", "time": "2d", "th_level": 7},
            9: {"cost": 800000, "currency": "gold", "time": "3d", "th_level": 8},
            10: {"cost": 1600000, "currency": "gold", "time": "4d", "th_level": 9},
            11: {"cost": 2400000, "currency": "gold", "time": "5d", "th_level": 10},
            12: {"cost": 3200000, "currency": "gold", "time": "6d", "th_level": 11},
            13: {"cost": 4200000, "currency": "gold", "time": "7d", "th_level": 12},
            14: {"cost": 5600000, "currency": "gold", "time": "8d", "th_level": 13},
            15: {"cost": 7500000, "currency": "gold", "time": "10d", "th_level": 14},
            16: {"cost": 10000000, "currency": "gold", "time": "12d", "th_level": 15},
            17: {"cost": 13000000, "currency": "gold", "time": "14d", "th_level": 16}
        }
    },
    
    "mortar": {
        "name": "Мортира",
        "levels": {
            1: {"cost": 8000, "currency": "gold", "time": "5h", "th_level": 3},
            2: {"cost": 32000, "currency": "gold", "time": "8h", "th_level": 4},
            3: {"cost": 120000, "currency": "gold", "time": "12h", "th_level": 5},
            4: {"cost": 400000, "currency": "gold", "time": "1d", "th_level": 6},
            5: {"cost": 800000, "currency": "gold", "time": "2d", "th_level": 7},
            6: {"cost": 1600000, "currency": "gold", "time": "3d", "th_level": 8},
            7: {"cost": 2400000, "currency": "gold", "time": "4d", "th_level": 9},
            8: {"cost": 3200000, "currency": "gold", "time": "5d", "th_level": 10},
            9: {"cost": 4200000, "currency": "gold", "time": "7d", "th_level": 11},
            10: {"cost": 5600000, "currency": "gold", "time": "8d", "th_level": 12},
            11: {"cost": 7500000, "currency": "gold", "time": "10d", "th_level": 13},
            12: {"cost": 10000000, "currency": "gold", "time": "12d", "th_level": 14},
            13: {"cost": 13000000, "currency": "gold", "time": "14d", "th_level": 15}
        }
    },
    
    "air_defense": {
        "name": "Воздушная защита",
        "levels": {
            1: {"cost": 22500, "currency": "gold", "time": "4h", "th_level": 4},
            2: {"cost": 90000, "currency": "gold", "time": "8h", "th_level": 5},
            3: {"cost": 270000, "currency": "gold", "time": "12h", "th_level": 6},
            4: {"cost": 500000, "currency": "gold", "time": "1d", "th_level": 7},
            5: {"cost": 1000000, "currency": "gold", "time": "2d", "th_level": 8},
            6: {"cost": 1800000, "currency": "gold", "time": "3d", "th_level": 9},
            7: {"cost": 2800000, "currency": "gold", "time": "4d", "th_level": 10},
            8: {"cost": 3800000, "currency": "gold", "time": "6d", "th_level": 11},
            9: {"cost": 5000000, "currency": "gold", "time": "8d", "th_level": 12},
            10: {"cost": 6500000, "currency": "gold", "time": "10d", "th_level": 13},
            11: {"cost": 8500000, "currency": "gold", "time": "12d", "th_level": 14},
            12: {"cost": 11000000, "currency": "gold", "time": "14d", "th_level": 15}
        }
    },
    
    "wizard_tower": {
        "name": "Башня магов",
        "levels": {
            1: {"cost": 180000, "currency": "gold", "time": "12h", "th_level": 5},
            2: {"cost": 360000, "currency": "gold", "time": "1d", "th_level": 6},
            3: {"cost": 650000, "currency": "gold", "time": "2d", "th_level": 7},
            4: {"cost": 1300000, "currency": "gold", "time": "3d", "th_level": 8},
            5: {"cost": 2000000, "currency": "gold", "time": "4d", "th_level": 9},
            6: {"cost": 2600000, "currency": "gold", "time": "5d", "th_level": 10},
            7: {"cost": 3400000, "currency": "gold", "time": "6d", "th_level": 11},
            8: {"cost": 4500000, "currency": "gold", "time": "7d", "th_level": 12},
            9: {"cost": 6000000, "currency": "gold", "time": "8d", "th_level": 13},
            10: {"cost": 8000000, "currency": "gold", "time": "10d", "th_level": 14},
            11: {"cost": 10500000, "currency": "gold", "time": "12d", "th_level": 15},
            12: {"cost": 14000000, "currency": "gold", "time": "14d", "th_level": 16}
        }
    },
    
    "air_sweeper": {
        "name": "Воздушная метла",
        "levels": {
            1: {"cost": 500000, "currency": "gold", "time": "12h", "th_level": 6},
            2: {"cost": 1000000, "currency": "gold", "time": "1d", "th_level": 7},
            3: {"cost": 2000000, "currency": "gold", "time": "2d", "th_level": 8},
            4: {"cost": 3000000, "currency": "gold", "time": "3d", "th_level": 9},
            5: {"cost": 4000000, "currency": "gold", "time": "4d", "th_level": 10},
            6: {"cost": 5000000, "currency": "gold", "time": "5d", "th_level": 11},
            7: {"cost": 6000000, "currency": "gold", "time": "6d", "th_level": 12},
            8: {"cost": 7000000, "currency": "gold", "time": "7d", "th_level": 13}
        }
    },
    
    "hidden_tesla": {
        "name": "Скрытая тесла",
        "levels": {
            1: {"cost": 1000000, "currency": "gold", "time": "1d", "th_level": 7},
            2: {"cost": 1500000, "currency": "gold", "time": "2d", "th_level": 7},
            3: {"cost": 2100000, "currency": "gold", "time": "3d", "th_level": 8},
            4: {"cost": 2800000, "currency": "gold", "time": "4d", "th_level": 9},
            5: {"cost": 3600000, "currency": "gold", "time": "5d", "th_level": 10},
            6: {"cost": 4500000, "currency": "gold", "time": "6d", "th_level": 11},
            7: {"cost": 5500000, "currency": "gold", "time": "7d", "th_level": 12},
            8: {"cost": 6600000, "currency": "gold", "time": "8d", "th_level": 13},
            9: {"cost": 7800000, "currency": "gold", "time": "10d", "th_level": 14},
            10: {"cost": 9100000, "currency": "gold", "time": "12d", "th_level": 15},
            11: {"cost": 10500000, "currency": "gold", "time": "14d", "th_level": 16}
        }
    },
    
    "bomb_tower": {
        "name": "Башня-бомба",
        "levels": {
            1: {"cost": 1500000, "currency": "gold", "time": "1d", "th_level": 8},
            2: {"cost": 2000000, "currency": "gold", "time": "2d", "th_level": 8},
            3: {"cost": 2800000, "currency": "gold", "time": "3d", "th_level": 9},
            4: {"cost": 3800000, "currency": "gold", "time": "4d", "th_level": 10},
            5: {"cost": 4900000, "currency": "gold", "time": "5d", "th_level": 11},
            6: {"cost": 6100000, "currency": "gold", "time": "6d", "th_level": 12},
            7: {"cost": 7400000, "currency": "gold", "time": "7d", "th_level": 13},
            8: {"cost": 8800000, "currency": "gold", "time": "8d", "th_level": 14},
            9: {"cost": 10300000, "currency": "gold", "time": "10d", "th_level": 15}
        }
    },
    
    "x_bow": {
        "name": "Адский лук",
        "levels": {
            1: {"cost": 3000000, "currency": "gold", "time": "3d", "th_level": 9},
            2: {"cost": 4000000, "currency": "gold", "time": "4d", "th_level": 9},
            3: {"cost": 5000000, "currency": "gold", "time": "5d", "th_level": 10},
            4: {"cost": 6000000, "currency": "gold", "time": "6d", "th_level": 11},
            5: {"cost": 7000000, "currency": "gold", "time": "7d", "th_level": 12},
            6: {"cost": 8000000, "currency": "gold", "time": "8d", "th_level": 13},
            7: {"cost": 9000000, "currency": "gold", "time": "10d", "th_level": 14},
            8: {"cost": 10000000, "currency": "gold", "time": "12d", "th_level": 15},
            9: {"cost": 11000000, "currency": "gold", "time": "14d", "th_level": 16}
        }
    },
    
    "inferno_tower": {
        "name": "Башня ада",
        "levels": {
            1: {"cost": 5000000, "currency": "gold", "time": "4d", "th_level": 10},
            2: {"cost": 6000000, "currency": "gold", "time": "5d", "th_level": 10},
            3: {"cost": 7000000, "currency": "gold", "time": "6d", "th_level": 11},
            4: {"cost": 8000000, "currency": "gold", "time": "7d", "th_level": 12},
            5: {"cost": 9000000, "currency": "gold", "time": "8d", "th_level": 13},
            6: {"cost": 10000000, "currency": "gold", "time": "10d", "th_level": 14},
            7: {"cost": 11000000, "currency": "gold", "time": "12d", "th_level": 15},
            8: {"cost": 12000000, "currency": "gold", "time": "14d", "th_level": 16}
        }
    },
    
    "eagle_artillery": {
        "name": "Орлиная артиллерия",
        "levels": {
            1: {"cost": 8000000, "currency": "gold", "time": "7d", "th_level": 11},
            2: {"cost": 10000000, "currency": "gold", "time": "10d", "th_level": 12},
            3: {"cost": 12000000, "currency": "gold", "time": "12d", "th_level": 13},
            4: {"cost": 14000000, "currency": "gold", "time": "14d", "th_level": 14},
            5: {"cost": 16000000, "currency": "gold", "time": "16d", "th_level": 15},
            6: {"cost": 18000000, "currency": "gold", "time": "18d", "th_level": 16}
        }
    },
    
    "scattershot": {
        "name": "Разброс",
        "levels": {
            1: {"cost": 12000000, "currency": "gold", "time": "12d", "th_level": 13},
            2: {"cost": 14000000, "currency": "gold", "time": "14d", "th_level": 14},
            3: {"cost": 16000000, "currency": "gold", "time": "16d", "th_level": 15},
            4: {"cost": 18000000, "currency": "gold", "time": "18d", "th_level": 16}
        }
    },
    
    # Армия
    "army_camp": {
        "name": "Казармы",
        "levels": {
            1: {"cost": 250, "currency": "gold", "time": "15m", "th_level": 1},
            2: {"cost": 2500, "currency": "gold", "time": "30m", "th_level": 2},
            3: {"cost": 10000, "currency": "gold", "time": "2h", "th_level": 3},
            4: {"cost": 100000, "currency": "gold", "time": "8h", "th_level": 4},
            5: {"cost": 250000, "currency": "gold", "time": "12h", "th_level": 6},
            6: {"cost": 750000, "currency": "gold", "time": "1d", "th_level": 7},
            7: {"cost": 2250000, "currency": "gold", "time": "2d", "th_level": 8},
            8: {"cost": 6750000, "currency": "gold", "time": "3d", "th_level": 9},
            9: {"cost": 7000000, "currency": "gold", "time": "4d", "th_level": 10},
            10: {"cost": 8000000, "currency": "gold", "time": "5d", "th_level": 11},
            11: {"cost": 10000000, "currency": "gold", "time": "7d", "th_level": 12}
        }
    },
    
    "barracks": {
        "name": "Учебные казармы",
        "levels": {
            1: {"cost": 0, "currency": "gold", "time": "0s", "th_level": 1},
            2: {"cost": 1000, "currency": "gold", "time": "15m", "th_level": 1},
            3: {"cost": 4000, "currency": "gold", "time": "30m", "th_level": 2},
            4: {"cost": 25000, "currency": "gold", "time": "2h", "th_level": 3},
            5: {"cost": 150000, "currency": "gold", "time": "6h", "th_level": 4},
            6: {"cost": 500000, "currency": "gold", "time": "12h", "th_level": 6},
            7: {"cost": 1000000, "currency": "gold", "time": "1d", "th_level": 7},
            8: {"cost": 1700000, "currency": "gold", "time": "2d", "th_level": 8},
            9: {"cost": 2800000, "currency": "gold", "time": "3d", "th_level": 9},
            10: {"cost": 4600000, "currency": "gold", "time": "4d", "th_level": 10},
            11: {"cost": 6000000, "currency": "gold", "time": "5d", "th_level": 11},
            12: {"cost": 7000000, "currency": "gold", "time": "6d", "th_level": 12},
            13: {"cost": 8000000, "currency": "gold", "time": "7d", "th_level": 13},
            14: {"cost": 9000000, "currency": "gold", "time": "8d", "th_level": 14},
            15: {"cost": 10000000, "currency": "gold", "time": "10d", "th_level": 15}
        }
    },
    
    "laboratory": {
        "name": "Лаборатория",
        "levels": {
            1: {"cost": 25000, "currency": "gold", "time": "6h", "th_level": 3},
            2: {"cost": 100000, "currency": "gold", "time": "12h", "th_level": 5},
            3: {"cost": 250000, "currency": "gold", "time": "1d", "th_level": 6},
            4: {"cost": 500000, "currency": "gold", "time": "2d", "th_level": 7},
            5: {"cost": 1000000, "currency": "gold", "time": "3d", "th_level": 8},
            6: {"cost": 2000000, "currency": "gold", "time": "4d", "th_level": 9},
            7: {"cost": 3000000, "currency": "gold", "time": "5d", "th_level": 10},
            8: {"cost": 4000000, "currency": "gold", "time": "6d", "th_level": 11},
            9: {"cost": 5000000, "currency": "gold", "time": "7d", "th_level": 12},
            10: {"cost": 6000000, "currency": "gold", "time": "8d", "th_level": 13},
            11: {"cost": 7000000, "currency": "gold", "time": "10d", "th_level": 14},
            12: {"cost": 8000000, "currency": "gold", "time": "12d", "th_level": 15},
            13: {"cost": 9000000, "currency": "gold", "time": "14d", "th_level": 16}
        }
    },
    
    "spell_factory": {
        "name": "Фабрика заклинаний",
        "levels": {
            1: {"cost": 200000, "currency": "gold", "time": "5h", "th_level": 5},
            2: {"cost": 300000, "currency": "gold", "time": "8h", "th_level": 6},
            3: {"cost": 1200000, "currency": "gold", "time": "1d", "th_level": 7},
            4: {"cost": 2400000, "currency": "gold", "time": "2d", "th_level": 8},
            5: {"cost": 4800000, "currency": "gold", "time": "3d", "th_level": 9},
            6: {"cost": 6000000, "currency": "gold", "time": "5d", "th_level": 10},
            7: {"cost": 7000000, "currency": "gold", "time": "6d", "th_level": 11},
            8: {"cost": 8000000, "currency": "gold", "time": "7d", "th_level": 12},
            9: {"cost": 9000000, "currency": "gold", "time": "8d", "th_level": 13}
        }
    },
    
    "clan_castle": {
        "name": "Замок клана",
        "levels": {
            1: {"cost": 10000, "currency": "gold", "time": "4h", "th_level": 3},
            2: {"cost": 40000, "currency": "gold", "time": "8h", "th_level": 4},
            3: {"cost": 500000, "currency": "gold", "time": "12h", "th_level": 6},
            4: {"cost": 1000000, "currency": "gold", "time": "1d", "th_level": 7},
            5: {"cost": 2000000, "currency": "gold", "time": "2d", "th_level": 8},
            6: {"cost": 3000000, "currency": "gold", "time": "3d", "th_level": 9},
            7: {"cost": 4000000, "currency": "gold", "time": "4d", "th_level": 10},
            8: {"cost": 5000000, "currency": "gold", "time": "5d", "th_level": 11},
            9: {"cost": 6000000, "currency": "gold", "time": "6d", "th_level": 12},
            10: {"cost": 7000000, "currency": "gold", "time": "7d", "th_level": 13},
            11: {"cost": 8000000, "currency": "gold", "time": "8d", "th_level": 14}
        }
    },
    
    "dark_barracks": {
        "name": "Тёмные казармы",
        "levels": {
            1: {"cost": 750000, "currency": "gold", "time": "1d", "th_level": 7},
            2: {"cost": 1500000, "currency": "gold", "time": "2d", "th_level": 8},
            3: {"cost": 2500000, "currency": "gold", "time": "3d", "th_level": 9},
            4: {"cost": 3500000, "currency": "gold", "time": "4d", "th_level": 10},
            5: {"cost": 4500000, "currency": "gold", "time": "5d", "th_level": 11},
            6: {"cost": 5500000, "currency": "gold", "time": "6d", "th_level": 12},
            7: {"cost": 6500000, "currency": "gold", "time": "7d", "th_level": 13},
            8: {"cost": 7500000, "currency": "gold", "time": "8d", "th_level": 14},
            9: {"cost": 8500000, "currency": "gold", "time": "10d", "th_level": 15}
        }
    },
    
    "dark_spell_factory": {
        "name": "Фабрика тёмных заклинаний",
        "levels": {
            1: {"cost": 1000000, "currency": "gold", "time": "1d", "th_level": 8},
            2: {"cost": 2000000, "currency": "gold", "time": "2d", "th_level": 9},
            3: {"cost": 3000000, "currency": "gold", "time": "3d", "th_level": 10},
            4: {"cost": 4000000, "currency": "gold", "time": "4d", "th_level": 11},
            5: {"cost": 5000000, "currency": "gold", "time": "5d", "th_level": 12},
            6: {"cost": 6000000, "currency": "gold", "time": "6d", "th_level": 13},
            7: {"cost": 7000000, "currency": "gold", "time": "7d", "th_level": 14},
            8: {"cost": 8000000, "currency": "gold", "time": "8d", "th_level": 15}
        }
    },
    
    # Ресурсы
    "gold_mine": {
        "name": "Золотая шахта",
        "levels": {
            1: {"cost": 150, "currency": "gold", "time": "45s", "th_level": 1},
            2: {"cost": 300, "currency": "gold", "time": "5m", "th_level": 1},
            3: {"cost": 700, "currency": "gold", "time": "15m", "th_level": 2},
            4: {"cost": 1400, "currency": "gold", "time": "30m", "th_level": 2},
            5: {"cost": 3000, "currency": "gold", "time": "1h", "th_level": 3},
            6: {"cost": 7000, "currency": "gold", "time": "2h", "th_level": 3},
            7: {"cost": 14000, "currency": "gold", "time": "4h", "th_level": 4},
            8: {"cost": 28000, "currency": "gold", "time": "8h", "th_level": 4},
            9: {"cost": 56000, "currency": "gold", "time": "12h", "th_level": 5},
            10: {"cost": 84000, "currency": "gold", "time": "1d", "th_level": 5},
            11: {"cost": 168000, "currency": "gold", "time": "2d", "th_level": 6},
            12: {"cost": 336000, "currency": "gold", "time": "3d", "th_level": 7},
            13: {"cost": 672000, "currency": "gold", "time": "4d", "th_level": 8},
            14: {"cost": 1344000, "currency": "gold", "time": "5d", "th_level": 9},
            15: {"cost": 2688000, "currency": "gold", "time": "6d", "th_level": 10},
            16: {"cost": 5376000, "currency": "gold", "time": "7d", "th_level": 11}
        }
    },
    
    "elixir_collector": {
        "name": "Накопитель эликсира",
        "levels": {
            1: {"cost": 150, "currency": "elixir", "time": "45s", "th_level": 1},
            2: {"cost": 300, "currency": "elixir", "time": "5m", "th_level": 1},
            3: {"cost": 700, "currency": "elixir", "time": "15m", "th_level": 2},
            4: {"cost": 1400, "currency": "elixir", "time": "30m", "th_level": 2},
            5: {"cost": 3000, "currency": "elixir", "time": "1h", "th_level": 3},
            6: {"cost": 7000, "currency": "elixir", "time": "2h", "th_level": 3},
            7: {"cost": 14000, "currency": "elixir", "time": "4h", "th_level": 4},
            8: {"cost": 28000, "currency": "elixir", "time": "8h", "th_level": 4},
            9: {"cost": 56000, "currency": "elixir", "time": "12h", "th_level": 5},
            10: {"cost": 84000, "currency": "elixir", "time": "1d", "th_level": 5},
            11: {"cost": 168000, "currency": "elixir", "time": "2d", "th_level": 6},
            12: {"cost": 336000, "currency": "elixir", "time": "3d", "th_level": 7},
            13: {"cost": 672000, "currency": "elixir", "time": "4d", "th_level": 8},
            14: {"cost": 1344000, "currency": "elixir", "time": "5d", "th_level": 9},
            15: {"cost": 2688000, "currency": "elixir", "time": "6d", "th_level": 10},
            16: {"cost": 5376000, "currency": "elixir", "time": "7d", "th_level": 11}
        }
    },
    
    "dark_elixir_drill": {
        "name": "Бур тёмного эликсира",
        "levels": {
            1: {"cost": 1000000, "currency": "gold", "time": "1d", "th_level": 7},
            2: {"cost": 1500000, "currency": "gold", "time": "2d", "th_level": 7},
            3: {"cost": 2000000, "currency": "gold", "time": "3d", "th_level": 8},
            4: {"cost": 3000000, "currency": "gold", "time": "4d", "th_level": 9},
            5: {"cost": 4000000, "currency": "gold", "time": "5d", "th_level": 10},
            6: {"cost": 5000000, "currency": "gold", "time": "6d", "th_level": 11},
            7: {"cost": 6000000, "currency": "gold", "time": "7d", "th_level": 12},
            8: {"cost": 7000000, "currency": "gold", "time": "8d", "th_level": 13},
            9: {"cost": 8000000, "currency": "gold", "time": "10d", "th_level": 14}
        }
    },
    
    "gold_storage": {
        "name": "Хранилище золота",
        "levels": {
            1: {"cost": 300, "currency": "gold", "time": "10s", "th_level": 1},
            2: {"cost": 750, "currency": "gold", "time": "15m", "th_level": 1},
            3: {"cost": 1500, "currency": "gold", "time": "30m", "th_level": 2},
            4: {"cost": 3000, "currency": "gold", "time": "1h", "th_level": 3},
            5: {"cost": 6000, "currency": "gold", "time": "2h", "th_level": 3},
            6: {"cost": 12000, "currency": "gold", "time": "4h", "th_level": 4},
            7: {"cost": 25000, "currency": "gold", "time": "8h", "th_level": 4},
            8: {"cost": 50000, "currency": "gold", "time": "12h", "th_level": 5},
            9: {"cost": 100000, "currency": "gold", "time": "1d", "th_level": 6},
            10: {"cost": 250000, "currency": "gold", "time": "2d", "th_level": 7},
            11: {"cost": 500000, "currency": "gold", "time": "3d", "th_level": 8},
            12: {"cost": 1000000, "currency": "gold", "time": "4d", "th_level": 9},
            13: {"cost": 2000000, "currency": "gold", "time": "5d", "th_level": 10},
            14: {"cost": 4000000, "currency": "gold", "time": "6d", "th_level": 11},
            15: {"cost": 6000000, "currency": "gold", "time": "7d", "th_level": 12},
            16: {"cost": 8000000, "currency": "gold", "time": "8d", "th_level": 13}
        }
    },
    
    "elixir_storage": {
        "name": "Хранилище эликсира",
        "levels": {
            1: {"cost": 300, "currency": "elixir", "time": "10s", "th_level": 1},
            2: {"cost": 750, "currency": "elixir", "time": "15m", "th_level": 1},
            3: {"cost": 1500, "currency": "elixir", "time": "30m", "th_level": 2},
            4: {"cost": 3000, "currency": "elixir", "time": "1h", "th_level": 3},
            5: {"cost": 6000, "currency": "elixir", "time": "2h", "th_level": 3},
            6: {"cost": 12000, "currency": "elixir", "time": "4h", "th_level": 4},
            7: {"cost": 25000, "currency": "elixir", "time": "8h", "th_level": 4},
            8: {"cost": 50000, "currency": "elixir", "time": "12h", "th_level": 5},
            9: {"cost": 100000, "currency": "elixir", "time": "1d", "th_level": 6},
            10: {"cost": 250000, "currency": "elixir", "time": "2d", "th_level": 7},
            11: {"cost": 500000, "currency": "elixir", "time": "3d", "th_level": 8},
            12: {"cost": 1000000, "currency": "elixir", "time": "4d", "th_level": 9},
            13: {"cost": 2000000, "currency": "elixir", "time": "5d", "th_level": 10},
            14: {"cost": 4000000, "currency": "elixir", "time": "6d", "th_level": 11},
            15: {"cost": 6000000, "currency": "elixir", "time": "7d", "th_level": 12},
            16: {"cost": 8000000, "currency": "elixir", "time": "8d", "th_level": 13}
        }
    },
    
    "dark_elixir_storage": {
        "name": "Хранилище тёмного эликсира",
        "levels": {
            1: {"cost": 600000, "currency": "gold", "time": "12h", "th_level": 7},
            2: {"cost": 1200000, "currency": "gold", "time": "1d", "th_level": 7},
            3: {"cost": 1800000, "currency": "gold", "time": "2d", "th_level": 8},
            4: {"cost": 2400000, "currency": "gold", "time": "3d", "th_level": 9},
            5: {"cost": 3000000, "currency": "gold", "time": "4d", "th_level": 10},
            6: {"cost": 3600000, "currency": "gold", "time": "5d", "th_level": 11},
            7: {"cost": 4200000, "currency": "gold", "time": "6d", "th_level": 12},
            8: {"cost": 4800000, "currency": "gold", "time": "7d", "th_level": 13},
            9: {"cost": 5400000, "currency": "gold", "time": "8d", "th_level": 14},
            10: {"cost": 6000000, "currency": "gold", "time": "10d", "th_level": 15}
        }
    },
    
    # Герои
    "barbarian_king": {
        "name": "Король варваров",
        "levels": {
            1: {"cost": 10000, "currency": "dark_elixir", "time": "1h", "th_level": 7},
            2: {"cost": 12500, "currency": "dark_elixir", "time": "2h", "th_level": 7},
            3: {"cost": 15000, "currency": "dark_elixir", "time": "3h", "th_level": 7},
            4: {"cost": 17500, "currency": "dark_elixir", "time": "4h", "th_level": 7},
            5: {"cost": 20000, "currency": "dark_elixir", "time": "5h", "th_level": 7},
            6: {"cost": 22500, "currency": "dark_elixir", "time": "6h", "th_level": 7},
            7: {"cost": 25000, "currency": "dark_elixir", "time": "8h", "th_level": 7},
            8: {"cost": 27500, "currency": "dark_elixir", "time": "10h", "th_level": 7},
            9: {"cost": 30000, "currency": "dark_elixir", "time": "12h", "th_level": 7},
            10: {"cost": 37500, "currency": "dark_elixir", "time": "1d", "th_level": 8},
            11: {"cost": 40000, "currency": "dark_elixir", "time": "1d", "th_level": 8},
            12: {"cost": 42500, "currency": "dark_elixir", "time": "1d", "th_level": 8},
            13: {"cost": 45000, "currency": "dark_elixir", "time": "1d", "th_level": 8},
            14: {"cost": 47500, "currency": "dark_elixir", "time": "1d", "th_level": 8},
            15: {"cost": 62500, "currency": "dark_elixir", "time": "2d", "th_level": 9},
            16: {"cost": 65000, "currency": "dark_elixir", "time": "2d", "th_level": 9},
            17: {"cost": 67500, "currency": "dark_elixir", "time": "2d", "th_level": 9},
            18: {"cost": 70000, "currency": "dark_elixir", "time": "2d", "th_level": 9},
            19: {"cost": 72500, "currency": "dark_elixir", "time": "2d", "th_level": 9},
            20: {"cost": 87500, "currency": "dark_elixir", "time": "3d", "th_level": 10},
            21: {"cost": 90000, "currency": "dark_elixir", "time": "3d", "th_level": 10},
            22: {"cost": 92500, "currency": "dark_elixir", "time": "3d", "th_level": 10},
            23: {"cost": 95000, "currency": "dark_elixir", "time": "3d", "th_level": 10},
            24: {"cost": 97500, "currency": "dark_elixir", "time": "3d", "th_level": 10},
            25: {"cost": 112500, "currency": "dark_elixir", "time": "4d", "th_level": 11},
            26: {"cost": 115000, "currency": "dark_elixir", "time": "4d", "th_level": 11},
            27: {"cost": 117500, "currency": "dark_elixir", "time": "4d", "th_level": 11},
            28: {"cost": 120000, "currency": "dark_elixir", "time": "4d", "th_level": 11},
            29: {"cost": 122500, "currency": "dark_elixir", "time": "4d", "th_level": 11},
            30: {"cost": 137500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            31: {"cost": 140000, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            32: {"cost": 142500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            33: {"cost": 145000, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            34: {"cost": 147500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            35: {"cost": 150000, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            36: {"cost": 152500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            37: {"cost": 155000, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            38: {"cost": 157500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            39: {"cost": 160000, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            40: {"cost": 187500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            41: {"cost": 190000, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            42: {"cost": 192500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            43: {"cost": 195000, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            44: {"cost": 197500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            45: {"cost": 200000, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            46: {"cost": 202500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            47: {"cost": 205000, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            48: {"cost": 207500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            49: {"cost": 210000, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            50: {"cost": 237500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            51: {"cost": 240000, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            52: {"cost": 242500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            53: {"cost": 245000, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            54: {"cost": 247500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            55: {"cost": 250000, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            56: {"cost": 252500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            57: {"cost": 255000, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            58: {"cost": 257500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            59: {"cost": 260000, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            60: {"cost": 287500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            61: {"cost": 290000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            62: {"cost": 292500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            63: {"cost": 295000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            64: {"cost": 297500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            65: {"cost": 300000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            66: {"cost": 302500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            67: {"cost": 305000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            68: {"cost": 307500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            69: {"cost": 310000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            70: {"cost": 337500, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            71: {"cost": 340000, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            72: {"cost": 342500, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            73: {"cost": 345000, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            74: {"cost": 347500, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            75: {"cost": 350000, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            76: {"cost": 352500, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            77: {"cost": 355000, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            78: {"cost": 357500, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            79: {"cost": 360000, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            80: {"cost": 362500, "currency": "dark_elixir", "time": "7d", "th_level": 16}
        }
    },
    
    "archer_queen": {
        "name": "Королева лучниц",
        "levels": {
            1: {"cost": 40000, "currency": "dark_elixir", "time": "1h", "th_level": 9},
            2: {"cost": 42500, "currency": "dark_elixir", "time": "2h", "th_level": 9},
            3: {"cost": 45000, "currency": "dark_elixir", "time": "3h", "th_level": 9},
            4: {"cost": 47500, "currency": "dark_elixir", "time": "4h", "th_level": 9},
            5: {"cost": 50000, "currency": "dark_elixir", "time": "5h", "th_level": 9},
            6: {"cost": 52500, "currency": "dark_elixir", "time": "6h", "th_level": 9},
            7: {"cost": 55000, "currency": "dark_elixir", "time": "8h", "th_level": 9},
            8: {"cost": 57500, "currency": "dark_elixir", "time": "10h", "th_level": 9},
            9: {"cost": 60000, "currency": "dark_elixir", "time": "12h", "th_level": 9},
            10: {"cost": 67500, "currency": "dark_elixir", "time": "1d", "th_level": 10},
            11: {"cost": 70000, "currency": "dark_elixir", "time": "1d", "th_level": 10},
            12: {"cost": 72500, "currency": "dark_elixir", "time": "1d", "th_level": 10},
            13: {"cost": 75000, "currency": "dark_elixir", "time": "1d", "th_level": 10},
            14: {"cost": 77500, "currency": "dark_elixir", "time": "1d", "th_level": 10},
            15: {"cost": 92500, "currency": "dark_elixir", "time": "2d", "th_level": 11},
            16: {"cost": 95000, "currency": "dark_elixir", "time": "2d", "th_level": 11},
            17: {"cost": 97500, "currency": "dark_elixir", "time": "2d", "th_level": 11},
            18: {"cost": 100000, "currency": "dark_elixir", "time": "2d", "th_level": 11},
            19: {"cost": 102500, "currency": "dark_elixir", "time": "2d", "th_level": 11},
            20: {"cost": 117500, "currency": "dark_elixir", "time": "3d", "th_level": 11},
            21: {"cost": 120000, "currency": "dark_elixir", "time": "3d", "th_level": 11},
            22: {"cost": 122500, "currency": "dark_elixir", "time": "3d", "th_level": 11},
            23: {"cost": 125000, "currency": "dark_elixir", "time": "3d", "th_level": 11},
            24: {"cost": 127500, "currency": "dark_elixir", "time": "3d", "th_level": 11},
            25: {"cost": 142500, "currency": "dark_elixir", "time": "4d", "th_level": 12},
            26: {"cost": 145000, "currency": "dark_elixir", "time": "4d", "th_level": 12},
            27: {"cost": 147500, "currency": "dark_elixir", "time": "4d", "th_level": 12},
            28: {"cost": 150000, "currency": "dark_elixir", "time": "4d", "th_level": 12},
            29: {"cost": 152500, "currency": "dark_elixir", "time": "4d", "th_level": 12},
            30: {"cost": 167500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            31: {"cost": 170000, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            32: {"cost": 172500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            33: {"cost": 175000, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            34: {"cost": 177500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            35: {"cost": 180000, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            36: {"cost": 182500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            37: {"cost": 185000, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            38: {"cost": 187500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            39: {"cost": 190000, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            40: {"cost": 217500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            41: {"cost": 220000, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            42: {"cost": 222500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            43: {"cost": 225000, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            44: {"cost": 227500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            45: {"cost": 230000, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            46: {"cost": 232500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            47: {"cost": 235000, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            48: {"cost": 237500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            49: {"cost": 240000, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            50: {"cost": 267500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            51: {"cost": 270000, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            52: {"cost": 272500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            53: {"cost": 275000, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            54: {"cost": 277500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            55: {"cost": 280000, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            56: {"cost": 282500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            57: {"cost": 285000, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            58: {"cost": 287500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            59: {"cost": 290000, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            60: {"cost": 317500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            61: {"cost": 320000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            62: {"cost": 322500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            63: {"cost": 325000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            64: {"cost": 327500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            65: {"cost": 330000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            66: {"cost": 332500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            67: {"cost": 335000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            68: {"cost": 337500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            69: {"cost": 340000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            70: {"cost": 367500, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            71: {"cost": 370000, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            72: {"cost": 372500, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            73: {"cost": 375000, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            74: {"cost": 377500, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            75: {"cost": 380000, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            76: {"cost": 382500, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            77: {"cost": 385000, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            78: {"cost": 387500, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            79: {"cost": 390000, "currency": "dark_elixir", "time": "7d", "th_level": 16},
            80: {"cost": 392500, "currency": "dark_elixir", "time": "7d", "th_level": 16}
        }
    },
    
    "grand_warden": {
        "name": "Великий хранитель",
        "levels": {
            1: {"cost": 6000000, "currency": "elixir", "time": "2d", "th_level": 11},
            2: {"cost": 6200000, "currency": "elixir", "time": "2d", "th_level": 11},
            3: {"cost": 6400000, "currency": "elixir", "time": "2d", "th_level": 11},
            4: {"cost": 6600000, "currency": "elixir", "time": "2d", "th_level": 11},
            5: {"cost": 6800000, "currency": "elixir", "time": "3d", "th_level": 11},
            6: {"cost": 7000000, "currency": "elixir", "time": "3d", "th_level": 11},
            7: {"cost": 7200000, "currency": "elixir", "time": "3d", "th_level": 11},
            8: {"cost": 7400000, "currency": "elixir", "time": "3d", "th_level": 11},
            9: {"cost": 7600000, "currency": "elixir", "time": "3d", "th_level": 11},
            10: {"cost": 7800000, "currency": "elixir", "time": "4d", "th_level": 11},
            11: {"cost": 8000000, "currency": "elixir", "time": "4d", "th_level": 12},
            12: {"cost": 8200000, "currency": "elixir", "time": "4d", "th_level": 12},
            13: {"cost": 8400000, "currency": "elixir", "time": "4d", "th_level": 12},
            14: {"cost": 8600000, "currency": "elixir", "time": "4d", "th_level": 12},
            15: {"cost": 8800000, "currency": "elixir", "time": "5d", "th_level": 12},
            16: {"cost": 9000000, "currency": "elixir", "time": "5d", "th_level": 12},
            17: {"cost": 9200000, "currency": "elixir", "time": "5d", "th_level": 12},
            18: {"cost": 9400000, "currency": "elixir", "time": "5d", "th_level": 12},
            19: {"cost": 9600000, "currency": "elixir", "time": "5d", "th_level": 12},
            20: {"cost": 9800000, "currency": "elixir", "time": "6d", "th_level": 12},
            21: {"cost": 10000000, "currency": "elixir", "time": "6d", "th_level": 13},
            22: {"cost": 10200000, "currency": "elixir", "time": "6d", "th_level": 13},
            23: {"cost": 10400000, "currency": "elixir", "time": "6d", "th_level": 13},
            24: {"cost": 10600000, "currency": "elixir", "time": "6d", "th_level": 13},
            25: {"cost": 10800000, "currency": "elixir", "time": "7d", "th_level": 13},
            26: {"cost": 11000000, "currency": "elixir", "time": "7d", "th_level": 13},
            27: {"cost": 11200000, "currency": "elixir", "time": "7d", "th_level": 13},
            28: {"cost": 11400000, "currency": "elixir", "time": "7d", "th_level": 13},
            29: {"cost": 11600000, "currency": "elixir", "time": "7d", "th_level": 13},
            30: {"cost": 11800000, "currency": "elixir", "time": "7d", "th_level": 13},
            31: {"cost": 12000000, "currency": "elixir", "time": "7d", "th_level": 14},
            32: {"cost": 12200000, "currency": "elixir", "time": "7d", "th_level": 14},
            33: {"cost": 12400000, "currency": "elixir", "time": "7d", "th_level": 14},
            34: {"cost": 12600000, "currency": "elixir", "time": "7d", "th_level": 14},
            35: {"cost": 12800000, "currency": "elixir", "time": "7d", "th_level": 14},
            36: {"cost": 13000000, "currency": "elixir", "time": "7d", "th_level": 14},
            37: {"cost": 13200000, "currency": "elixir", "time": "7d", "th_level": 14},
            38: {"cost": 13400000, "currency": "elixir", "time": "7d", "th_level": 14},
            39: {"cost": 13600000, "currency": "elixir", "time": "7d", "th_level": 14},
            40: {"cost": 13800000, "currency": "elixir", "time": "7d", "th_level": 14},
            41: {"cost": 14000000, "currency": "elixir", "time": "7d", "th_level": 15},
            42: {"cost": 14200000, "currency": "elixir", "time": "7d", "th_level": 15},
            43: {"cost": 14400000, "currency": "elixir", "time": "7d", "th_level": 15},
            44: {"cost": 14600000, "currency": "elixir", "time": "7d", "th_level": 15},
            45: {"cost": 14800000, "currency": "elixir", "time": "7d", "th_level": 15},
            46: {"cost": 15000000, "currency": "elixir", "time": "7d", "th_level": 15},
            47: {"cost": 15200000, "currency": "elixir", "time": "7d", "th_level": 15},
            48: {"cost": 15400000, "currency": "elixir", "time": "7d", "th_level": 15},
            49: {"cost": 15600000, "currency": "elixir", "time": "7d", "th_level": 15},
            50: {"cost": 15800000, "currency": "elixir", "time": "7d", "th_level": 15},
            51: {"cost": 16000000, "currency": "elixir", "time": "7d", "th_level": 16},
            52: {"cost": 16200000, "currency": "elixir", "time": "7d", "th_level": 16},
            53: {"cost": 16400000, "currency": "elixir", "time": "7d", "th_level": 16},
            54: {"cost": 16600000, "currency": "elixir", "time": "7d", "th_level": 16},
            55: {"cost": 16800000, "currency": "elixir", "time": "7d", "th_level": 16}
        }
    },
    
    "royal_champion": {
        "name": "Королевский чемпион",
        "levels": {
            1: {"cost": 120000, "currency": "dark_elixir", "time": "3d", "th_level": 13},
            2: {"cost": 125000, "currency": "dark_elixir", "time": "3d", "th_level": 13},
            3: {"cost": 130000, "currency": "dark_elixir", "time": "3d", "th_level": 13},
            4: {"cost": 135000, "currency": "dark_elixir", "time": "3d", "th_level": 13},
            5: {"cost": 140000, "currency": "dark_elixir", "time": "4d", "th_level": 13},
            6: {"cost": 145000, "currency": "dark_elixir", "time": "4d", "th_level": 13},
            7: {"cost": 150000, "currency": "dark_elixir", "time": "4d", "th_level": 13},
            8: {"cost": 155000, "currency": "dark_elixir", "time": "4d", "th_level": 13},
            9: {"cost": 160000, "currency": "dark_elixir", "time": "4d", "th_level": 13},
            10: {"cost": 165000, "currency": "dark_elixir", "time": "5d", "th_level": 13},
            11: {"cost": 170000, "currency": "dark_elixir", "time": "5d", "th_level": 14},
            12: {"cost": 175000, "currency": "dark_elixir", "time": "5d", "th_level": 14},
            13: {"cost": 180000, "currency": "dark_elixir", "time": "5d", "th_level": 14},
            14: {"cost": 185000, "currency": "dark_elixir", "time": "5d", "th_level": 14},
            15: {"cost": 190000, "currency": "dark_elixir", "time": "6d", "th_level": 14},
            16: {"cost": 195000, "currency": "dark_elixir", "time": "6d", "th_level": 14},
            17: {"cost": 200000, "currency": "dark_elixir", "time": "6d", "th_level": 14},
            18: {"cost": 205000, "currency": "dark_elixir", "time": "6d", "th_level": 14},
            19: {"cost": 210000, "currency": "dark_elixir", "time": "6d", "th_level": 14},
            20: {"cost": 215000, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            21: {"cost": 220000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            22: {"cost": 225000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            23: {"cost": 230000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            24: {"cost": 235000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            25: {"cost": 240000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            26: {"cost": 245000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            27: {"cost": 250000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            28: {"cost": 255000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            29: {"cost": 260000, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            30: {"cost": 265000, "currency": "dark_elixir", "time": "7d", "th_level": 15}
        }
    },
    
    # Стены
    "walls": {
        "name": "Стены",
        "levels": {
            1: {"cost": 50, "currency": "gold", "time": "0s", "th_level": 2},
            2: {"cost": 1000, "currency": "gold", "time": "0s", "th_level": 2},
            3: {"cost": 5000, "currency": "gold", "time": "0s", "th_level": 3},
            4: {"cost": 10000, "currency": "gold", "time": "0s", "th_level": 4},
            5: {"cost": 30000, "currency": "gold", "time": "0s", "th_level": 5},
            6: {"cost": 75000, "currency": "gold", "time": "0s", "th_level": 6},
            7: {"cost": 200000, "currency": "gold", "time": "0s", "th_level": 7},
            8: {"cost": 500000, "currency": "gold", "time": "0s", "th_level": 8},
            9: {"cost": 1000000, "currency": "gold", "time": "0s", "th_level": 9},
            10: {"cost": 3000000, "currency": "gold", "time": "0s", "th_level": 10},
            11: {"cost": 4000000, "currency": "gold", "time": "0s", "th_level": 11},
            12: {"cost": 5000000, "currency": "gold", "time": "0s", "th_level": 12},
            13: {"cost": 6000000, "currency": "gold", "time": "0s", "th_level": 13},
            14: {"cost": 7000000, "currency": "gold", "time": "0s", "th_level": 14},
            15: {"cost": 8000000, "currency": "gold", "time": "0s", "th_level": 15},
            16: {"cost": 9000000, "currency": "gold", "time": "0s", "th_level": 16}
        }
    },
    
    # Деревня строителя
    "builder_hall": {
        "name": "Зал строителя",
        "levels": {
            1: {"cost": 0, "currency": "gold", "time": "0s", "th_level": 4},
            2: {"cost": 100000, "currency": "gold", "time": "1h", "th_level": 4},
            3: {"cost": 250000, "currency": "gold", "time": "4h", "th_level": 4},
            4: {"cost": 500000, "currency": "gold", "time": "12h", "th_level": 4},
            5: {"cost": 1000000, "currency": "gold", "time": "1d", "th_level": 4},
            6: {"cost": 1500000, "currency": "gold", "time": "2d", "th_level": 4},
            7: {"cost": 2000000, "currency": "gold", "time": "3d", "th_level": 4},
            8: {"cost": 2500000, "currency": "gold", "time": "4d", "th_level": 4},
            9: {"cost": 3000000, "currency": "gold", "time": "5d", "th_level": 4},
            10: {"cost": 4000000, "currency": "gold", "time": "6d", "th_level": 4}
        }
    },
    
    "builder_barracks": {
        "name": "Казармы БД",
        "levels": {
            1: {"cost": 100000, "currency": "gold", "time": "30m", "th_level": 4},
            2: {"cost": 150000, "currency": "gold", "time": "1h", "th_level": 4},
            3: {"cost": 200000, "currency": "gold", "time": "2h", "th_level": 4},
            4: {"cost": 400000, "currency": "gold", "time": "4h", "th_level": 4},
            5: {"cost": 800000, "currency": "gold", "time": "8h", "th_level": 4},
            6: {"cost": 1200000, "currency": "gold", "time": "12h", "th_level": 4},
            7: {"cost": 1600000, "currency": "gold", "time": "1d", "th_level": 4},
            8: {"cost": 2000000, "currency": "gold", "time": "2d", "th_level": 4},
            9: {"cost": 2400000, "currency": "gold", "time": "3d", "th_level": 4},
            10: {"cost": 2800000, "currency": "gold", "time": "4d", "th_level": 4}
        }
    },
    
    "builder_archer_tower": {
        "name": "Башня лучниц БД",
        "levels": {
            1: {"cost": 50000, "currency": "gold", "time": "15m", "th_level": 4},
            2: {"cost": 100000, "currency": "gold", "time": "30m", "th_level": 4},
            3: {"cost": 150000, "currency": "gold", "time": "1h", "th_level": 4},
            4: {"cost": 300000, "currency": "gold", "time": "2h", "th_level": 4},
            5: {"cost": 600000, "currency": "gold", "time": "4h", "th_level": 4},
            6: {"cost": 900000, "currency": "gold", "time": "8h", "th_level": 4},
            7: {"cost": 1200000, "currency": "gold", "time": "12h", "th_level": 4},
            8: {"cost": 1500000, "currency": "gold", "time": "1d", "th_level": 4},
            9: {"cost": 1800000, "currency": "gold", "time": "2d", "th_level": 4},
            10: {"cost": 2100000, "currency": "gold", "time": "3d", "th_level": 4}
        }
    },
    
    "builder_cannon": {
        "name": "Пушка БД",
        "levels": {
            1: {"cost": 25000, "currency": "gold", "time": "10m", "th_level": 4},
            2: {"cost": 75000, "currency": "gold", "time": "20m", "th_level": 4},
            3: {"cost": 125000, "currency": "gold", "time": "40m", "th_level": 4},
            4: {"cost": 250000, "currency": "gold", "time": "1h", "th_level": 4},
            5: {"cost": 500000, "currency": "gold", "time": "2h", "th_level": 4},
            6: {"cost": 750000, "currency": "gold", "time": "4h", "th_level": 4},
            7: {"cost": 1000000, "currency": "gold", "time": "8h", "th_level": 4},
            8: {"cost": 1250000, "currency": "gold", "time": "12h", "th_level": 4},
            9: {"cost": 1500000, "currency": "gold", "time": "1d", "th_level": 4},
            10: {"cost": 1750000, "currency": "gold", "time": "2d", "th_level": 4}
        }
    },
    
    "builder_firecrackers": {
        "name": "Печь БД",
        "levels": {
            1: {"cost": 100000, "currency": "gold", "time": "30m", "th_level": 4},
            2: {"cost": 200000, "currency": "gold", "time": "1h", "th_level": 4},
            3: {"cost": 300000, "currency": "gold", "time": "2h", "th_level": 4},
            4: {"cost": 600000, "currency": "gold", "time": "4h", "th_level": 4},
            5: {"cost": 900000, "currency": "gold", "time": "8h", "th_level": 4},
            6: {"cost": 1200000, "currency": "gold", "time": "12h", "th_level": 4},
            7: {"cost": 1500000, "currency": "gold", "time": "1d", "th_level": 4},
            8: {"cost": 1800000, "currency": "gold", "time": "2d", "th_level": 4},
            9: {"cost": 2100000, "currency": "gold", "time": "3d", "th_level": 4}
        }
    },
    
    "builder_tesla": {
        "name": "Тесла БД",
        "levels": {
            1: {"cost": 300000, "currency": "gold", "time": "2h", "th_level": 4},
            2: {"cost": 450000, "currency": "gold", "time": "4h", "th_level": 4},
            3: {"cost": 600000, "currency": "gold", "time": "6h", "th_level": 4},
            4: {"cost": 900000, "currency": "gold", "time": "8h", "th_level": 4},
            5: {"cost": 1200000, "currency": "gold", "time": "12h", "th_level": 4},
            6: {"cost": 1500000, "currency": "gold", "time": "1d", "th_level": 4},
            7: {"cost": 1800000, "currency": "gold", "time": "2d", "th_level": 4},
            8: {"cost": 2100000, "currency": "gold", "time": "3d", "th_level": 4},
            9: {"cost": 2400000, "currency": "gold", "time": "4d", "th_level": 4}
        }
    },
    
    "giant_cannon": {
        "name": "Гигантская пушка БД",
        "levels": {
            1: {"cost": 1000000, "currency": "gold", "time": "1d", "th_level": 4},
            2: {"cost": 1200000, "currency": "gold", "time": "2d", "th_level": 4},
            3: {"cost": 1400000, "currency": "gold", "time": "3d", "th_level": 4},
            4: {"cost": 1600000, "currency": "gold", "time": "4d", "th_level": 4},
            5: {"cost": 1800000, "currency": "gold", "time": "5d", "th_level": 4},
            6: {"cost": 2000000, "currency": "gold", "time": "6d", "th_level": 4},
            7: {"cost": 2200000, "currency": "gold", "time": "7d", "th_level": 4},
            8: {"cost": 2400000, "currency": "gold", "time": "8d", "th_level": 4},
            9: {"cost": 2600000, "currency": "gold", "time": "9d", "th_level": 4},
            10: {"cost": 2800000, "currency": "gold", "time": "10d", "th_level": 4}
        }
    },
    
    "mega_tesla": {
        "name": "Мега тесла БД",
        "levels": {
            1: {"cost": 2000000, "currency": "gold", "time": "2d", "th_level": 4},
            2: {"cost": 2400000, "currency": "gold", "time": "3d", "th_level": 4},
            3: {"cost": 2800000, "currency": "gold", "time": "4d", "th_level": 4},
            4: {"cost": 3200000, "currency": "gold", "time": "5d", "th_level": 4},
            5: {"cost": 3600000, "currency": "gold", "time": "6d", "th_level": 4},
            6: {"cost": 4000000, "currency": "gold", "time": "7d", "th_level": 4},
            7: {"cost": 4400000, "currency": "gold", "time": "8d", "th_level": 4},
            8: {"cost": 4800000, "currency": "gold", "time": "9d", "th_level": 4},
            9: {"cost": 5200000, "currency": "gold", "time": "10d", "th_level": 4},
            10: {"cost": 5600000, "currency": "gold", "time": "11d", "th_level": 4}
        }
    }
}

def format_currency(amount: int, currency: str) -> str:
    """Форматирование валюты"""
    currency_symbols = {
        "gold": "🟡",
        "elixir": "💜", 
        "dark_elixir": "⚫"
    }
    
    if amount >= 1000000:
        return f"{amount // 1000000}М {currency_symbols.get(currency, '')}"
    elif amount >= 1000:
        return f"{amount // 1000}К {currency_symbols.get(currency, '')}"
    else:
        return f"{amount} {currency_symbols.get(currency, '')}"

def format_time(time_str: str) -> str:
    """Форматирование времени"""
    if time_str == "0s":
        return "Мгновенно"
    elif time_str.endswith("m"):
        return time_str.replace("m", " мин")
    elif time_str.endswith("h"):
        return time_str.replace("h", " ч")
    elif time_str.endswith("d"):
        return time_str.replace("d", " дн")
    else:
        return time_str

def get_building_info(building_id: str) -> dict:
    """Получение информации о здании"""
    return BUILDING_DATA.get(building_id, {})