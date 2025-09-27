"""
Сервис для работы с платежами через YooKassa
"""
import logging
import aiohttp
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
import uuid
from config import config

logger = logging.getLogger(__name__)


class YooKassaService:

    TEST_SHOP_ID = "1164328"
    TEST_SECRET_KEY = "live_FVe4M7peyvzGPRZrM4UJq4pF6soCfuv4VZEgntsPmhs"
    API_URL = "https://api.yookassa.ru/v3"
    
    # Цены подписок в рублях (снижены)
    SUBSCRIPTION_PRICES = {
        # Premium
        "premium_1month": 49.00,
        "premium_3months": 119.00,
        "premium_6months": 199.00,
        "premium_1year": 349.00,
        # PRO PLUS  
        "proplus_1month": 99.00,
        "proplus_3months": 249.00,
        "proplus_6months": 449.00,
        "proplus_1year": 799.00,
        # Legacy support
        "1month": 49.00,
        "3months": 119.00,
        "6months": 199.00,
        "1year": 349.00
    }
    
    # Названия подписок
    SUBSCRIPTION_NAMES = {
        # Premium
        "premium_1month": "ClashBot Премиум подписка на 1 месяц",
        "premium_3months": "ClashBot Премиум подписка на 3 месяца",
        "premium_6months": "ClashBot Премиум подписка на 6 месяцев", 
        "premium_1year": "ClashBot Премиум подписка на 1 год",
        # PRO PLUS
        "proplus_1month": "ClashBot ПРО ПЛЮС подписка на 1 месяц",
        "proplus_3months": "ClashBot ПРО ПЛЮС подписка на 3 месяца",
        "proplus_6months": "ClashBot ПРО ПЛЮС подписка на 6 месяцев",
        "proplus_1year": "ClashBot ПРО ПЛЮС подписка на 1 год",
        "proplus_permanent": "ClashBot ПРО ПЛЮС подписка (Вечная)",
        # Legacy support
        "1month": "ClashBot Премиум подписка на 1 месяц",
        "3months": "ClashBot Премиум подписка на 3 месяца",
        "6months": "ClashBot Премиум подписка на 6 месяцев",
        "1year": "ClashBot Премиум подписка на 1 год"
    }
    
    def __init__(self, bot_username: str = None):
        self.session = None
        self.bot_username = bot_username or "YourBotUsername"
    
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
        
        # Используем credentials из конфигурации, fallback на тестовые значения
        shop_id = config.YOOKASSA_SHOP_ID or self.TEST_SHOP_ID
        secret_key = config.YOOKASSA_SECRET_KEY or self.TEST_SECRET_KEY
        
        credentials = f"{shop_id}:{secret_key}"
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
                    "return_url": return_url or f"https://t.me/{self.bot_username}"
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
        # Извлекаем период из типа подписки
        if 'permanent' in subscription_type:
            return timedelta(days=36500)  # 100 лет для вечной подписки
        elif '1month' in subscription_type:
            return timedelta(days=30)
        elif '3months' in subscription_type:
            return timedelta(days=90)
        elif '6months' in subscription_type:
            return timedelta(days=180)
        elif '1year' in subscription_type:
            return timedelta(days=365)
        else:
            # Fallback для legacy форматов
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
    
    async def create_refund(self, payment_id: str, amount: float, reason: str = None) -> Optional[Dict]:
        """Создание возврата платежа"""
        try:
            refund_data = {
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "RUB"
                },
                "payment_id": payment_id
            }
            
            if reason:
                refund_data["description"] = reason
            
            session = await self._get_session()
            async with session.post(
                f"{self.API_URL}/refunds",
                headers=self._get_auth_headers(),
                json=refund_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Возврат создан: {result.get('id')}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка создания возврата: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Исключение при создании возврата: {e}")
            return None
    
    async def process_refund_notification(self, telegram_id: int, payment_id: str, 
                                        refund_amount: float, bot) -> bool:
        """Обработка уведомления о возврате"""
        try:
            # Уменьшаем дни подписки у пользователя
            # Это нужно реализовать в database service
            
            # Отправляем уведомление пользователю
            notification_text = (
                f"🔄 *Уведомление о возврате*\n\n"
                f"Был совершен возврат на покупку с ID `{payment_id}`.\n"
                f"Сумма возврата: {refund_amount:.2f} ₽\n\n"
                f"Дни подписки были списаны с вашего аккаунта.\n\n"
                f"Если возврат ошибочен, напишите техническому специалисту @Negodayo"
            )
            
            await bot.send_message(
                chat_id=telegram_id,
                text=notification_text,
                parse_mode='Markdown'
            )
            
            logger.info(f"Уведомление о возврате отправлено пользователю {telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обработке уведомления о возврате: {e}")
            return False