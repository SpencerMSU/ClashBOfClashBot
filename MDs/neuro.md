# 🧠 Нейросеть для анализа атак ClashBot (Бесплатная версия)

## 📋 Обзор проекта

Упрощенная нейросеть для ClashBot, сфокусированная на анализе кого атаковать в клановых войнах. Реализация основана на бесплатных решениях и минимальных ресурсах.

---

## 🎯 Основная задача

**Анализ целей для атаки** - нейросеть анализирует доступные цели в клановой войне и рекомендует оптимальные варианты для каждого игрока.

### Входные данные:
- Информация об игроке (ТХ, войска, герои)
- Список доступных целей в войне
- Контекст (обычная война / ЛВК)

### Выходные данные:
- Рекомендуемая цель для атаки
- Вероятность успеха
- Краткое обоснование выбора

---

## 🏗️ Архитектура (Упрощенная)

### Тип модели: Легкая нейросеть
```
🧠 ClashBot Attack Analyzer (Lite)
├── 📊 Feature Encoder (простые признаки)
├── 🔤 Small Embedding Layer (128 dim)
├── 🧩 2-3 Dense Layers
├── 🎯 Classification Head (выбор цели)
└── 📈 Probability Output
```

### Технические параметры:
- **Размер модели**: ~5-10M параметров
- **Входные признаки**: 50-100 признаков
- **Обучение**: На CPU/небольшой GPU
- **Память**: <1GB RAM
- **Время ответа**: <1 секунда

---

## 📚 Данные для обучения (Бесплатные источники)

### 1. COC API данные:
- История клановых войн (бесплатно)
- Профили игроков (бесплатно)
- Результаты атак (бесплатно)

### 2. Синтетические данные:
```python
def generate_training_example():
    """Генерация обучающего примера"""
    return {
        "attacker": {
            "th_level": random.randint(8, 16),
            "hero_levels": generate_heroes(),
            "army_strength": calculate_army_power()
        },
        "target": {
            "th_level": random.randint(8, 16),
            "defense_strength": calculate_defense_power(),
            "layout_type": random.choice(["defensive", "farming", "trophy"])
        },
        "context": random.choice(["regular_war", "cwl"]),
        "result": {
            "stars": random.randint(0, 3),
            "success": True/False
        }
    }
```

### 3. Объем данных:
- **Обучающий набор**: 50K примеров
- **Тестовый набор**: 10K примеров
- **Размер**: ~100MB

---

## 🛠️ Техническая реализация

### 1. Простая модель на Python
```python
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

class AttackTargetAnalyzer:
    """Анализатор целей для атак"""
    
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.model = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            max_iter=1000,
            random_state=42
        )
    
    def extract_features(self, attacker_data, target_data, context):
        """Извлечение признаков для анализа"""
        features = []
        
        # Признаки атакующего
        features.extend([
            attacker_data.get("th_level", 0),
            attacker_data.get("hero_power", 0),
            attacker_data.get("army_strength", 0)
        ])
        
        # Признаки цели
        features.extend([
            target_data.get("th_level", 0),
            target_data.get("defense_rating", 0),
            target_data.get("walls_level", 0)
        ])
        
        # Контекстные признаки
        features.extend([
            1 if context == "cwl" else 0,
            self.calculate_th_difference(attacker_data, target_data)
        ])
        
        return np.array(features)
    
    def predict_success(self, attacker, target, context):
        """Предсказание успеха атаки"""
        features = self.extract_features(attacker, target, context)
        
        # Вероятность успеха
        success_prob = self.model.predict_proba([features])[0][1]
        
        # Рекомендация
        recommendation = self.generate_recommendation(success_prob, attacker, target)
        
        return {
            "success_probability": success_prob,
            "recommended": success_prob > 0.6,
            "reasoning": recommendation
        }
    
    def generate_recommendation(self, prob, attacker, target):
        """Генерация обоснования рекомендации"""
        th_diff = target["th_level"] - attacker["th_level"]
        
        if prob > 0.8:
            return f"Отличная цель! Высокие шансы на успех ({prob:.1%})"
        elif prob > 0.6:
            return f"Хорошая цель для атаки ({prob:.1%})"
        elif th_diff > 1:
            return f"Сложная цель (+{th_diff} ТХ), низкие шансы"
        else:
            return f"Не рекомендуется, вероятность успеха {prob:.1%}"
```

### 2. Интеграция с ботом
```python
# В handlers.py
async def analyze_war_targets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Анализ целей в клановой войне"""
    
    # Получаем данные о войне
    war_data = await get_current_war_data()
    user_tag = get_user_tag(update.effective_user.id)
    
    if not war_data or not user_tag:
        await update.message.reply_text("❌ Не удалось получить данные о войне")
        return
    
    # Находим игрока в войне
    player_data = find_player_in_war(war_data, user_tag)
    if not player_data:
        await update.message.reply_text("❌ Вы не участвуете в текущей войне")
        return
    
    # Анализируем доступные цели
    analyzer = AttackTargetAnalyzer()
    recommendations = []
    
    for enemy in war_data["opponent"]["members"]:
        if is_target_available(enemy):
            analysis = analyzer.predict_success(
                player_data, enemy, war_data["type"]
            )
            
            recommendations.append({
                "target": enemy,
                "analysis": analysis
            })
    
    # Сортируем по вероятности успеха
    recommendations.sort(key=lambda x: x["analysis"]["success_probability"], reverse=True)
    
    # Форматируем ответ
    response = format_attack_recommendations(recommendations[:5])
    await update.message.reply_text(response, parse_mode='HTML')

def format_attack_recommendations(recommendations):
    """Форматирование рекомендаций для пользователя"""
    response = "🎯 <b>Рекомендации по атакам:</b>\n\n"
    
    for i, rec in enumerate(recommendations, 1):
        target = rec["target"]
        analysis = rec["analysis"]
        
        prob_emoji = "🟢" if analysis["success_probability"] > 0.7 else "🟡" if analysis["success_probability"] > 0.5 else "🔴"
        
        response += f"{i}. {prob_emoji} <b>{target['name']}</b> (#{target['mapPosition']})\n"
        response += f"   ТХ {target['townhallLevel']} | Шанс: {analysis['success_probability']:.1%}\n"
        response += f"   💭 {analysis['reasoning']}\n\n"
    
    return response
```

---

## 📊 Простые метрики

### Оценка качества:
- **Точность предсказаний**: >70%
- **Полезность советов**: Оценка пользователей
- **Скорость работы**: <1 сек на анализ

### Сбор обратной связи:
```python
async def collect_attack_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сбор обратной связи после атаки"""
    
    # Пользователь отмечает результат атаки
    keyboard = [
        [InlineKeyboardButton("⭐⭐⭐ 3 звезды", callback_data="feedback_3stars")],
        [InlineKeyboardButton("⭐⭐ 2 звезды", callback_data="feedback_2stars")],
        [InlineKeyboardButton("⭐ 1 звезда", callback_data="feedback_1star")],
        [InlineKeyboardButton("❌ Неудача", callback_data="feedback_fail")]
    ]
    
    await update.message.reply_text(
        "Как прошла атака по рекомендованной цели?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
```

---

## 🚀 План реализации (2-3 месяца)

### Месяц 1: Подготовка данных и базовая модель
- ✅ Сбор данных из COC API
- ✅ Создание обучающих примеров
- ✅ Обучение простой модели
- ✅ Тестирование на исторических данных

### Месяц 2: Интеграция с ботом
- 📅 Создание API для модели
- 📅 Интеграция с командами бота
- 📅 Тестирование с реальными пользователями
- 📅 Сбор обратной связи

### Месяц 3: Улучшения и оптимизация
- 📅 Улучшение модели на основе feedback
- 📅 Добавление новых признаков
- 📅 Оптимизация скорости работы
- 📅 Финальное тестирование

---

## 💰 Бюджет (Минимальный)

### Расходы:
- **Разработка**: Бесплатно (свои силы)
- **Хостинг**: $5-10/месяц (VPS)
- **API**: Бесплатно (COC API)
- **Обучение модели**: Бесплатно (CPU/Google Colab)

### Общий бюджет: <$50 в год

---

## 🎯 Ожидаемые результаты

### Для пользователей:
- 📈 Увеличение процента успешных атак на 15-20%
- ⏱️ Экономия времени на выбор целей
- 📚 Обучение тактикам через объяснения

### Для бота:
- 🚀 Новая уникальная функция
- 👥 Привлечение пользователей
- 📊 Данные для дальнейших улучшений

---

## 🔄 Дальнейшее развитие

После успешной реализации базовой версии:

1. **Более сложные модели** при наличии ресурсов
2. **Анализ планировок** через Computer Vision
3. **Персонализация** под стиль игры
4. **Интеграция с другими функциями** бота

---

## 📖 Заключение

Эта упрощенная версия нейросети для анализа атак:
- ✅ Реализуема с минимальными ресурсами
- ✅ Предоставляет реальную пользу игрокам
- ✅ Создает основу для дальнейшего развития
- ✅ Не требует больших инвестиций

Фокус на одной конкретной задаче (выбор целей для атак) позволяет создать действительно полезный инструмент, который можно реализовать быстро и эффективно.