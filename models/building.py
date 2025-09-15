"""
Модели данных для зданий и отслеживания улучшений
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class BuildingSnapshot:
    """Снимок состояния зданий игрока"""
    player_tag: str
    snapshot_time: str
    buildings_data: str  # JSON строка с данными о зданиях
    
    def __init__(self, player_tag: str, snapshot_time: str, buildings_data: str):
        self.player_tag = player_tag
        self.snapshot_time = snapshot_time
        self.buildings_data = buildings_data


@dataclass
class BuildingUpgrade:
    """Информация об улучшении здания"""
    building_name: str
    old_level: int
    new_level: int
    
    def __init__(self, building_name: str, old_level: int, new_level: int):
        self.building_name = building_name
        self.old_level = old_level
        self.new_level = new_level


@dataclass
class BuildingTracker:
    """Настройки отслеживания улучшений для пользователя"""
    telegram_id: int
    player_tag: str
    is_active: bool
    created_at: str
    last_check: Optional[str] = None
    
    def __init__(self, telegram_id: int, player_tag: str, is_active: bool, 
                 created_at: str, last_check: Optional[str] = None):
        self.telegram_id = telegram_id
        self.player_tag = player_tag
        self.is_active = is_active
        self.created_at = created_at
        self.last_check = last_check