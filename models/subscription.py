"""
Модель подписки пользователя
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Subscription:
    """Модель подписки пользователя"""
    telegram_id: int
    subscription_type: str  # "1month", "3months", "6months", "1year"
    start_date: datetime
    end_date: datetime
    is_active: bool
    payment_id: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "RUB"
    
    def __init__(self, telegram_id: int, subscription_type: str, start_date: datetime, 
                 end_date: datetime, is_active: bool = True, payment_id: str = None, 
                 amount: float = None, currency: str = "RUB"):
        self.telegram_id = telegram_id
        self.subscription_type = subscription_type
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active
        self.payment_id = payment_id
        self.amount = amount
        self.currency = currency
    
    def is_expired(self) -> bool:
        """Проверка истечения подписки"""
        return datetime.now() > self.end_date
    
    def days_remaining(self) -> int:
        """Количество дней до истечения подписки"""
        if self.is_expired():
            return 0
        return (self.end_date - datetime.now()).days