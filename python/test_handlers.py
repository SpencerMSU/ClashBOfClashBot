"""
Тестовый файл для проверки импортов и базовой функциональности.
"""
import sys
import os

# Добавляем путь к нашему пакету
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тестирование импортов."""
    try:
        # Тестируем основные модули
        from bot.user_state import UserState
        from bot.war_sort import WarSort
        from bot.keyboards import Keyboards
        
        print("✅ Основные модули импортированы успешно")
        
        # Тестируем обработчики
        from bot.handlers.message_handler import MessageHandler
        from bot.handlers.callback_handler import CallbackHandler
        
        print("✅ Обработчики импортированы успешно")
        
        # Тестируем главный модуль
        from bot.handlers import setup_handlers
        from bot.bot_handlers import BotHandlers
        
        print("✅ Главный модуль handlers импортирован успешно")
        
        # Тестируем основной пакет  
        from bot import (
            validate_clan_tag,
            process_tag,
            UserState,
            WarSort,
            Keyboards
        )
        
        print("✅ Основной пакет bot импортирован успешно")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_functionality():
    """Тестирование базовой функциональности."""
    try:
        from bot import UserState, WarSort, Keyboards, validate_clan_tag, process_tag
        
        # Тестируем enum'ы
        assert UserState.AWAITING_PLAYER_TAG_TO_LINK.value == "awaiting_player_tag_to_link"
        assert WarSort.DATE_DESC.value == "DATE_DESC"
        print("✅ Enum'ы работают корректно")
        
        # Тестируем константы
        assert Keyboards.PROFILE_BTN == "👤 Профиль"
        assert Keyboards.CLAN_BTN == "🛡 Клан"
        print("✅ Константы клавиатур корректны")
        
        # Тестируем обработку тегов
        assert process_tag("abc123") == "#ABC123"
        assert process_tag("#def456") == "#DEF456"
        assert process_tag("  ghi789  ") == "#GHI789"
        print("✅ Обработка тегов работает корректно")
        
        # Тестируем валидацию
        assert validate_clan_tag("#ABC123")
        assert not validate_clan_tag("")
        assert not validate_clan_tag("ab")
        print("✅ Валидация тегов работает корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка функциональности: {e}")
        return False

def main():
    """Главная функция тестирования."""
    print("🔍 Тестирование Python handlers для Clash of Clans Bot")
    print("=" * 60)
    
    # Тестируем импорты
    if not test_imports():
        print("\n❌ Тестирование провалено на этапе импортов")
        return False
    
    # Тестируем функциональность
    if not test_functionality():
        print("\n❌ Тестирование провалено на этапе функциональности")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Все тесты пройдены успешно!")
    print("\nСозданные компоненты:")
    print("• MessageHandler - обработка текстовых сообщений")
    print("• CallbackHandler - обработка callback-запросов")
    print("• UserState - состояния пользователей")
    print("• WarSort - типы сортировки войн")
    print("• Keyboards - константы клавиатур")
    print("• Вспомогательные функции валидации и обработки")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)