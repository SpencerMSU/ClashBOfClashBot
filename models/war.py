"""
Модели данных для войн - аналог Java WarToSave и AttackData
"""
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class AttackData:
    """Данные об атаке"""
    attacker_name: str
    stars: int
    destruction: float
    
    def __init__(self, attacker_name: str, stars: int, destruction: float):
        self.attacker_name = attacker_name
        self.stars = stars
        self.destruction = destruction


@dataclass
class WarToSave:
    """Данные войны для сохранения в БД"""
    end_time: str
    opponent_name: str
    team_size: int
    clan_stars: int
    opponent_stars: int
    clan_destruction: float
    opponent_destruction: float
    clan_attacks_used: int
    result: str
    is_cwl_war: bool
    total_violations: int
    attacks_by_member: Dict[str, List[Dict]] = None
    
    def __init__(self, end_time: str, opponent_name: str, team_size: int, 
                 clan_stars: int, opponent_stars: int, clan_destruction: float,
                 opponent_destruction: float, clan_attacks_used: int, result: str,
                 is_cwl_war: bool, total_violations: int, attacks_by_member: Dict = None):
        self.end_time = end_time
        self.opponent_name = opponent_name
        self.team_size = team_size
        self.clan_stars = clan_stars
        self.opponent_stars = opponent_stars
        self.clan_destruction = clan_destruction
        self.opponent_destruction = opponent_destruction
        self.clan_attacks_used = clan_attacks_used
        self.result = result
        self.is_cwl_war = is_cwl_war
        self.total_violations = total_violations
        self.attacks_by_member = attacks_by_member or {}


@dataclass
class Player:
    """Модель игрока из COC API"""
    tag: str
    name: str
    town_hall_level: int
    trophies: int
    clan: Optional[Dict] = None
    
    
@dataclass
class Clan:
    """Модель клана из COC API"""
    tag: str
    name: str
    description: str
    location: Optional[Dict] = None
    members: List[Dict] = None
    war_wins: int = 0
    war_losses: int = 0
    war_ties: int = 0