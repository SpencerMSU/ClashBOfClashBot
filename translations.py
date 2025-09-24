"""
Система переводов для бота
"""
from typing import Dict, Any
from telegram import Update


class TranslationManager:
    """Менеджер переводов"""
    
    def __init__(self):
        # Поддерживаемые языки
        self.supported_languages = {'ru', 'en'}
        self.default_language = 'ru'
        
        # Словари переводов
        self.translations = {
            'ru': {
                # CWL Messages
                'cwl_not_participating': '❌ Клан не участвует в текущем сезоне ЛВК.',
                'cwl_back_to_clan': '⬅️ Назад к клану',
                
                # Analyzer Messages
                'analyzer_coming_soon': '🤖 <b>Анализатор войн</b>\n\n🚧 <b>В разработке</b>\n\nАнализатор находится в стадии разработки.\nКогда-то он будет, но не сейчас.\n\nСледите за обновлениями!',
                'analyzer_refresh_error': '🤖 <b>Анализатор войн</b>\n\n🚧 Функция временно недоступна.\nПопробуйте позже.',
                
                # Achievement Names (Russian translations)
                'achievement_names': {
                    'Bigger Coffers': 'Большие Сундуки',
                    'Get those Goblins!': 'Поймай Гоблинов!',
                    'Bigger & Better': 'Больше и Лучше',
                    'Nice and Tidy': 'Чисто и Аккуратно',
                    'Release the Beasts': 'Выпусти Зверей',
                    'Gold Grab': 'Захват Золота',
                    'Elixir Escapade': 'Эликсирное Приключение',
                    'Sweet Victory!': 'Сладкая Победа!',
                    'Empire Builder': 'Строитель Империи',
                    'Wall Buster': 'Разрушитель Стен',
                    'Humiliator': 'Унизитель',
                    'Union Buster': 'Разрушитель Союзов',
                    'Conqueror': 'Завоеватель',
                    'Unbreakable': 'Несокрушимый',
                    'Friend in Need': 'Друг в Беде',
                    'Mortar Mauler': 'Сокрушитель Мортир',
                    'Heroic Heist': 'Героическое Ограбление',
                    'League All-Star': 'Звезда Лиги',
                    'X-Bow Exterminator': 'Истребитель Адских Луков',
                    'Firefighter': 'Пожарный',
                    'War Hero': 'Герой Войны',
                    'Treasurer': 'Казначей',
                    'Anti-Artillery': 'Противоартиллерийский',
                    'Sharing is caring': 'Делиться значит заботиться',
                    'Keep your account safe!': 'Сохрани свой аккаунт в безопасности!',
                    'Master Engineering': 'Мастер Инженерии',
                    'Next Generation Model': 'Модель Нового Поколения',
                    'Un-Build It': 'Разстрой Это',
                    'Champion Builder': 'Чемпион Строитель',
                    'High Gear': 'Высокая Передача',
                    'Hidden Treasures': 'Скрытые Сокровища',
                    'Games Champion': 'Чемпион Игр',
                    'Dragon Slayer': 'Убийца Драконов',
                    'War League Legend': 'Легенда Лиги Войн',
                    'Keep your account safe': 'Сохрани свой аккаунт в безопасности',
                    'Well Seasoned': 'Хорошо Приправленный',
                    'Shattered and Scattered': 'Разбитый и Рассеянный',
                    'Not So Easy This Time': 'На Этот Раз Не Так Просто',
                    'Bust This!': 'Разруши Это!',
                    'Superb Work': 'Превосходная Работа',
                    'Siege Sharer': 'Дележка Осадных Машин',
                    'Aggressive Artillery': 'Агрессивная Артиллерия',
                    'Counterspell': 'Контрзаклинание',
                    'Monolith Masher': 'Сокрушитель Монолитов',
                    'Ungrateful Child': 'Неблагодарное Дитя'
                }
            },
            'en': {
                # CWL Messages
                'cwl_not_participating': '❌ Clan is not participating in the current CWL season.',
                'cwl_back_to_clan': '⬅️ Back to clan',
                
                # Analyzer Messages
                'analyzer_coming_soon': '🤖 <b>War Analyzer</b>\n\n🚧 <b>Under Development</b>\n\nThe analyzer is under development.\nSomeday it will be, but not now.\n\nStay tuned for updates!',
                'analyzer_refresh_error': '🤖 <b>War Analyzer</b>\n\n🚧 Feature temporarily unavailable.\nTry again later.',
                
                # Achievement Names (English - original names)
                'achievement_names': {}  # English names stay as is
            }
        }
    
    def get_user_language(self, update: Update) -> str:
        """Определяет язык пользователя из Telegram"""
        try:
            # Получаем языковой код пользователя из Telegram
            if update.effective_user and update.effective_user.language_code:
                lang_code = update.effective_user.language_code.lower()
                # Берем первые 2 символа для языкового кода
                lang = lang_code[:2]
                if lang in self.supported_languages:
                    return lang
        except Exception:
            pass
        
        return self.default_language
    
    def get_text(self, update: Update, key: str, default: str = None) -> str:
        """Получает переведенный текст для пользователя"""
        user_lang = self.get_user_language(update)
        
        if user_lang in self.translations and key in self.translations[user_lang]:
            return self.translations[user_lang][key]
        
        # Fallback to default language
        if self.default_language in self.translations and key in self.translations[self.default_language]:
            return self.translations[self.default_language][key]
        
        return default or key
    
    def get_achievement_name(self, update: Update, original_name: str) -> str:
        """Получает переведенное название достижения"""
        user_lang = self.get_user_language(update)
        
        if (user_lang in self.translations and 
            'achievement_names' in self.translations[user_lang] and
            original_name in self.translations[user_lang]['achievement_names']):
            return self.translations[user_lang]['achievement_names'][original_name]
        
        return original_name


# Глобальный экземпляр менеджера переводов
translation_manager = TranslationManager()