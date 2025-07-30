import openai
from typing import Dict, List, Tuple
from decimal import Decimal
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class OpenAIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required for OpenAI models")
        
        try:
            openai.api_key = settings.OPENAI_API_KEY
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            raise
    
    def get_model_config(self, model: str) -> Dict:
        """Получает конфигурацию для конкретной модели"""
        # Базовые настройки для всех моделей
        base_config = {
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        # Специфичные настройки для разных моделей
        model_configs = {
            # GPT-3.5 Models
            "gpt-3.5-turbo": {"max_tokens": 1500, "temperature": 0.7},
            "gpt-3.5-turbo-16k": {"max_tokens": 3000, "temperature": 0.7},
            "gpt-3.5-turbo-instruct": {"max_tokens": 1500, "temperature": 0.7},
            
            # GPT-4 Models
            "gpt-4": {"max_tokens": 4000, "temperature": 0.7},
            "gpt-4-32k": {"max_tokens": 8000, "temperature": 0.7},
            "gpt-4-turbo": {"max_tokens": 4000, "temperature": 0.7},
            "gpt-4-turbo-preview": {"max_tokens": 4000, "temperature": 0.7},
            
            # GPT-4o Models
            "gpt-4o": {"max_tokens": 4000, "temperature": 0.7},
            "gpt-4o-mini": {"max_tokens": 2000, "temperature": 0.7},
            
            # Legacy Models
            "text-davinci-003": {"max_tokens": 1500, "temperature": 0.7},
        }
        
        return model_configs.get(model, base_config)
    
    def generate_structure(self, topic: str, thesis: str, keywords: List[str], 
                          questions: List[str], model: str = "gpt-4o-mini") -> Tuple[str, Dict]:
        """Генерирует структуру статьи"""
        
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
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Ты эксперт по SEO и созданию структур статей. Создавай подробные, логичные структуры статей в markdown формате."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            
            structure = response.choices[0].message.content
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return structure, usage_info
            
        except Exception as e:
            print(f"Error generating structure: {e}")
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
                        character_count: int = 5000, model: str = "gpt-4o-mini") -> Tuple[str, Dict]:
        """Генерирует полный текст статьи по структуре"""
        
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
КРИТИЧЕСКИ ВАЖНО: Статья должна быть ТОЧНО {character_count} знаков (±200 знаков). Это строгое требование!
- Заголовок до 60-70 символов с социальным триггером
- Лид-абзац 2-3 предложения с главным ключом
- Подзаголовки H2-H3 по 200-300 символов
- Плотность ключевых слов ≈ 1%
- Форматирование: буллеты, нумерация, цитаты
- Bold для выводов, italic для терминов
- БЕЗ таблиц

КОНТРОЛЬ ДЛИНЫ:
- Если текст получается короче {character_count} знаков - добавь больше примеров, деталей, объяснений
- Если текст получается длиннее {character_count} знаков - сократи, убери лишние детали
- В конце проверь длину и подкорректируй до нужного размера

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
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Ты эксперт-копирайтер, специализирующийся на создании качественных SEO-статей. Пишешь информативно, экспертно, с хорошей структурой и естественным включением ключевых слов."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=article_max_tokens,
                temperature=config["temperature"]
            )
            
            article = response.choices[0].message.content
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            # Проверяем и корректируем длину статьи
            article = self._adjust_article_length(article, character_count, model)
            
            return article, usage_info
            
        except Exception as e:
            print(f"Error generating article: {e}")
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
        """Рассчитывает стоимость использования OpenAI API"""
        pricing = settings.OPENAI_PRICING.get(model, settings.OPENAI_PRICING["gpt-4o-mini"])
        
        input_cost = (usage_info["prompt_tokens"] / 1000) * pricing["input"]
        output_cost = (usage_info["completion_tokens"] / 1000) * pricing["output"]
        
        return Decimal(str(input_cost + output_cost)).quantize(Decimal('0.000001'))
    
    def _adjust_article_length(self, article: str, target_length: int, model: str) -> str:
        """Корректирует длину статьи если она не соответствует требованиям"""
        current_length = len(article)
        tolerance = 200  # Допустимое отклонение
        
        # Если длина в пределах допустимого отклонения, возвращаем как есть
        if target_length - tolerance <= current_length <= target_length + tolerance:
            return article
        
        print(f"Корректируем длину статьи: текущая {current_length}, нужна {target_length}")
        
        if current_length < target_length - tolerance:
            # Статья слишком короткая, нужно расширить
            return self._expand_article(article, target_length, model)
        elif current_length > target_length + tolerance:
            # Статья слишком длинная, нужно сократить
            return self._shorten_article(article, target_length, model)
        
        return article
    
    def _expand_article(self, article: str, target_length: int, model: str) -> str:
        """Расширяет статью до нужной длины"""
        try:
            prompt = f"""
Исходная статья:
{article}

ЗАДАЧА: Расширь эту статью до {target_length} знаков (сейчас {len(article)} знаков).

ТРЕБОВАНИЯ:
- Добавь больше деталей, примеров, объяснений
- Сохрани стиль и структуру оригинала
- Не добавляй новые разделы, только расширяй существующие
- Итоговая длина должна быть близка к {target_length} знакам

Верни ТОЛЬКО расширенную статью без комментариев.
"""
            
            config = self.get_model_config(model)
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Ты эксперт-редактор, умеющий качественно расширять тексты."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config["max_tokens"],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error expanding article: {e}")
            return article
    
    def _shorten_article(self, article: str, target_length: int, model: str) -> str:
        """Сокращает статью до нужной длины"""
        try:
            prompt = f"""
Исходная статья:
{article}

ЗАДАЧА: Сократи эту статью до {target_length} знаков (сейчас {len(article)} знаков).

ТРЕБОВАНИЯ:
- Убери лишние детали, повторы, избыточные объяснения
- Сохрани основную суть, структуру и ключевые идеи
- Сохрани все заголовки и важные выводы
- Итоговая длина должна быть близка к {target_length} знакам

Верни ТОЛЬКО сокращенную статью без комментариев.
"""
            
            config = self.get_model_config(model)
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Ты эксперт-редактор, умеющий качественно сокращать тексты без потери смысла."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config["max_tokens"],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error shortening article: {e}")
            return article 