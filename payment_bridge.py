#!/usr/bin/env python3
"""
Автономный Python скрипт для работы с YooKassa API.
Используется из Go приложения через exec.Command.
"""

import sys
import json
import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
import uuid
from typing import Dict, Optional
import base64
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YooKassaService:
    """Сервис для работы с платежами через YooKassa"""
    
    # Тестовые реквизиты YooKassa (fallback значения)
    TEST_SHOP_ID = "1164328"
    TEST_SECRET_KEY = "live_FVe4M7peyvzGPRZrM4UJq4pF6soCfuv4VZEgntsPmhs"
    API_URL = "https://api.yookassa.ru/v3"
    
    # Цены подписок в рублях
    SUBSCRIPTION_PRICES = {
        "premium_1month": 1.00,
        "premium_3months": 119.00,
        "premium_6months": 199.00,
        "premium_1year": 349.00,
        "proplus_1month": 99.00,
        "proplus_3months": 249.00,
        "proplus_6months": 449.00,
        "proplus_1year": 799.00,
        "1month": 49.00,
        "3months": 119.00,
        "6months": 199.00,
        "1year": 349.00
    }
    
    # Названия подписок
    SUBSCRIPTION_NAMES = {
        "premium_1month": "ClashBot Премиум подписка на 1 месяц",
        "premium_3months": "ClashBot Премиум подписка на 3 месяца",
        "premium_6months": "ClashBot Премиум подписка на 6 месяцев", 
        "premium_1year": "ClashBot Премиум подписка на 1 год",
        "proplus_1month": "ClashBot ПРО ПЛЮС подписка на 1 месяц",
        "proplus_3months": "ClashBot ПРО ПЛЮС подписка на 3 месяца",
        "proplus_6months": "ClashBot ПРО ПЛЮС подписка на 6 месяцев",
        "proplus_1year": "ClashBot ПРО ПЛЮС подписка на 1 год",
        "1month": "ClashBot подписка на 1 месяц",
        "3months": "ClashBot подписка на 3 месяца",
        "6months": "ClashBot подписка на 6 месяцев",
        "1year": "ClashBot подписка на 1 год"
    }
    
    def __init__(self, bot_username: str = None):
        self.session = None
        self.bot_username = bot_username or "ClashBot"
        
        # Получаем реквизиты из переменных окружения или используем тестовые
        self.shop_id = os.getenv('YOOKASSA_SHOP_ID', self.TEST_SHOP_ID)
        self.secret_key = os.getenv('YOOKASSA_SECRET_KEY', self.TEST_SECRET_KEY)
    
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
        credentials = f"{self.shop_id}:{self.secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Idempotence-Key': str(uuid.uuid4())
        }
    
    async def create_payment(self, telegram_id: int, subscription_type: str, 
                           return_url: str = None) -> Optional[Dict]:
        """Создание платежа в YooKassa"""
        try:
            session = await self._get_session()
            
            amount = self.SUBSCRIPTION_PRICES.get(subscription_type, 0.0)
            if amount <= 0:
                logger.error(f"Неизвестный тип подписки: {subscription_type}")
                return None
            
            description = self.SUBSCRIPTION_NAMES.get(subscription_type, f"Подписка {subscription_type}")
            
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
                    "subscription_type": subscription_type
                }
            }
            
            headers = self._get_auth_headers()
            
            async with session.post(f"{self.API_URL}/payments", 
                                  json=payment_data, 
                                  headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Платеж создан: {result['id']}")
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
            headers = self._get_auth_headers()
            
            async with session.get(f"{self.API_URL}/payments/{payment_id}", 
                                 headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Статус платежа {payment_id}: {result.get('status')}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка получения статуса платежа: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка при проверке статуса платежа: {e}")
            return None
    
    def get_subscription_duration(self, subscription_type: str) -> timedelta:
        """Получение длительности подписки"""
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

async def main():
    """Главная функция для обработки команд из Go"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Не указана команда"}))
        sys.exit(1)
    
    command = sys.argv[1]
    service = YooKassaService()
    
    try:
        if command == "create_payment":
            if len(sys.argv) < 5:
                print(json.dumps({"error": "Недостаточно параметров для create_payment"}))
                sys.exit(1)
            
            telegram_id = int(sys.argv[2])
            subscription_type = sys.argv[3]
            return_url = sys.argv[4] if len(sys.argv) > 4 else None
            
            result = await service.create_payment(telegram_id, subscription_type, return_url)
            print(json.dumps(result))
            
        elif command == "check_payment":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Недостаточно параметров для check_payment"}))
                sys.exit(1)
            
            payment_id = sys.argv[2]
            result = await service.check_payment_status(payment_id)
            print(json.dumps(result))
            
        elif command == "get_price":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Недостаточно параметров для get_price"}))
                sys.exit(1)
            
            subscription_type = sys.argv[2]
            price = service.get_subscription_price(subscription_type)
            print(json.dumps({"price": price}))
            
        elif command == "get_name":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Недостаточно параметров для get_name"}))
                sys.exit(1)
            
            subscription_type = sys.argv[2]
            name = service.get_subscription_name(subscription_type)
            print(json.dumps({"name": name}))
            
        else:
            print(json.dumps({"error": f"Неизвестная команда: {command}"}))
            sys.exit(1)
            
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(main())