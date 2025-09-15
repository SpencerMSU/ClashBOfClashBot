"""
Скрипт валидации - проверка работоспособности всех компонентов бота
"""
import asyncio
import os
import sys
import tempfile
import logging

# Временно устанавливаем тестовые переменные окружения
os.environ['BOT_TOKEN'] = 'test_token'
os.environ['COC_API_TOKEN'] = 'test_coc_token'

async def validate_components():
    """Валидация всех компонентов бота"""
    print("🔍 Начинаем валидацию компонентов...")
    
    try:
        # 1. Проверка импорта конфигурации
        print("📋 Проверка конфигурации...")
        from config import config
        assert config.BOT_TOKEN == 'test_token'
        assert config.COC_API_TOKEN == 'test_coc_token'
        print("✅ Конфигурация: OK")
        
        # 2. Проверка моделей данных
        print("📊 Проверка моделей данных...")
        from models.user import User
        from models.war import WarToSave, AttackData
        
        user = User(123, "#ABC123")
        assert user.telegram_id == 123
        assert user.player_tag == "#ABC123"
        
        attack = AttackData("TestPlayer", 3, 95.5)
        assert attack.attacker_name == "TestPlayer"
        assert attack.stars == 3
        
        war = WarToSave(
            end_time="2024-01-01T00:00:00Z",
            opponent_name="Test Clan",
            team_size=15,
            clan_stars=30,
            opponent_stars=25,
            clan_destruction=85.5,
            opponent_destruction=75.2,
            clan_attacks_used=28,
            result="win",
            is_cwl_war=False,
            total_violations=2
        )
        assert war.result == "win"
        print("✅ Модели данных: OK")
        
        # 3. Проверка базы данных (с временным файлом)
        print("🗄️ Проверка базы данных...")
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            from database import DatabaseService
            db_service = DatabaseService(tmp_db.name)
            await db_service.init_db()
            
            # Тест сохранения пользователя
            await db_service.save_user(user)
            found_user = await db_service.find_user(123)
            assert found_user is not None
            assert found_user.player_tag == "#ABC123"
            
            # Тест войны
            await db_service.save_war(war)
            exists = await db_service.war_exists(war.end_time)
            assert exists is True
            
            os.unlink(tmp_db.name)
        print("✅ База данных: OK")
        
        # 4. Проверка COC API клиента
        print("🎮 Проверка COC API клиента...")
        from coc_api import CocApiClient, format_clan_tag, format_player_tag
        
        assert format_clan_tag("abc123") == "#ABC123"
        assert format_player_tag("abc123def") == "#ABC123DEF"
        
        # Создание клиента (без реальных запросов)
        coc_client = CocApiClient()
        assert coc_client.base_url == 'https://api.clashofclans.com/v1'
        print("✅ COC API клиент: OK")
        
        # 5. Проверка клавиатур
        print("⌨️ Проверка клавиатур...")
        from keyboards import Keyboards
        
        main_menu = Keyboards.main_menu()
        assert main_menu is not None
        
        profile_menu = Keyboards.profile_menu("TestPlayer")
        assert profile_menu is not None
        print("✅ Клавиатуры: OK")
        
        # 6. Проверка состояний пользователя
        print("👤 Проверка состояний пользователя...")
        from user_state import UserState
        
        assert UserState.AWAITING_PLAYER_TAG_TO_LINK is not None
        print("✅ Состояния пользователя: OK")
        
        # 7. Проверка обработчиков (без Telegram)
        print("🔧 Проверка обработчиков...")
        from message_generator import MessageGenerator
        from handlers import MessageHandler, CallbackHandler
        
        msg_gen = MessageGenerator(db_service, coc_client)
        msg_handler = MessageHandler(msg_gen)
        callback_handler = CallbackHandler(msg_gen)
        
        assert msg_handler.message_generator is not None
        assert callback_handler.message_generator is not None
        print("✅ Обработчики: OK")
        
        # 8. Проверка архиватора войн
        print("⚔️ Проверка архиватора войн...")
        from war_archiver import WarArchiver
        
        archiver = WarArchiver("#TEST123", db_service, coc_client)
        assert archiver.clan_tag == "#TEST123"
        assert archiver.is_running is False
        print("✅ Архиватор войн: OK")
        
        print("\n🎉 Все компоненты успешно прошли валидацию!")
        print("🚀 Бот готов к запуску с реальными токенами!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Главная функция валидации"""
    success = await validate_components()
    
    if success:
        print("\n📝 Для запуска бота:")
        print("1. Создайте файл .env на основе .env.example")
        print("2. Заполните BOT_TOKEN и COC_API_TOKEN")
        print("3. Запустите: python main.py")
        sys.exit(0)
    else:
        print("\n❌ Валидация не пройдена. Проверьте ошибки выше.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())