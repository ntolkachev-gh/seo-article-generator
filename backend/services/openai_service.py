import openai
from typing import Dict, List, Tuple
from decimal import Decimal
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_structure(self, topic: str, thesis: str, keywords: List[str], 
                          questions: List[str], model: str = "gpt-3.5-turbo") -> Tuple[str, Dict]:
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
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Ты эксперт по SEO и созданию структур статей. Создавай подробные, логичные структуры статей в markdown формате."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
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
                        keywords: List[str], model: str = "gpt-3.5-turbo") -> Tuple[str, Dict]:
        """Генерирует полный текст статьи по структуре"""
        
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
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Ты эксперт-копирайтер, специализирующийся на создании качественных SEO-статей. Пишешь информативно, экспертно, с хорошей структурой и естественным включением ключевых слов."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            article = response.choices[0].message.content
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
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
        pricing = settings.OPENAI_PRICING.get(model, settings.OPENAI_PRICING["gpt-3.5-turbo"])
        
        input_cost = (usage_info["prompt_tokens"] / 1000) * pricing["input"]
        output_cost = (usage_info["completion_tokens"] / 1000) * pricing["output"]
        
        return Decimal(str(input_cost + output_cost)).quantize(Decimal('0.000001')) 