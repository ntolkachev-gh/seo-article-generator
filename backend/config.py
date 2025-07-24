import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/seo_articles")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
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
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "gpt-4": {"input": 0.03, "output": 0.06}
    }

settings = Settings() 