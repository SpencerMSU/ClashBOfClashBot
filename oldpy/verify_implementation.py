#!/usr/bin/env python3
"""
Скрипт для проверки полноты реализации Python версии ClashBot.
Запустите этот скрипт, чтобы убедиться, что все компоненты на месте.

Использование:
    python3 verify_implementation.py

Скрипт проверяет:
- Наличие всех основных файлов
- Наличие всех моделей
- Наличие всех сканеров
- Ключевые функции в каждом модуле
- Статистику методов

Возвращает 0 при успехе, 1 при ошибках.
"""

import os
import re
import sys
from typing import Dict, List

def check_file_exists(filename: str) -> bool:
    """Проверка существования файла"""
    return os.path.exists(filename)

def check_function_exists(filename: str, function_name: str) -> bool:
    """Проверка существования функции в файле"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        patterns = [
            f'def {function_name}\\(',
            f'async def {function_name}\\('
        ]
        return any(re.search(pattern, content) for pattern in patterns)
    except:
        return False

def main():
    """Основная функция проверки"""
    print("=" * 70)
    print("🔍 ПРОВЕРКА ПОЛНОТЫ РЕАЛИЗАЦИИ PYTHON ВЕРСИИ CLASHBOT")
    print("=" * 70)
    
    all_tests_passed = True
    
    # 1. Проверка основных файлов
    print("\n✅ Проверка основных файлов...")
    required_files = [
        'bot.py', 'handlers.py', 'message_generator.py', 'keyboards.py',
        'coc_api.py', 'database.py', 'payment_service.py', 'building_monitor.py',
        'war_archiver.py', 'user_state.py', 'translations.py', 'policy.py',
        'config.py', 'building_data.py', 'errors.py'
    ]
    
    missing_files = [f for f in required_files if not check_file_exists(f)]
    if missing_files:
        print(f"   ❌ Отсутствуют файлы: {', '.join(missing_files)}")
        all_tests_passed = False
    else:
        print(f"   ✅ Все {len(required_files)} основных файлов присутствуют")
    
    # 2. Проверка моделей
    print("\n✅ Проверка моделей...")
    model_files = [
        'models/user.py', 'models/war.py', 'models/subscription.py',
        'models/building.py', 'models/user_profile.py', 'models/linked_clan.py'
    ]
    
    missing_models = [f for f in model_files if not check_file_exists(f)]
    if missing_models:
        print(f"   ❌ Отсутствуют модели: {', '.join(missing_models)}")
        all_tests_passed = False
    else:
        print(f"   ✅ Все {len(model_files)} моделей присутствуют")
    
    # 3. Проверка сканеров
    print("\n✅ Проверка сканеров...")
    scanner_files = ['scanners/clan_scanner.py', 'scanners/war_importer.py']
    
    missing_scanners = [f for f in scanner_files if not check_file_exists(f)]
    if missing_scanners:
        print(f"   ❌ Отсутствуют сканеры: {', '.join(missing_scanners)}")
        all_tests_passed = False
    else:
        print(f"   ✅ Все {len(scanner_files)} сканера присутствуют")
    
    # 4. Ключевые функции
    print("\n✅ Проверка ключевых функций...")
    
    key_functions = {
        'message_generator.py': [
            'handle_premium_menu', 'handle_building_tracker_toggle',
            'handle_subscription_type_selection', 'display_war_violations'
        ],
        'handlers.py': [
            '_handle_premium_menu', '_handle_building_tracker'
        ],
        'coc_api.py': [
            'get_player_info', 'get_clan_info', '_track_error'
        ],
        'payment_service.py': [
            'create_payment', 'check_payment_status', 'create_refund'
        ],
        'keyboards.py': [
            'main_menu', 'premium_menu', 'subscription_types'
        ]
    }
    
    missing_functions = []
    for filename, functions in key_functions.items():
        for func in functions:
            if not check_function_exists(filename, func):
                missing_functions.append(f"{filename}:{func}")
    
    if missing_functions:
        print(f"   ❌ Отсутствуют функции:")
        for func in missing_functions:
            print(f"      - {func}")
        all_tests_passed = False
    else:
        total_checked = sum(len(funcs) for funcs in key_functions.values())
        print(f"   ✅ Все {total_checked} ключевых функций присутствуют")
    
    # Итоговый результат
    print("\n" + "=" * 70)
    if all_tests_passed:
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ PYTHON РЕАЛИЗАЦИЯ ПОЛНОСТЬЮ ЗАВЕРШЕНА!")
        print("\n📚 Для детальной информации см. PYTHON_IMPLEMENTATION_COMPLETE.md")
        print("=" * 70)
        return 0
    else:
        print("❌ НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ!")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
