#!/usr/bin/env python3
"""
Обертка для запуска Ultra Clan Scanner из корневой папки проекта
Решает проблемы с импортами и путями
"""
import os
import sys
import subprocess

def main():
    # Получаем путь к корневой папке проекта
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Путь к скрипту Ultra Scanner
    scanner_path = os.path.join(current_dir, 'scripts', 'all_importer.py')
    
    if not os.path.exists(scanner_path):
        print(f"❌ Ошибка: Ultra Scanner не найден по пути {scanner_path}")
        return 1
    
    print("🚀 Запуск Ultra Clan Scanner...")
    print(f"📁 Рабочая папка: {current_dir}")
    print(f"🐍 Python: {sys.executable}")
    print(f"📄 Скрипт: {scanner_path}")
    print()
    
    try:
        # Запуск скрипта с правильной рабочей папкой
        result = subprocess.run([
            sys.executable, scanner_path
        ], cwd=current_dir, check=True)
        
        print("\n✅ Ultra Clan Scanner успешно завершен!")
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при выполнении Ultra Scanner: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n⏹️ Ultra Scanner остановлен пользователем")
        return 1
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())