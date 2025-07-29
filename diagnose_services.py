#!/usr/bin/env python3
"""
🔧 Полная диагностика SEO Article Generator
Проверяет все компоненты системы для выявления источника ошибки 500
"""

import sys
import os
import traceback
import asyncio
from datetime import datetime

# Добавляем backend в путь
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

print("🔧 ДИАГНОСТИКА SEO ARTICLE GENERATOR")
print("=" * 60)
print(f"🕐 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 1. Проверка переменных окружения
print("1️⃣ ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
print("-" * 40)

try:
    from backend.config import settings
    
    print(f"OPENAI_API_KEY: {'✅ Установлен' if settings.OPENAI_API_KEY else '❌ НЕ УСТАНОВЛЕН'}")
    print(f"ANTHROPIC_API_KEY: {'✅ Установлен' if settings.ANTHROPIC_API_KEY else '❌ НЕ УСТАНОВЛЕН'}")
    print(f"SERP_API_KEY: {'✅ Установлен' if settings.SERP_API_KEY else '❌ НЕ УСТАНОВЛЕН'}")
    print(f"DATABASE_URL: {'✅ Установлен' if settings.DATABASE_URL else '❌ НЕ УСТАНОВЛЕН'}")
    print(f"FRONTEND_URL: {settings.FRONTEND_URL}")
except Exception as e:
    print(f"❌ Ошибка загрузки конфигурации: {e}")
    traceback.print_exc()

print()

# 2. Проверка подключения к базе данных
print("2️⃣ ПРОВЕРКА БАЗЫ ДАННЫХ")
print("-" * 40)

try:
    from backend.database import engine, get_db
    from backend.models import Base
    
    # Проверяем подключение
    with engine.connect() as conn:
        from sqlalchemy import text
        result = conn.execute(text("SELECT 1"))
        print("✅ Подключение к БД: УСПЕШНО")
    
    # Проверяем таблицы
    Base.metadata.create_all(bind=engine)
    print("✅ Создание таблиц: УСПЕШНО")
    
except Exception as e:
    print(f"❌ Ошибка БД: {e}")
    traceback.print_exc()

print()

# 3. Проверка AI сервисов
print("3️⃣ ПРОВЕРКА AI СЕРВИСОВ")
print("-" * 40)

try:
    from backend.services.ai_service import AIService
    
    ai_service = AIService()
    print(f"OpenAI сервис: {'✅ Доступен' if ai_service.openai_service else '❌ Недоступен'}")
    print(f"Anthropic сервис: {'✅ Доступен' if ai_service.anthropic_service else '❌ Недоступен'}")
    
    if ai_service.openai_service or ai_service.anthropic_service:
        models = ai_service.get_available_models()
        print(f"✅ Доступно моделей: {len(models)}")
        for model in models[:3]:  # Показываем первые 3
            print(f"   - {model['name']} ({model['provider']})")
    else:
        print("❌ Ни один AI сервис не доступен!")
        
except Exception as e:
    print(f"❌ Ошибка AI сервисов: {e}")
    traceback.print_exc()

print()

# 4. Проверка SERP сервиса
print("4️⃣ ПРОВЕРКА SERP СЕРВИСА")
print("-" * 40)

try:
    from backend.services.serp_service import SERPService
    
    serp_service = SERPService()
    print("✅ SERP сервис инициализирован")
    
    # Тестовый поиск
    test_topic = "искусственный интеллект"
    print(f"🔍 Тестируем поиск по теме: '{test_topic}'")
    
    serp_data = serp_service.analyze_topic(test_topic)
    print(f"✅ Поиск выполнен успешно:")
    print(f"   - Ключевых слов: {len(serp_data.get('keywords', []))}")
    print(f"   - Заголовков: {len(serp_data.get('titles', []))}")
    print(f"   - Вопросов: {len(serp_data.get('questions', []))}")
    
except Exception as e:
    print(f"❌ Ошибка SERP сервиса: {e}")
    traceback.print_exc()

print()

# 5. Проверка SEO сервиса
print("5️⃣ ПРОВЕРКА SEO СЕРВИСА")
print("-" * 40)

try:
    from backend.services.seo_service import SEOService
    
    seo_service = SEOService()
    print("✅ SEO сервис инициализирован")
    
    # Тестовый расчет SEO
    test_text = "Искусственный интеллект - это технология будущего."
    test_keywords = ["искусственный", "интеллект", "технология"]
    
    seo_score = seo_service.calculate_seo_score(test_text, test_keywords)
    print(f"✅ SEO расчет выполнен: оценка = {seo_score}")
    
except Exception as e:
    print(f"❌ Ошибка SEO сервиса: {e}")
    traceback.print_exc()

print()

# 6. Проверка CRUD операций
print("6️⃣ ПРОВЕРКА CRUD ОПЕРАЦИЙ")
print("-" * 40)

try:
    import backend.crud as crud
    from backend.database import get_db
    
    # Получаем сессию БД
    db = next(get_db())
    
    # Тестовые данные
    test_article_data = {
        "topic": "Тестовая статья",
        "thesis": "Тестовый тезис",
        "style_examples": "",
        "character_count": 1000,
        "keywords": ["тест", "диагностика"],
        "structure": "# Заголовок\n## Подзаголовок",
        "article": "Это тестовая статья для диагностики.",
        "seo_score": 75.0,
        "model_used": "gpt-4o-mini"
    }
    
    # Создаем статью
    article = crud.create_article(db, test_article_data)
    print(f"✅ Создание статьи: ID = {article.id}")
    
    # Получаем статьи
    articles = crud.get_articles(db, skip=0, limit=1)
    print(f"✅ Получение статей: найдено {len(articles)}")
    
    # Удаляем тестовую статью
    crud.delete_article(db, article.id)
    print("✅ Удаление тестовой статьи: УСПЕШНО")
    
    db.close()
    
except Exception as e:
    print(f"❌ Ошибка CRUD операций: {e}")
    traceback.print_exc()

print()

# 7. Тестовая генерация (если есть AI сервисы)
print("7️⃣ ТЕСТОВАЯ ГЕНЕРАЦИЯ")
print("-" * 40)

try:
    if 'ai_service' in locals() and (ai_service.openai_service or ai_service.anthropic_service):
        print("🧪 Выполняем тестовую генерацию...")
        
        test_topic = "Python программирование" 
        test_thesis = "Python - лучший язык для начинающих"
        test_keywords = ["python", "программирование", "обучение"]
        test_questions = ["Что такое Python?", "Как изучить Python?"]
        
        # Тест генерации структуры
        model = "gpt-4o-mini" if ai_service.openai_service else "claude-3-5-haiku-20241022"
        
        if ai_service.is_model_available(model):
            structure, usage = ai_service.generate_structure(
                test_topic, test_thesis, test_keywords, test_questions, model
            )
            print(f"✅ Генерация структуры: УСПЕШНО (токенов: {usage.get('total_tokens', 0)})")
            print(f"   Длина структуры: {len(structure)} символов")
        else:
            print(f"⚠️ Модель {model} недоступна для тестирования")
    else:
        print("⚠️ AI сервисы недоступны - пропускаем тестовую генерацию")
        
except Exception as e:
    print(f"❌ Ошибка тестовой генерации: {e}")
    traceback.print_exc()

print()

# 8. Итоговая сводка
print("8️⃣ ИТОГОВАЯ СВОДКА")
print("-" * 40)

print("📋 Статус компонентов:")
print("   🔧 Конфигурация: проверена")
print("   🗄️ База данных: проверена") 
print("   🤖 AI сервисы: проверены")
print("   🔍 SERP сервис: проверен")
print("   📈 SEO сервис: проверен")
print("   💾 CRUD операции: проверены")

print()
print("🎯 РЕКОМЕНДАЦИИ ДЛЯ ОТЛАДКИ:")
print("1. Запустите сервер с подробным логированием:")
print("   cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug")
print()
print("2. Проверьте логи в реальном времени при ошибке 500")
print()
print("3. Если проблема в API ключах - установите переменные окружения:")
print("   export OPENAI_API_KEY='your-key'")
print("   export ANTHROPIC_API_KEY='your-key'") 
print()
print("4. Для детальной диагностики запустите тест генерации:")
print("   python diagnose_services.py")

print()
print("=" * 60)
print("🏁 ДИАГНОСТИКА ЗАВЕРШЕНА") 