from typing import Dict, List, Tuple, Optional
from decimal import Decimal
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class AIService:
    def __init__(self):
        self.openai_service = None
        self.anthropic_service = None
        
        # Инициализируем сервисы только если есть соответствующие API ключи
        try:
            from services.openai_service import OpenAIService
            if settings.OPENAI_API_KEY:
                self.openai_service = OpenAIService()
                print("OpenAI service initialized successfully")
        except Exception as e:
            print(f"Failed to initialize OpenAI service: {e}")
        
        try:
            from services.anthropic_service import AnthropicService
            if settings.ANTHROPIC_API_KEY:
                self.anthropic_service = AnthropicService()
                print("Anthropic service initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Anthropic service: {e}")
    
    def get_provider_for_model(self, model: str) -> str:
        """Определяет провайдера для конкретной модели"""
        # Находим модель в списке доступных
        for model_info in settings.AVAILABLE_MODELS:
            if model_info["id"] == model:
                return model_info["provider"]
        
        # Если модель не найдена, определяем по названию
        if model.startswith("claude"):
            return "anthropic"
        else:
            return "openai"
    
    def get_service_for_model(self, model: str):
        """Получает соответствующий сервис для модели"""
        provider = self.get_provider_for_model(model)
        
        if provider == "anthropic":
            if not self.anthropic_service:
                raise ValueError(f"Anthropic service not available for model {model}. Please check ANTHROPIC_API_KEY.")
            return self.anthropic_service
        else:
            if not self.openai_service:
                raise ValueError(f"OpenAI service not available for model {model}. Please check OPENAI_API_KEY.")
            return self.openai_service
    
    def generate_structure(self, topic: str, thesis: str, keywords: List[str], 
                          questions: List[str], model: str = "gpt-4o-mini") -> Tuple[str, Dict]:
        """Генерирует структуру статьи, автоматически выбирая провайдера"""
        service = self.get_service_for_model(model)
        return service.generate_structure(topic, thesis, keywords, questions, model)
    
    def generate_article(self, topic: str, thesis: str, structure: str, 
                        keywords: List[str], model: str = "gpt-4o-mini") -> Tuple[str, Dict]:
        """Генерирует полный текст статьи, автоматически выбирая провайдера"""
        service = self.get_service_for_model(model)
        return service.generate_article(topic, thesis, structure, keywords, model)
    
    def calculate_cost(self, usage_info: Dict, model: str) -> Decimal:
        """Рассчитывает стоимость использования API"""
        service = self.get_service_for_model(model)
        return service.calculate_cost(usage_info, model)
    
    def is_model_available(self, model: str) -> bool:
        """Проверяет доступность модели"""
        try:
            provider = self.get_provider_for_model(model)
            if provider == "anthropic":
                return self.anthropic_service is not None
            else:
                return self.openai_service is not None
        except:
            return False
    
    def get_available_models(self) -> List[Dict]:
        """Возвращает список доступных моделей с учетом доступности сервисов"""
        available_models = []
        
        for model_info in settings.AVAILABLE_MODELS:
            model_id = model_info["id"]
            provider = model_info["provider"]
            
            # Проверяем доступность сервиса
            if provider == "anthropic" and self.anthropic_service:
                available_models.append(model_info)
            elif provider == "openai" and self.openai_service:
                available_models.append(model_info)
        
        return available_models
    
    def get_model_pricing(self, model: str) -> Optional[Dict]:
        """Получает информацию о ценах для модели"""
        provider = self.get_provider_for_model(model)
        
        if provider == "anthropic":
            return settings.ANTHROPIC_PRICING.get(model)
        else:
            return settings.OPENAI_PRICING.get(model) 