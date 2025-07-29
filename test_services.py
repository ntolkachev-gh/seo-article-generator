#!/usr/bin/env python3
"""
Тест инициализации сервисов
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config import settings
from backend.services.ai_service import AIService

print("🔍 Тестирование инициализации сервисов:")
print("=" * 50)

print(f"OPENAI_API_KEY: {'✅ Установлен' if settings.OPENAI_API_KEY else '❌ НЕ УСТАНОВЛЕН'}")
print(f"ANTHROPIC_API_KEY: {'✅ Установлен' if settings.ANTHROPIC_API_KEY else '❌ НЕ УСТАНОВЛЕН'}")

try:
    print("\n🔄 Инициализация AIService...")
    ai_service = AIService()
    
    print(f"OpenAI service: {'✅ Доступен' if ai_service.openai_service else '❌ Недоступен'}")
    print(f"Anthropic service: {'✅ Доступен' if ai_service.anthropic_service else '❌ Недоступен'}")
    
    if ai_service.openai_service or ai_service.anthropic_service:
        print("\n📋 Доступные модели:")
        models = ai_service.get_available_models()
        for model in models:
            print(f"  - {model['name']} ({model['provider']})")
    else:
        print("❌ Ни один сервис не доступен")
        
except Exception as e:
    print(f"❌ Ошибка инициализации: {e}")
    import traceback
    traceback.print_exc() 