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
from services.openai_service import OpenAIService
from services.seo_service import SEOService
from config import settings

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SEO Article Generator",
    description="API для генерации SEO-статей с помощью OpenAI",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация сервисов
serp_service = SERPService()
openai_service = OpenAIService()
seo_service = SEOService()

@app.get("/")
async def root():
    return {"message": "SEO Article Generator API"}

@app.post("/api/articles/generate", response_model=schemas.GenerationResponse)
async def generate_article(
    request: schemas.GenerationRequest,
    db: Session = Depends(get_db)
):
    """Генерирует новую SEO-статью"""
    try:
        # 1. Анализ SERP
        serp_data = serp_service.analyze_topic(request.topic)
        keywords = serp_data["keywords"]
        questions = serp_data["questions"]
        
        # 2. Генерация структуры статьи
        structure, structure_usage = openai_service.generate_structure(
            request.topic, 
            request.thesis, 
            keywords, 
            questions, 
            request.model
        )
        
        # 3. Генерация полной статьи
        article_text, article_usage = openai_service.generate_article(
            request.topic,
            request.thesis,
            structure,
            keywords,
            request.model
        )
        
        # 4. Расчет SEO-оценки
        seo_score = seo_service.calculate_seo_score(article_text, keywords)
        
        # 5. Сохранение в базу данных
        article_data = {
            "topic": request.topic,
            "thesis": request.thesis,
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
        
        cost = openai_service.calculate_cost(total_usage, request.model)
        
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
            keywords=db_article.keywords,
            structure=db_article.structure,
            article=db_article.article,
            seo_score=db_article.seo_score,
            model_used=db_article.model_used,
            usage=schemas.OpenAIUsageResponse.from_orm(db_usage)
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
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 