import anthropic
from typing import Dict, List, Tuple
from decimal import Decimal
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class AnthropicService:
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required for Claude models")
        
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def get_model_config(self, model: str) -> Dict:
        """Получает конфигурацию для конкретной модели Claude"""
        # Базовые настройки для всех моделей Claude
        base_config = {
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        # Специфичные настройки для разных моделей Claude
        model_configs = {
            # Claude 3 Models
            "claude-3-haiku-20240307": {"max_tokens": 1500, "temperature": 0.7},
            "claude-3-sonnet-20240229": {"max_tokens": 4000, "temperature": 0.7},
            "claude-3-opus-20240229": {"max_tokens": 4000, "temperature": 0.7},
            
            # Claude 3.5 Models (Latest)
            "claude-3-5-sonnet-20241022": {"max_tokens": 4000, "temperature": 0.7},
            "claude-3-5-haiku-20241022": {"max_tokens": 2000, "temperature": 0.7},
        }
        
        return model_configs.get(model, base_config)
    
    def generate_structure(self, topic: str, thesis: str, keywords: List[str], 
                          questions: List[str], model: str = "claude-3-5-sonnet-20241022") -> Tuple[str, Dict]:
        """Генерирует структуру статьи с помощью Claude"""
        
        keywords_str = ", ".join(keywords[:10])
        questions_str = "\n".join(questions[:5])
        
        prompt = f"""
Создай подробную структуру SEO-статьи на тему: "{topic}"

Тезисы автора: {thesis}

Ключевые слова для включения: {keywords_str}

Популярные вопросы пользователей:
{questions_str}

Требования к структуре:
1. Используй markdown формат с заголовками H1, H2, H3
2. Включи введение, основную часть с подразделами и заключение
3. Обязательно используй предоставленные ключевые слова
4. Ответь на популярные вопросы пользователей
5. Структура должна быть логичной и SEO-оптимизированной
6. Длина статьи должна быть 2000-3000 слов

Верни только структуру в markdown формате, без дополнительных комментариев.
"""
        
        try:
            config = self.get_model_config(model)
            response = self.client.messages.create(
                model=model,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            structure = response.content[0].text
            usage_info = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            return structure, usage_info
            
        except Exception as e:
            print(f"Error generating structure with Claude: {e}")
            # Возвращаем базовую структуру
            basic_structure = f"""# {topic}

## Введение
- Что такое {topic}
- Актуальность темы

## Основная часть

### Основные понятия
### Преимущества и недостатки
### Практическое применение
### Советы и рекомендации

## Заключение
- Выводы
- Рекомендации
"""
            return basic_structure, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    def generate_article(self, topic: str, thesis: str, structure: str, 
                        keywords: List[str], style_examples: str = "", 
                        character_count: int = 5000, model: str = "claude-3-5-sonnet-20241022") -> Tuple[str, Dict]:
        """Генерирует полный текст статьи по структуре с помощью Claude"""
        
        keywords_str = ", ".join(keywords[:10])
        
        prompt = f"""
Напиши полную статью о здоровом питании и снижении веса на основе следующей структуры:

Тема: {topic}
Тезисы автора: {thesis}

Структура статьи:
{structure}

Ключевые слова для обязательного включения: {keywords_str}

ПРИМЕРЫ СТИЛЯ ДЛЯ ПОДРАЖАНИЯ:
{style_examples}

ВАЖНО: Изучи приведенные примеры стиля и пиши статью точно в таком же тоне, используя аналогичные речевые обороты, структуру предложений и способы обращения к читателю.

ВАЖНАЯ ЗАДАЧА: Создать статью, которая мотивирует читателя к действию - нажать кнопки «Получить персональный план питания» или «Бесплатный курс по снижению веса» в конце статьи.

ЦЕЛЕВАЯ АУДИТОРИЯ: Люди, желающие похудеть, преимущественно женщины.

КЛЮЧЕВЫЕ СМЫСЛЫ ДЛЯ ВКЛЮЧЕНИЯ (выбери 2-3 наиболее подходящих для темы):
1. Сбалансированное питание с белками, жирами, углеводами, витаминами и минералами
2. Диеты - зло, вызывают стресс и дефицит полезных веществ, приводят к срывам
3. Продукты-помощники: витамины, белковые коктейли для восполнения дефицита
4. Питание каждые 3-4 часа предотвращает голод и контролирует сахар
5. Норма воды: 30-40 мл на кг веса для расщепления жира и ускорения метаболизма
6. Режим сна до 23:00 для правильного метаболизма
7. Белок минимум 1,3 г на кг веса для снижения веса и здоровья
8. Норму белка сложно получить из обычных продуктов - нужны белковые коктейли
9. Худеть в одиночку сложно - важна поддержка консультантов по питанию
10. Осознанное отношение к еде и понимание процессов в организме

АВТОРИТЕТНЫЕ ИСТОЧНИКИ:
Обязательно ссылайся на:
- Исследования и выводы ученых
- Материалы ВОЗ, Роспотребнадзора
- ФГБУН «ФИЦ питания и биотехнологии пищи»
- Академиков РАН (например, Виктор Тутельян)
- Зарубежных экспертов

ТРЕБОВАНИЯ К ТЕКСТУ:
- Размер: {character_count} знаков
- Заголовок до 60-70 символов с социальным триггером
- Лид-абзац 2-3 предложения с главным ключом
- Подзаголовки H2-H3 по 200-300 символов
- Плотность ключевых слов ≈ 1%
- Форматирование: буллеты, нумерация, цитаты
- Bold для выводов, italic для терминов
- БЕЗ таблиц

СТРУКТУРА КОНТЕНТА:
1. Эмоциональный зацеп в начале
2. Объяснение проблемы (почему диеты не работают)
3. Научное обоснование с цитатами экспертов
4. Практические решения
5. Мотивирующий финал, подводящий к кнопкам действия

Напиши полную статью в markdown формате, следуя этому стилю и требованиям.
"""
        
        try:
            config = self.get_model_config(model)
            # Для генерации статьи используем больше токенов
            article_max_tokens = min(config["max_tokens"] * 2, 8000)
            
            response = self.client.messages.create(
                model=model,
                max_tokens=article_max_tokens,
                temperature=config["temperature"],
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            article = response.content[0].text
            usage_info = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            return article, usage_info
            
        except Exception as e:
            print(f"Error generating article with Claude: {e}")
            # Возвращаем базовую статью
            basic_article = f"""# {topic}

{thesis}

## Введение

В данной статье мы рассмотрим тему "{topic}". Эта тема является актуальной и важной для понимания.

## Основная часть

### Основные понятия

Ключевые аспекты темы включают в себя различные элементы, которые необходимо рассмотреть подробно.

### Практическое применение

Рассмотрим практические аспекты использования знаний по данной теме.

## Заключение

В заключение можно сказать, что тема "{topic}" требует детального изучения и практического применения.
"""
            return basic_article, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    def calculate_cost(self, usage_info: Dict, model: str) -> Decimal:
        """Рассчитывает стоимость использования Anthropic API"""
        pricing = settings.ANTHROPIC_PRICING.get(model, settings.ANTHROPIC_PRICING["claude-3-5-sonnet-20241022"])
        
        input_cost = (usage_info["prompt_tokens"] / 1000) * pricing["input"]
        output_cost = (usage_info["completion_tokens"] / 1000) * pricing["output"]
        
        return Decimal(str(input_cost + output_cost)).quantize(Decimal('0.000001')) 