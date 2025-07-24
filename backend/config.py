import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/seo_articles")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    SERP_API_KEY: str = os.getenv("SERP_API_KEY", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # OpenAI pricing per 1K tokens (as of 2024)
    OPENAI_PRICING = {
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "gpt-4": {"input": 0.03, "output": 0.06}
    }

settings = Settings() 