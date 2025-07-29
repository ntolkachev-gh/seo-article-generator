import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/seo_articles")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")  # Новый ключ для Claude
    SERP_API_KEY: str = os.getenv("SERP_API_KEY", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    @property
    def database_url_fixed(self) -> str:
        """Fix DATABASE_URL for SQLAlchemy 2.0+ compatibility"""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    
    # OpenAI pricing per 1K tokens (as of 2024)
    OPENAI_PRICING = {
        # GPT-3.5 Models
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
        
        # GPT-4 Models
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-32k": {"input": 0.06, "output": 0.12},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        
        # GPT-4o Models (Latest)
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        
        # Legacy Models
        "gpt-3.5-turbo-instruct": {"input": 0.0015, "output": 0.002},
        "text-davinci-003": {"input": 0.02, "output": 0.02},
    }
    
    # Anthropic pricing per 1K tokens (as of 2024)
    ANTHROPIC_PRICING = {
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-5-haiku-20241022": {"input": 0.00025, "output": 0.00125},
    }
    
    # Combined pricing for all models
    @property
    def ALL_PRICING(self):
        return {**self.OPENAI_PRICING, **self.ANTHROPIC_PRICING}
    
    # Available models for selection
    AVAILABLE_MODELS = [
        # Fast and cost-effective
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Самый быстрый и дешевый", "category": "fast", "provider": "openai"},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Быстрый и экономичный", "category": "fast", "provider": "openai"},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "description": "Быстрый и дешевый", "category": "fast", "provider": "anthropic"},
        
        # Balanced
        {"id": "gpt-4o", "name": "GPT-4o", "description": "Оптимальное качество и скорость", "category": "balanced", "provider": "openai"},
        {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Высокое качество", "category": "balanced", "provider": "openai"},
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "description": "Сбалансированное качество", "category": "balanced", "provider": "anthropic"},
        
        # High quality
        {"id": "gpt-4", "name": "GPT-4", "description": "Максимальное качество", "category": "quality", "provider": "openai"},
        {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "description": "Альтернатива GPT-4", "category": "quality", "provider": "anthropic"},
        
        # Premium
        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "description": "Премиум качество", "category": "premium", "provider": "anthropic"},
        {"id": "gpt-4-32k", "name": "GPT-4 32K", "description": "Длинные контексты", "category": "premium", "provider": "openai"},
    ]

settings = Settings() 