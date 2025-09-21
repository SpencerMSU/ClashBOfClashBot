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
    
    # Герои
    "barbarian_king": {
        "name": "Король варваров",
        "levels": {
            1: {"cost": 10000, "currency": "dark_elixir", "time": "1h", "th_level": 7},
            2: {"cost": 12500, "currency": "dark_elixir", "time": "2h", "th_level": 7},
            3: {"cost": 15000, "currency": "dark_elixir", "time": "3h", "th_level": 7},
            4: {"cost": 17500, "currency": "dark_elixir", "time": "4h", "th_level": 7},
            5: {"cost": 20000, "currency": "dark_elixir", "time": "5h", "th_level": 7},
            10: {"cost": 37500, "currency": "dark_elixir", "time": "1d", "th_level": 8},
            15: {"cost": 62500, "currency": "dark_elixir", "time": "2d", "th_level": 9},
            20: {"cost": 87500, "currency": "dark_elixir", "time": "3d", "th_level": 10},
            25: {"cost": 112500, "currency": "dark_elixir", "time": "4d", "th_level": 11},
            30: {"cost": 137500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            40: {"cost": 187500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            50: {"cost": 237500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            60: {"cost": 287500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            70: {"cost": 337500, "currency": "dark_elixir", "time": "7d", "th_level": 16}
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
            10: {"cost": 67500, "currency": "dark_elixir", "time": "1d", "th_level": 10},
            20: {"cost": 117500, "currency": "dark_elixir", "time": "3d", "th_level": 11},
            30: {"cost": 167500, "currency": "dark_elixir", "time": "5d", "th_level": 12},
            40: {"cost": 217500, "currency": "dark_elixir", "time": "6d", "th_level": 13},
            50: {"cost": 267500, "currency": "dark_elixir", "time": "7d", "th_level": 14},
            60: {"cost": 317500, "currency": "dark_elixir", "time": "7d", "th_level": 15},
            70: {"cost": 367500, "currency": "dark_elixir", "time": "7d", "th_level": 16}
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