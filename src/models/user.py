"""
Модель пользователя - аналог Java User
"""
from dataclasses import dataclass


@dataclass
class User:
    """Модель пользователя бота"""
    telegram_id: int
    player_tag: str
    
    def __init__(self, telegram_id: int, player_tag: str):
        self.telegram_id = telegram_id
        self.player_tag = player_tag