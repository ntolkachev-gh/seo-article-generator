#!/usr/bin/env python3
"""
Простой тест инициализации AI сервисов
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

print("🔧 Тестирование инициализации AI сервисов")
print("=" * 50)

try:
    from backend.config import settings
    print(f"✅ Конфигурация загружена")
    print(f"OPENAI_API_KEY: {'Set' if settings.OPENAI_API_KEY else 'Not set'}")
    print(f"ANTHROPIC_API_KEY: {'Set' if settings.ANTHROPIC_API_KEY else 'Not set'}")
except Exception as e:
    print(f"❌ Ошибка загрузки конфигурации: {e}")
    sys.exit(1)

print("\n🔍 Тестирование OpenAI сервиса...")
try:
    import openai
    print(f"✅ OpenAI библиотека импортирована, версия: {openai.__version__}")
    
    # Тестируем создание клиента
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    print("✅ OpenAI клиент создан успешно")
    
except Exception as e:
    print(f"❌ Ошибка OpenAI: {e}")
    import traceback
    traceback.print_exc()

print("\n🔍 Тестирование Anthropic сервиса...")
try:
    import anthropic
    print(f"✅ Anthropic библиотека импортирована, версия: {anthropic.__version__}")
    
    # Тестируем создание клиента
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    print("✅ Anthropic клиент создан успешно")
    
except Exception as e:
    print(f"❌ Ошибка Anthropic: {e}")
    import traceback
    traceback.print_exc()

print("\n🔍 Тестирование наших сервисов...")
try:
    from backend.services.openai_service import OpenAIService
    openai_service = OpenAIService()
    print("✅ OpenAIService инициализирован успешно")
except Exception as e:
    print(f"❌ Ошибка OpenAIService: {e}")
    import traceback
    traceback.print_exc()

try:
    from backend.services.anthropic_service import AnthropicService
    anthropic_service = AnthropicService()
    print("✅ AnthropicService инициализирован успешно")
except Exception as e:
    print(f"❌ Ошибка AnthropicService: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 Тестирование завершено") 