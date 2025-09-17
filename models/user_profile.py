"""
Модель профиля пользователя для многопрофильной системы
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserProfile:
    """Модель профиля пользователя"""
    telegram_id: int
    player_tag: str
    profile_name: Optional[str] = None
    is_primary: bool = False
    created_at: Optional[str] = None
    profile_id: Optional[int] = None
    
    def __init__(self, telegram_id: int, player_tag: str, profile_name: str = None, 
                 is_primary: bool = False, created_at: str = None, profile_id: int = None):
        self.telegram_id = telegram_id
        self.player_tag = player_tag
        self.profile_name = profile_name
        self.is_primary = is_primary
        self.created_at = created_at or datetime.now().isoformat()
        self.profile_id = profile_id