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
                
                # Common Error Messages
                'generic_error': '❌ Произошла ошибка. Попробуйте позже.',
                'loading_error': '❌ Произошла ошибка при загрузке данных.',
                'player_not_found': '❌ Игрок не найден.',
                'clan_not_found': '❌ Клан не найден.',
                
                # Button Text
                'back_to_main_menu': '⬅️ Главное меню',
                'back_to_clan': '⬅️ Назад к клану',
                
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
                },
                # Achievement Descriptions (Russian)
                'achievement_descriptions': {
                    'Bigger Coffers': 'Улучшите хранилища золота',
                    'Get those Goblins!': 'Победите гоблинов в одиночных миссиях',
                    'Bigger & Better': 'Улучшайте ратушу',
                    'Nice and Tidy': 'Уберите препятствия с базы',
                    'Release the Beasts': 'Разблокируйте войска',
                    'Gold Grab': 'Украдите золото в мультиплеерных боях',
                    'Elixir Escapade': 'Украдите эликсир в мультиплеерных боях',
                    'Sweet Victory!': 'Побеждайте в мультиплеерных боях',
                    'Empire Builder': 'Выигрывайте трофеи в мультиплеерных боях',
                    'Wall Buster': 'Улучшайте стены',
                    'Humiliator': 'Побеждайте игроков с более высокой ратушей',
                    'Union Buster': 'Уничтожайте замки кланов в боях',
                    'Conqueror': 'Выигрывайте атаки в клановых войнах',
                    'Unbreakable': 'Успешно защищайтесь в клановых войнах',
                    'Friend in Need': 'Донатьте войска членам клана',
                    'Mortar Mauler': 'Уничтожайте мортиры в боях',
                    'Heroic Heist': 'Украдите темный эликсир в боях',
                    'League All-Star': 'Выигрывайте звезды в войнах',
                    'X-Bow Exterminator': 'Уничтожайте адские луки в боях',
                    'Firefighter': 'Уничтожайте башни ада в боях',
                    'War Hero': 'Выигрывайте звезды в клановых войнах',
                    'Treasurer': 'Донатьте войска в клановых войнах',
                    'Anti-Artillery': 'Уничтожайте орлиные артиллерии в боях',
                    'Sharing is caring': 'Донатьте заклинания членам клана',
                    'Keep your account safe!': 'Защитите свой аккаунт (Supercell ID)',
                    'Master Engineering': 'Улучшайте зал строителя',
                    'Next Generation Model': 'Улучшайте боевую машину',
                    'Un-Build It': 'Уничтожайте залы строителя в боях',
                    'Champion Builder': 'Достигайте высоких трофеев в деревне строителя',
                    'High Gear': 'Прокачивайте боевую машину на максимум',
                    'Hidden Treasures': 'Разрушайте здания в деревне строителя',
                    'Games Champion': 'Выигрывайте звезды в клановых играх',
                    'Dragon Slayer': 'Уничтожайте осадные машины в боях',
                    'War League Legend': 'Выигрывайте звезды в лиге войн кланов',
                    'Keep your account safe': 'Защитите свой аккаунт (Supercell ID)',
                    'Well Seasoned': 'Участвуйте в сезонах клановых игр',
                    'Shattered and Scattered': 'Уничтожайте разбросы в боях',
                    'Not So Easy This Time': 'Уничтожайте гига-тесла в боях',
                    'Bust This!': 'Уничтожайте гига-ад в боях',
                    'Superb Work': 'Улучшайте зал строителя до максимума',
                    'Siege Sharer': 'Донатьте осадные машины в войнах',
                    'Aggressive Artillery': 'Уничтожайте осадные казармы в боях',
                    'Counterspell': 'Уничтожайте фабрики заклинаний в боях',
                    'Monolith Masher': 'Уничтожайте монолиты в боях',
                    'Ungrateful Child': 'Уничтожайте статуи в боях'
                }
            },
            'en': {
                # CWL Messages
                'cwl_not_participating': '❌ Clan is not participating in the current CWL season.',
                'cwl_back_to_clan': '⬅️ Back to clan',
                
                # Common Error Messages
                'generic_error': '❌ An error occurred. Please try again later.',
                'loading_error': '❌ Error loading data.',
                'player_not_found': '❌ Player not found.',
                'clan_not_found': '❌ Clan not found.',
                
                # Button Text
                'back_to_main_menu': '⬅️ Main Menu',
                'back_to_clan': '⬅️ Back to clan',
                
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
    
    def get_achievement_description(self, update: Update, original_name: str) -> str:
        """Получает описание достижения (что делать для прогресса)"""
        user_lang = self.get_user_language(update)
        
        if (user_lang in self.translations and 
            'achievement_descriptions' in self.translations[user_lang] and
            original_name in self.translations[user_lang]['achievement_descriptions']):
            return self.translations[user_lang]['achievement_descriptions'][original_name]
        
        return ""


# Глобальный экземпляр менеджера переводов
translation_manager = TranslationManager()