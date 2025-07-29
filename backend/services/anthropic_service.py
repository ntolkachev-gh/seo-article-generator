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
                        keywords: List[str], model: str = "claude-3-5-sonnet-20241022") -> Tuple[str, Dict]:
        """Генерирует полный текст статьи по структуре с помощью Claude"""
        
        keywords_str = ", ".join(keywords[:10])
        
        prompt = f"""
Напиши полную SEO-статью на основе следующей структуры:

Тема: {topic}
Тезисы автора: {thesis}

Структура статьи:
{structure}

Ключевые слова для обязательного включения: {keywords_str}

Требования к статье:
1. Объем 2000-3000 слов
2. Используй предоставленную структуру как основу
3. Естественно включи все ключевые слова
4. Пиши экспертно и информативно
5. Используй markdown формат
6. Добавь практические примеры и советы
7. Статья должна быть полезной и читабельной
8. Избегай переспама ключевых слов

Напиши полную статью в markdown формате.
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