"""
Сервис для работы с платежами через YooKassa
"""
import logging
import aiohttp
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)


class YooKassaService:
    """Сервис для работы с YooKassa API"""
    
    # Тестовые реквизиты YooKassa
    TEST_SHOP_ID = "1000000"
    TEST_SECRET_KEY = "test_secretkey"
    API_URL = "https://api.yookassa.ru/v3"
    
    # Цены подписок в рублях
    SUBSCRIPTION_PRICES = {
        "1month": 299.00,
        "3months": 799.00,
        "6months": 1499.00,
        "1year": 2799.00
    }
    
    # Названия подписок
    SUBSCRIPTION_NAMES = {
        "1month": "Премиум подписка на 1 месяц",
        "3months": "Премиум подписка на 3 месяца",
        "6months": "Премиум подписка на 6 месяцев",
        "1year": "Премиум подписка на 1 год"
    }
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        """Получение HTTP сессии"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Закрытие HTTP сессии"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Получение заголовков авторизации"""
        import base64
        credentials = f"{self.TEST_SHOP_ID}:{self.TEST_SECRET_KEY}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Idempotence-Key": str(uuid.uuid4())
        }
    
    async def create_payment(self, telegram_id: int, subscription_type: str, 
                           return_url: str = None) -> Optional[Dict]:
        """Создание платежа в YooKassa"""
        try:
            if subscription_type not in self.SUBSCRIPTION_PRICES:
                logger.error(f"Неизвестный тип подписки: {subscription_type}")
                return None
            
            amount = self.SUBSCRIPTION_PRICES[subscription_type]
            description = self.SUBSCRIPTION_NAMES[subscription_type]
            
            payment_data = {
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url or "https://t.me/your_bot"
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "telegram_id": str(telegram_id),
                    "subscription_type": subscription_type,
                    "created_at": datetime.now().isoformat()
                }
            }
            
            session = await self._get_session()
            async with session.post(
                f"{self.API_URL}/payments",
                headers=self._get_auth_headers(),
                data=json.dumps(payment_data)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Платеж создан: {result.get('id')}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка создания платежа: {response.status} - {error_text}")
                    return None
        
        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {e}")
            return None
    
    async def check_payment_status(self, payment_id: str) -> Optional[Dict]:
        """Проверка статуса платежа"""
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.API_URL}/payments/{payment_id}",
                headers=self._get_auth_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка проверки платежа: {response.status} - {error_text}")
                    return None
        
        except Exception as e:
            logger.error(f"Ошибка при проверке платежа: {e}")
            return None
    
    def get_subscription_duration(self, subscription_type: str) -> timedelta:
        """Получение длительности подписки"""
        durations = {
            "1month": timedelta(days=30),
            "3months": timedelta(days=90),
            "6months": timedelta(days=180),
            "1year": timedelta(days=365)
        }
        return durations.get(subscription_type, timedelta(days=30))
    
    def get_subscription_price(self, subscription_type: str) -> float:
        """Получение цены подписки"""
        return self.SUBSCRIPTION_PRICES.get(subscription_type, 0.0)
    
    def get_subscription_name(self, subscription_type: str) -> str:
        """Получение названия подписки"""
        return self.SUBSCRIPTION_NAMES.get(subscription_type, "Неизвестная подписка")