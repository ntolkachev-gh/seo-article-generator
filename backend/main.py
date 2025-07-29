from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import asyncio

from database import get_db, engine
from models import Base
import crud
import schemas
from services.serp_service import SERPService
from services.ai_service import AIService  # Изменено на AIService для поддержки разных провайдеров
from services.seo_service import SEOService
from config import settings

# Создаем таблицы только при запуске приложения
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SEO Article Generator",
    description="API для генерации SEO-статей с помощью ИИ",
    version="2.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "https://localhost:3000",
        "https://seo-article-generator-app-8a9fa9a58cbb.herokuapp.com",
        "https://seo-article-generator.vercel.app",
        "https://seo-article-generator-git-main.vercel.app",
        "https://seo-article-generator-git-main-seo-article-generator.vercel.app",
        "*"  # Временно разрешаем все домены для отладки
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Инициализация сервисов
serp_service = SERPService()
ai_service = AIService()  # Изменено на AIService
seo_service = SEOService()

@app.get("/")
async def root():
    return {"message": "SEO Article Generator API"}

@app.options("/api/articles/generate")
async def options_generate_article():
    """Обработчик OPTIONS запросов для CORS preflight"""
    return {"message": "OK"}

@app.options("/api/articles")
async def options_articles():
    """Обработчик OPTIONS запросов для списка статей"""
    return {"message": "OK"}

@app.options("/api/articles/{article_id}")
async def options_article(article_id: str):
    """Обработчик OPTIONS запросов для отдельной статьи"""
    return {"message": "OK"}

@app.options("/api/models")
async def options_models():
    """Обработчик OPTIONS запросов для моделей"""
    return {"message": "OK"}

@app.options("/api/health")
async def options_health():
    """Обработчик OPTIONS запросов для health check"""
    return {"message": "OK"}

@app.post("/api/articles/generate", response_model=schemas.GenerationResponse)
async def generate_article(
    request: schemas.GenerationRequest,
    db: Session = Depends(get_db)
):
    """Генерирует новую SEO-статью"""
    try:
        # Проверяем доступность модели перед началом генерации
        if not ai_service.is_model_available(request.model):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Модель {request.model} недоступна. Проверьте настройки API ключей."
            )
        
        # 1. Анализ SERP
        serp_data = serp_service.analyze_topic(request.topic)
        keywords = serp_data["keywords"]
        questions = serp_data["questions"]
        
        # 2. Генерация структуры статьи
        structure, structure_usage = ai_service.generate_structure(
            request.topic, 
            request.thesis, 
            keywords, 
            questions, 
            request.model
        )
        
        # 3. Генерация полной статьи с новыми параметрами
        article_text, article_usage = ai_service.generate_article(
            request.topic,
            request.thesis,
            structure,
            keywords,
            request.style_examples or "",  # Добавлен параметр style_examples
            request.character_count or 5000,  # Добавлен параметр character_count
            request.model
        )
        
        # 4. Расчет SEO-оценки
        seo_score = seo_service.calculate_seo_score(article_text, keywords)
        
        # 5. Сохранение в базу данных с новыми полями
        article_data = {
            "topic": request.topic,
            "thesis": request.thesis,
            "style_examples": request.style_examples or "",  # Добавлено
            "character_count": request.character_count or 5000,  # Добавлено
            "keywords": keywords,
            "structure": structure,
            "article": article_text,
            "seo_score": seo_score,
            "model_used": request.model
        }
        
        db_article = crud.create_article(db, article_data)
        
        # 6. Сохранение информации об использовании OpenAI
        total_usage = {
            "prompt_tokens": structure_usage["prompt_tokens"] + article_usage["prompt_tokens"],
            "completion_tokens": structure_usage["completion_tokens"] + article_usage["completion_tokens"],
            "total_tokens": structure_usage["total_tokens"] + article_usage["total_tokens"]
        }
        
        cost = ai_service.calculate_cost(total_usage, request.model)  # Изменено на ai_service
        
        usage_data = {
            "article_id": db_article.id,
            "model": request.model,
            "prompt_tokens": total_usage["prompt_tokens"],
            "completion_tokens": total_usage["completion_tokens"],
            "total_tokens": total_usage["total_tokens"],
            "cost_usd": cost
        }
        
        db_usage = crud.create_openai_usage(db, usage_data)
        
        return schemas.GenerationResponse(
            article_id=db_article.id,
            topic=db_article.topic,
            thesis=db_article.thesis,
            style_examples=getattr(db_article, 'style_examples', ''),  # Добавлено
            character_count=getattr(db_article, 'character_count', 5000),  # Добавлено
            keywords=db_article.keywords,
            structure=db_article.structure,
            article=db_article.article,
            seo_score=db_article.seo_score,
            model_used=db_article.model_used,
            usage=schemas.OpenAIUsageResponse.from_orm(db_usage)
        )
        
    except ValueError as e:
        # Специальная обработка для ошибок сервисов
        if "API" in str(e) and "key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Сервис AI недоступен: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка валидации: {str(e)}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка генерации статьи: {str(e)}"
        )

@app.get("/api/articles", response_model=List[schemas.ArticleListResponse])
async def get_articles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получает список всех статей"""
    articles = crud.get_articles(db, skip=skip, limit=limit)
    return articles

@app.get("/api/articles/{article_id}", response_model=schemas.ArticleResponse)
async def get_article(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    """Получает статью по ID"""
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена"
        )
    return article

@app.delete("/api/articles/{article_id}")
async def delete_article(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    """Удаляет статью"""
    success = crud.delete_article(db, article_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена"
        )
    return {"message": "Статья успешно удалена"}

@app.get("/api/articles/{article_id}/seo-recommendations")
async def get_seo_recommendations(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    """Получает SEO-рекомендации для статьи"""
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена"
        )
    
    recommendations = seo_service.get_seo_recommendations(
        article.article, 
        article.keywords, 
        article.seo_score
    )
    
    return {
        "article_id": article_id,
        "seo_score": article.seo_score,
        "recommendations": recommendations
    }

@app.get("/api/health")
async def health_check():
    """Проверка здоровья API"""
    try:
        # Проверяем доступность сервисов
        openai_available = ai_service.openai_service is not None
        anthropic_available = ai_service.anthropic_service is not None
        
        return {
            "status": "healthy",
            "message": "Service is running",
            "version": "2.0.0",
            "services": {
                "openai": openai_available,
                "anthropic": anthropic_available,
                "serp": True,  # SERP service is always available
                "seo": True    # SEO service is always available
            },
            "available_models": len(ai_service.get_available_models())
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Service error: {str(e)}",
            "version": "2.0.0",
            "services": {
                "openai": False,
                "anthropic": False,
                "serp": False,
                "seo": False
            },
            "available_models": 0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 