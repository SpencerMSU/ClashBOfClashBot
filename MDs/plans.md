# 🏗️ Анализ планировок игроков - Возможности и API

## 📋 Обзор

Документ описывает все доступные способы получения и анализа планировок баз игроков в Clash of Clans, включая официальные API, сторонние сервисы и инновационные подходы.

---

## 🚫 Ограничения официального COC API

### Что НЕ предоставляет официальный API:
❌ **Планировки баз игроков**  
❌ **Расположение зданий**  
❌ **Координаты защитных сооружений**  
❌ **Визуальную информацию о базах**

### Что МОЖНО получить из официального API:
```python
# Доступная информация через COC API
player_info = {
    "townHallLevel": 14,
    "trophies": 5200,
    "buildings": [
        {"name": "Cannon", "level": 18, "maxLevel": 20},
        {"name": "Archer Tower", "level": 17, "maxLevel": 20},
        {"name": "Air Defense", "level": 9, "maxLevel": 10}
        # Список всех зданий с уровнями, но БЕЗ координат
    ],
    "heroes": [
        {"name": "Barbarian King", "level": 75},
        {"name": "Archer Queen", "level": 75}
    ],
    "defenseWins": 1250,
    "attackWins": 2150
}
```

✅ **Полезная информация для анализа силы базы:**
- Уровень ратуши
- Список и уровни всех зданий
- Уровни героев и войск
- Статистика атак и защит
- Достижения игрока

---

## 🌐 Сторонние API и сервисы

### 1. ClashOfStats API
**URL**: `https://www.clashofstats.com/`

```python
class ClashOfStatsAPI:
    """Расширенная статистика игроков"""
    
    BASE_URL = "https://api.clashofstats.com"
    
    async def get_player_analytics(self, player_tag: str):
        """
        Дополнительная аналитика:
        - История изменения трофеев
        - Статистика по сезонам
        - Детальный анализ войн
        - Сравнение с другими игроками
        - Активность по времени
        """
        url = f"{self.BASE_URL}/players/{player_tag}/analytics"
        return await self.make_request(url)
    
    async def get_base_strength_rating(self, player_tag: str):
        """
        Оценка силы базы:
        - Рейтинг защиты (1-10)
        - Слабые места
        - Рекомендации по улучшению
        """
        url = f"{self.BASE_URL}/players/{player_tag}/base-rating"
        return await self.make_request(url)
```

**Преимущества:**
- ✅ Историческая статистика
- ✅ Аналитические метрики
- ✅ Рейтинги игроков
- ✅ Бесплатный доступ к базовым функциям

**Ограничения:**
- ❌ Нет планировок баз
- ❌ Лимиты на запросы

### 2. ClashPerk API
**URL**: `https://clashperk.com/`

```python
class ClashPerkAPI:
    """Расширенная аналитика кланов и игроков"""
    
    async def get_war_performance(self, player_tag: str):
        """
        Анализ эффективности в войнах:
        - Процент успешных атак по уровням ТХ
        - Среднее количество звезд
        - Предпочитаемые стратегии атак
        - Статистика против разных типов баз
        """
        return {
            "war_stats": {
                "total_attacks": 245,
                "success_rate": 0.73,
                "average_stars": 2.1,
                "preferred_strategies": ["LavaLoon", "Electro Dragon"],
                "th_performance": {
                    "vs_th13": {"attacks": 45, "success": 0.67},
                    "vs_th14": {"attacks": 78, "success": 0.71}
                }
            }
        }
    
    async def get_clan_war_insights(self, clan_tag: str):
        """
        Инсайты по клановым войнам:
        - Паттерны успешных атак
        - Анализ вражеских баз
        - Рекомендации по стратегии
        """
        pass
```

### 3. ClashAPI (Неофициальный)
```python
class ClashAPIUnofficial:
    """Дополнительные данные из сторонних источников"""
    
    async def get_popular_base_layouts(self, th_level: int):
        """
        Популярные планировки баз:
        - ТОП-10 баз для каждого ТХ
        - Статистика защит
        - Ссылки на копирование
        """
        return {
            f"th{th_level}_layouts": [
                {
                    "name": "Anti-3 Star Special",
                    "link": "https://link.clashofclans.com/...",
                    "success_rate": 0.85,
                    "usage_count": 15420,
                    "strengths": ["Anti-LavaLoon", "Trap placement"],
                    "weaknesses": ["Vulnerable to QC Hybrid"]
                }
            ]
        }
```

---

## 📸 Computer Vision подходы

### 1. Анализ скриншотов планировок

```python
import cv2
import torch
from transformers import YolosImageProcessor, YolosForObjectDetection

class BaseLayoutAnalyzer:
    """Анализ планировок через Computer Vision"""
    
    def __init__(self):
        # Модель детекции объектов (можно использовать YOLO или аналоги)
        self.processor = YolosImageProcessor.from_pretrained("huggingface/yolos-tiny")
        self.model = YolosForObjectDetection.from_pretrained("huggingface/yolos-tiny")
        
        # Специализированные модели для COC зданий (нужно обучить)
        self.coc_building_detector = self.load_coc_model()
    
    async def analyze_base_screenshot(self, image_bytes: bytes):
        """
        Полный анализ планировки по скриншоту:
        1. Детекция зданий и их позиций
        2. Классификация типа планировки
        3. Анализ слабых мест
        4. Рекомендации по улучшению
        """
        
        # Обработка изображения
        image = self.preprocess_image(image_bytes)
        
        # Детекция зданий
        buildings = await self.detect_buildings(image)
        
        # Анализ расстановки
        layout_analysis = await self.analyze_layout_structure(buildings)
        
        # Поиск уязвимостей
        vulnerabilities = await self.find_vulnerabilities(layout_analysis)
        
        return {
            "buildings_detected": buildings,
            "layout_type": layout_analysis.get("type"),
            "defense_rating": layout_analysis.get("rating"),
            "vulnerabilities": vulnerabilities,
            "recommendations": self.generate_recommendations(vulnerabilities)
        }
    
    async def detect_buildings(self, image):
        """Детекция зданий на изображении"""
        # Используем предобученную модель
        inputs = self.processor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)
        
        # Обработка результатов
        target_sizes = torch.tensor([image.size[::-1]])
        results = self.processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=0.7
        )[0]
        
        buildings = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            building_type = self.classify_coc_building(box, image)
            buildings.append({
                "type": building_type,
                "coordinates": box.tolist(),
                "confidence": score.item(),
                "level": self.estimate_building_level(box, image)
            })
        
        return buildings
```

### 2. Real-time анализ через мобильное приложение

```python
class MobileLayoutAnalyzer:
    """Анализ планировок в реальном времени"""
    
    async def real_time_analysis(self, camera_stream):
        """
        Анализ планировки в реальном времени:
        - Камера наводится на экран с игрой
        - ИИ анализирует планировку
        - AR-наложения показывают слабые места
        """
        
        for frame in camera_stream:
            # Быстрый анализ кадра
            quick_analysis = await self.analyze_frame(frame)
            
            if quick_analysis.base_detected:
                # Создаем AR-наложение
                ar_overlay = self.create_ar_overlay(quick_analysis)
                yield ar_overlay
    
    def create_ar_overlay(self, analysis):
        """Создание AR-наложения с подсказками"""
        overlay = {
            "weak_spots": [],
            "improvement_tips": [],
            "threat_indicators": []
        }
        
        for vulnerability in analysis.vulnerabilities:
            overlay["weak_spots"].append({
                "position": vulnerability.coordinates,
                "color": "red",
                "text": vulnerability.description
            })
        
        return overlay
```

---

## 🤖 AI-подходы для анализа без изображений

### 1. Анализ силы базы по списку зданий

```python
class BaseStrengthAnalyzer:
    """Анализ силы базы на основе списка зданий"""
    
    def __init__(self):
        # Веса важности для разных типов защиты
        self.defense_weights = {
            "Air Defense": 1.0,
            "Inferno Tower": 0.9,
            "Eagle Artillery": 0.8,
            "X-Bow": 0.7,
            "Wizard Tower": 0.6,
            "Archer Tower": 0.5,
            "Cannon": 0.4,
            "Mortar": 0.3
        }
    
    def calculate_defense_rating(self, buildings_list):
        """Расчет рейтинга защиты базы"""
        total_defense = 0
        max_possible = 0
        
        for building in buildings_list:
            if building["name"] in self.defense_weights:
                weight = self.defense_weights[building["name"]]
                level_ratio = building["level"] / building["maxLevel"]
                
                total_defense += weight * level_ratio
                max_possible += weight
        
        defense_rating = (total_defense / max_possible) * 10
        
        return {
            "rating": defense_rating,
            "grade": self.get_defense_grade(defense_rating),
            "recommendations": self.get_upgrade_recommendations(buildings_list)
        }
    
    def analyze_attack_vulnerabilities(self, buildings_data, th_level):
        """Анализ уязвимостей для атак"""
        vulnerabilities = []
        
        # Анализ воздушной защиты
        air_defenses = [b for b in buildings_data if b["name"] == "Air Defense"]
        if len(air_defenses) < self.get_optimal_air_defense_count(th_level):
            vulnerabilities.append({
                "type": "air_vulnerability",
                "severity": "high",
                "description": "Недостаточно воздушных защит",
                "recommended_strategies": ["LavaLoon", "Electro Dragon"]
            })
        
        # Анализ splash damage
        wizard_towers = [b for b in buildings_data if b["name"] == "Wizard Tower"]
        if not wizard_towers or max(wt["level"] for wt in wizard_towers) < th_level - 2:
            vulnerabilities.append({
                "type": "swarm_vulnerability", 
                "severity": "medium",
                "description": "Слабая защита от swarm атак",
                "recommended_strategies": ["Barch", "Goblin Knife"]
            })
        
        return vulnerabilities
```

### 2. Предсказание типа планировки по метаданным

```python
class LayoutTypePredictor:
    """Предсказание типа планировки без изображения"""
    
    def predict_layout_type(self, player_data):
        """
        Предсказание типа планировки на основе:
        - Уровня трофеев
        - Статистики защит
        - Времени последней активности
        - Уровня зданий
        """
        
        features = self.extract_features(player_data)
        layout_type = self.classify_layout(features)
        
        return {
            "predicted_type": layout_type,
            "confidence": 0.75,
            "reasoning": self.explain_prediction(features, layout_type)
        }
    
    def extract_features(self, player_data):
        """Извлечение признаков для классификации"""
        return {
            "trophy_range": self.get_trophy_range(player_data["trophies"]),
            "defense_wins_ratio": player_data["defenseWins"] / (player_data["attackWins"] + 1),
            "th_progress": self.calculate_th_progress(player_data),
            "activity_level": self.estimate_activity(player_data),
            "resource_priority": self.analyze_resource_priority(player_data)
        }
    
    def classify_layout(self, features):
        """Классификация типа планировки"""
        if features["trophy_range"] == "high" and features["defense_wins_ratio"] > 0.3:
            return "trophy_base"
        elif features["activity_level"] == "high" and features["resource_priority"] == "farming":
            return "farming_base"
        elif features["th_progress"] < 0.7:
            return "progression_base"
        else:
            return "hybrid_base"
```

---

## 📱 Интеграция с мобильными приложениями

### 1. Clash Ninja Integration
```python
class ClashNinjaAPI:
    """Интеграция с Clash Ninja для дополнительных данных"""
    
    async def get_base_analysis(self, player_tag: str):
        """
        Анализ базы через Clash Ninja:
        - Оптимальные улучшения
        - Калькулятор ресурсов
        - Планировщик развития
        """
        pass
```

### 2. Pixel API для игрового контента
```python
class PixelAPI:
    """Получение игрового контента через Pixel API"""
    
    async def get_base_layouts_database(self):
        """
        База данных планировок:
        - Популярные базы от про-игроков
        - Сезонные мета-планировки
        - Анти-стратегии для текущей меты
        """
        pass
```

---

## 🔗 Интеграция в ClashBot

### 1. Команды для анализа планировок

```python
# В handlers.py
async def handle_analyze_base_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда анализа планировки игрока"""
    
    if len(context.args) == 0:
        await update.message.reply_text(
            "🏗️ <b>Анализ планировки базы</b>\n\n"
            "Доступные варианты:\n"
            "• Отправьте скриншот планировки\n"
            "• Используйте /analyze_base #тег_игрока\n"
            "• Или просто /analyze_base для анализа своей базы",
            parse_mode='HTML'
        )
        return
    
    player_tag = context.args[0].replace('#', '')
    
    try:
        # Получаем данные игрока
        player_data = await coc_client.get_player_info(player_tag)
        
        # Анализируем силу базы без изображения
        analyzer = BaseStrengthAnalyzer()
        strength_analysis = analyzer.calculate_defense_rating(player_data["buildings"])
        vulnerability_analysis = analyzer.analyze_attack_vulnerabilities(
            player_data["buildings"], 
            player_data["townHallLevel"]
        )
        
        # Предсказываем тип планировки
        layout_predictor = LayoutTypePredictor()
        layout_prediction = layout_predictor.predict_layout_type(player_data)
        
        # Форматируем результат
        response = format_base_analysis_response(
            player_data, strength_analysis, vulnerability_analysis, layout_prediction
        )
        
        await update.message.reply_text(response, parse_mode='HTML')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при анализе: {str(e)}")

async def handle_base_screenshot_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Анализ планировки по скриншоту"""
    
    if not update.message.photo:
        await update.message.reply_text("❌ Пожалуйста, отправьте изображение планировки")
        return
    
    # Загружаем изображение
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()
    
    await update.message.reply_text("🧠 Анализирую планировку... Это может занять минуту.")
    
    try:
        # CV анализ изображения
        layout_analyzer = BaseLayoutAnalyzer()
        analysis_result = await layout_analyzer.analyze_base_screenshot(image_bytes)
        
        # Форматируем результат CV анализа
        response = format_cv_analysis_response(analysis_result)
        
        await update.message.reply_text(response, parse_mode='HTML')
        
        # Предлагаем дополнительные действия
        keyboard = [
            [InlineKeyboardButton("🔍 Детальный анализ", callback_data=f"detailed_{photo.file_id}")],
            [InlineKeyboardButton("💡 Советы по улучшению", callback_data=f"tips_{photo.file_id}")],
            [InlineKeyboardButton("⚔️ Анти-стратегии", callback_data=f"anti_{photo.file_id}")]
        ]
        
        await update.message.reply_text(
            "Что изучим подробнее?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка CV анализа: {e}")
        await update.message.reply_text(
            "❌ Не удалось проанализировать изображение. "
            "Попробуйте более четкий скриншот планировки."
        )
```

### 2. Форматирование результатов

```python
def format_base_analysis_response(player_data, strength_analysis, vulnerabilities, layout_prediction):
    """Форматирование результатов анализа базы"""
    
    name = player_data.get("name", "Игрок")
    th_level = player_data.get("townHallLevel", 0)
    trophies = player_data.get("trophies", 0)
    
    rating = strength_analysis["rating"]
    stars = "⭐" * min(5, max(1, int(rating/2)))
    
    response = f"🏗️ <b>Анализ базы игрока {name}</b>\n\n"
    response += f"🏰 ТХ {th_level} | 🏆 {trophies} трофеев\n\n"
    response += f"📊 <b>Рейтинг защиты:</b> {stars} ({rating:.1f}/10)\n"
    response += f"🎯 <b>Тип планировки:</b> {layout_prediction['predicted_type']}\n\n"
    
    if vulnerabilities:
        response += "⚠️ <b>Основные уязвимости:</b>\n"
        for vuln in vulnerabilities[:3]:
            response += f"• {vuln['description']}\n"
        response += "\n"
    
    response += "💡 <b>Рекомендуемые стратегии атак:</b>\n"
    for vuln in vulnerabilities:
        for strategy in vuln.get("recommended_strategies", []):
            response += f"• {strategy}\n"
    
    return response

def format_cv_analysis_response(cv_analysis):
    """Форматирование результатов Computer Vision анализа"""
    
    buildings = cv_analysis.get("buildings_detected", [])
    layout_type = cv_analysis.get("layout_type", "Неопределен")
    rating = cv_analysis.get("defense_rating", 0)
    
    response = "📸 <b>Анализ планировки по изображению</b>\n\n"
    response += f"🎯 <b>Тип планировки:</b> {layout_type}\n"
    response += f"📊 <b>Оценка:</b> {rating:.1f}/10\n\n"
    
    response += f"🏗️ <b>Обнаружено зданий:</b> {len(buildings)}\n"
    
    # Группируем здания по типам
    building_counts = {}
    for building in buildings:
        building_type = building["type"]
        building_counts[building_type] = building_counts.get(building_type, 0) + 1
    
    for building_type, count in building_counts.items():
        emoji = get_building_emoji(building_type)
        response += f"{emoji} {building_type}: {count}\n"
    
    vulnerabilities = cv_analysis.get("vulnerabilities", [])
    if vulnerabilities:
        response += "\n⚠️ <b>Найденные слабости:</b>\n"
        for vuln in vulnerabilities[:3]:
            response += f"• {vuln}\n"
    
    return response
```

---

## 📊 Сравнение подходов

| Подход | Точность | Сложность | Ресурсы | Доступность |
|--------|----------|-----------|---------|-------------|
| **Официальный API** | Средняя | Низкая | Минимальные | ✅ Высокая |
| **Сторонние API** | Высокая | Средняя | Средние | ⚠️ Ограниченная |
| **Computer Vision** | Очень высокая | Высокая | Высокие | ❌ Требует разработки |
| **AI без изображений** | Средняя | Средняя | Средние | ✅ Реализуемо |

---

## 🚀 Рекомендуемая стратегия реализации

### Этап 1: Базовый анализ (1-2 месяца)
- ✅ Анализ силы базы через официальный API
- ✅ Предсказание уязвимостей по списку зданий
- ✅ Интеграция в бот команд анализа

### Этап 2: Расширенная аналитика (2-3 месяца)
- 📅 Интеграция со сторонними API
- 📅 Машинное обучение для предсказания типов планировок
- 📅 Система рекомендаций по улучшению

### Этап 3: Computer Vision (3-6 месяцев)
- 📅 Разработка модели детекции зданий COC
- 📅 Анализ планировок по скриншотам
- 📅 AR-функции для мобильного приложения

---

## 💰 Оценка затрат

### Минимальная реализация (Этап 1):
- Разработка: 40-60 часов
- API costs: $0 (используем бесплатные лимиты)
- Хостинг: $5-10/месяц

### Полная реализация (Все этапы):
- Разработка: 200-300 часов
- ML обучение: $500-1000 (GPU time)
- API costs: $50-100/месяц
- Хостинг: $50-100/месяц

---

## 📖 Заключение

Анализ планировок игроков возможен через множество подходов:

1. **Сейчас доступно**: Анализ силы базы по API данным
2. **Краткосрочно**: Интеграция со сторонними сервисами  
3. **Долгосрочно**: Computer Vision анализ изображений

Каждый подход имеет свои преимущества и может быть реализован поэтапно, начиная с простых решений и постепенно добавляя более сложные функции.

**Рекомендация**: Начать с базового анализа через API, затем добавлять CV функции по мере необходимости и наличия ресурсов.