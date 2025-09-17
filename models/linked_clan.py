"""
Модель данных для привязанных кланов
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LinkedClan:
    """Привязанный клан пользователя"""
    id: Optional[int]
    telegram_id: int
    clan_tag: str
    clan_name: str
    slot_number: int  # номер слота (1-5)
    created_at: str
    
    def __init__(self, telegram_id: int, clan_tag: str, clan_name: str, 
                 slot_number: int, created_at: str = None, id: int = None):
        self.id = id
        self.telegram_id = telegram_id
        self.clan_tag = clan_tag
        self.clan_name = clan_name
        self.slot_number = slot_number
        self.created_at = created_at or datetime.now().isoformat()