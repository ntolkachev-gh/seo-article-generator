from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import asyncio
import logging
import traceback
import aiohttp
import json
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from database import get_db, engine
from models import Base, ArticleStatus
import models
import crud
import schemas
from services.serp_service import SERPService
from services.ai_service import AIService  # Изменено на AIService для поддержки разных провайдеров
from services.seo_service import SEOService
from services.background_tasks import background_task_manager
from config import settings

# Создаем таблицы только при запуске приложения
# Base.metadata.create_all(bind=engine)

# Webhook configuration
N8N_WEBHOOK_URL = "https://n8n.tech.ai-community.com/webhook/generate-article"

async def send_webhook_to_n8n(article_id: str, article_data: dict = None):
    """Отправляет webhook на n8n с Article ID и дополнительными данными"""
    try:
        payload = {
            "article_id": article_id,
            "timestamp": asyncio.get_event_loop().time(),
            "event": "article_created",
            "status": "pending"
        }
        
        # Добавляем дополнительную информацию о статье, если передана
        if article_data:
            payload.update({
                "topic": article_data.get("topic"),
                "thesis": article_data.get("thesis", "")[:200] + "..." if len(article_data.get("thesis", "")) > 200 else article_data.get("thesis", ""),  # Обрезаем длинный тезис
                "model_used": article_data.get("model_used"),
                "character_count": article_data.get("character_count")
            })
        
        logger.info(f"🔗 Отправляем webhook на n8n для статьи {article_id}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                N8N_WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10)  # 10 секунд таймаут
            ) as response:
                if response.status == 200:
                    logger.info(f"✅ Webhook успешно отправлен на n8n для статьи {article_id}")
                else:
                    logger.warning(f"⚠️ Webhook вернул статус {response.status} для статьи {article_id}")
                    
    except asyncio.TimeoutError:
        logger.error(f"❌ Таймаут при отправке webhook на n8n для статьи {article_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки webhook на n8n для статьи {article_id}: {str(e)}")
        # Не прерываем выполнение, если webhook не работает

app = FastAPI(
    title="SEO Article Generator",
    description="API для генерации SEO-статей с помощью ИИ",
    version="0.2.0"
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

@app.options("/api/articles/generate-async")
async def options_generate_article_async():
    """Обработчик OPTIONS запросов для асинхронной генерации"""
    return {"message": "OK"}

@app.options("/api/articles/{article_id}/status")
async def options_article_status(article_id: str):
    """Обработчик OPTIONS запросов для статуса статьи"""
    return {"message": "OK"}

@app.options("/api/articles/{article_id}/complete")
async def options_complete_article(article_id: str):
    """Обработчик OPTIONS запросов для завершения статьи"""
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

@app.get("/api/models", response_model=schemas.ModelsResponse)
async def get_available_models():
    """Получить список доступных моделей с информацией о ценах"""
    models = []
    
    # Получаем доступные модели из AI сервиса
    available_models = ai_service.get_available_models()
    
    for model_info in available_models:
        models.append(schemas.ModelInfo(
            id=model_info["id"],
            name=model_info["name"],
            description=model_info["description"],
            category=model_info["category"],
            pricing=model_info.get("pricing", {"input": 0, "output": 0})
        ))
    
    return schemas.ModelsResponse(models=models)

@app.options("/api/health")
async def options_health():
    """Обработчик OPTIONS запросов для health check"""
    return {"message": "OK"}

@app.post("/api/articles/generate-async", response_model=schemas.AsyncGenerationResponse)
async def generate_article_async(
    request: schemas.GenerationRequest,
    db: Session = Depends(get_db)
):
    """Сохраняет параметры генерации статьи в базу данных со статусом 'pending' (асинхронный режим)"""
    try:
        logger.info(f"💾 Сохраняем параметры генерации статьи (асинхронно) для темы: {request.topic}")
        
        # Создаем запись статьи с параметрами и статусом "pending"
        logger.info("💾 Создаем запись статьи в базе данных...")
        article_data = {
            "topic": request.topic,
            "thesis": request.thesis,
            "style_examples": request.style_examples or "",
            "character_count": request.character_count or 5000,
            "model_used": request.model,
            "status": ArticleStatus.PENDING,  # Устанавливаем статус "pending"
            "keywords": None,
            "structure": None,
            "article": None,
            "seo_score": None,
            "error_message": None
        }
        
        db_article = crud.create_article(db, article_data)
        logger.info(f"✅ Создана запись статьи с ID: {db_article.id}")
        
        # Отправляем webhook на n8n с Article ID и данными статьи
        article_id_str = str(db_article.id)
        await send_webhook_to_n8n(article_id_str, article_data)
        
        # Возвращаем ответ с информацией о сохраненной статье
        return schemas.AsyncGenerationResponse(
            article_id=article_id_str,
            status="pending",
            message="Параметры генерации сохранены. Статья ожидает генерации.",
            estimated_time=None  # Нет оценки времени, так как генерация не запущена
        )
        
    except Exception as e:
        logger.error(f"Ошибка сохранения параметров генерации (асинхронно): {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сохранения параметров генерации: {str(e)}"
        )

@app.get("/api/articles/{article_id}/status", response_model=schemas.ArticleStatusResponse)
async def get_article_status(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    """Получает статус генерации статьи"""
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена"
        )
    
    # Определяем описание текущего этапа на основе статуса
    progress_descriptions = {
        ArticleStatus.PENDING: "Ожидает начала генерации",
        ArticleStatus.GENERATING: "Генерация в процессе...",
        ArticleStatus.COMPLETED: "Генерация завершена успешно",
        ArticleStatus.FAILED: "Ошибка при генерации"
    }
    
    return schemas.ArticleStatusResponse(
        article_id=str(article_id),
        status=article.status.value,
        progress=progress_descriptions.get(article.status, "Неизвестный статус"),
        error_message=article.error_message,
        created_at=article.created_at.isoformat() if article.created_at else None,
        updated_at=article.updated_at.isoformat() if article.updated_at else None
    )

@app.put("/api/articles/{article_id}/complete", response_model=schemas.ArticleCompletionResponse)
async def complete_article(
    article_id: UUID,
    request: schemas.ArticleCompletionRequest,
    db: Session = Depends(get_db)
):
    """Завершает статью готовым контентом и устанавливает статус 'completed'"""
    try:
        logger.info(f"📝 Завершаем статью {article_id} готовым контентом")
        
        # Проверяем, существует ли статья
        article = crud.get_article(db, article_id)
        if not article:
            logger.error(f"❌ Статья {article_id} не найдена")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Статья не найдена"
            )
        
        # Подготавливаем данные для обновления
        content_data = {
            "keywords": request.keywords,
            "structure": request.structure,
            "article": request.article,
            "seo_score": request.seo_score,
            "status": ArticleStatus.COMPLETED,
            "error_message": None,
            "updated_at": asyncio.get_event_loop().time()
        }
        
        # Обновляем статью
        success = crud.update_article_content(db, article_id, content_data)
        if not success:
            logger.error(f"❌ Не удалось обновить статью {article_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось обновить статью"
            )
        
        # Сохраняем информацию об использовании токенов, если передана
        if request.usage:
            try:
                usage_data = {
                    "article_id": article_id,
                    "model": request.usage.get("model", article.model_used),
                    "prompt_tokens": request.usage.get("prompt_tokens", 0),
                    "completion_tokens": request.usage.get("completion_tokens", 0),
                    "total_tokens": request.usage.get("total_tokens", 0),
                    "cost_usd": request.usage.get("cost_usd", 0.0)
                }
                crud.create_openai_usage(db, usage_data)
                logger.info(f"💰 Сохранена информация об использовании токенов для статьи {article_id}")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось сохранить информацию об использовании: {str(e)}")
        
        logger.info(f"✅ Статья {article_id} успешно завершена")
        
        return schemas.ArticleCompletionResponse(
            article_id=str(article_id),
            status="completed",
            message="Статья успешно завершена и сохранена",
            updated_at=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при завершении статьи {article_id}: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при завершении статьи: {str(e)}"
        )

@app.post("/api/articles/generate", response_model=schemas.GenerationResponse)
async def generate_article(
    request: schemas.GenerationRequest,
    db: Session = Depends(get_db)
):
    """Сохраняет параметры генерации статьи в базу данных со статусом 'pending'"""
    try:
        logger.info(f"💾 Сохраняем параметры генерации статьи для темы: {request.topic}")
        logger.info(f"📊 Параметры запроса: модель={request.model}, тезис={request.thesis}")
        
        # Создаем запись статьи с параметрами и статусом "pending"
        logger.info("💾 Создаем запись статьи в базе данных...")
        article_data = {
            "topic": request.topic,
            "thesis": request.thesis,
            "style_examples": request.style_examples or "",
            "character_count": request.character_count or 5000,
            "model_used": request.model,
            "status": ArticleStatus.PENDING,  # Устанавливаем статус "pending"
            "keywords": None,
            "structure": None,
            "article": None,
            "seo_score": None,
            "error_message": None
        }
        
        db_article = crud.create_article(db, article_data)
        logger.info(f"✅ Создана запись статьи с ID: {db_article.id}")
        
        # Формируем ответ
        logger.info("📤 Формируем ответ...")
        try:
            response = schemas.GenerationResponse(
                article_id=str(db_article.id),
                topic=db_article.topic,
                thesis=db_article.thesis,
                style_examples=db_article.style_examples,
                character_count=db_article.character_count,
                keywords=db_article.keywords,
                structure=db_article.structure,
                article=db_article.article,
                seo_score=db_article.seo_score,
                model_used=db_article.model_used,
                status=db_article.status.value,
                error_message=db_article.error_message,
                usage=None  # Нет использования, так как генерация не запущена
            )
            logger.info(f"✅ Параметры генерации сохранены. ID: {db_article.id}")
            return response
        except Exception as e:
            logger.error(f"❌ Ошибка при формировании ответа: {str(e)}")
            logger.error(f"📝 Подробности ошибки ответа: {traceback.format_exc()}")
            raise
        
    except Exception as e:
        logger.error(f"Ошибка сохранения параметров генерации: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сохранения параметров генерации: {str(e)}"
        )

@app.get("/api/articles", response_model=List[schemas.ArticleListResponse])
async def get_articles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получает список всех статей"""
    articles = crud.get_articles(db, skip=skip, limit=limit)
    return [schemas.ArticleListResponse.from_orm(article) for article in articles]

@app.get("/api/articles/{article_id}", response_model=schemas.GenerationResponse)
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
    
    # Преобразуем ArticleResponse в GenerationResponse
    article_response = schemas.ArticleResponse.from_orm(article)
    
    # Получаем информацию об использовании, если статья завершена
    usage_response = None
    if article.status == ArticleStatus.COMPLETED:
        usage_records = crud.get_article_usage(db, article_id)
        if usage_records:
            usage_response = schemas.OpenAIUsageResponse.from_orm(usage_records[0])
    
    # Если нет данных об использовании, создаем пустой объект для совместимости
    if not usage_response:
        usage_response = schemas.OpenAIUsageResponse(
            id="",
            article_id=str(article_id),
            model=article_response.model_used or "unknown",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            cost_usd="0.00",
            created_at=article_response.created_at
        )
    
    # Создаем GenerationResponse
    generation_response = schemas.GenerationResponse(
        article_id=article_response.id,
        topic=article_response.topic,
        thesis=article_response.thesis,
        style_examples=article_response.style_examples,
        character_count=article_response.character_count,
        keywords=article_response.keywords,
        structure=article_response.structure,
        article=article_response.article,
        seo_score=article_response.seo_score,
        model_used=article_response.model_used,
        status=article_response.status,  # Добавлено
        error_message=article_response.error_message,  # Добавлено
        usage=usage_response
    )
    
    return generation_response

@app.get("/api/articles/{article_id}/generation-params", response_model=schemas.GenerationParamsResponse)
async def get_article_generation_params(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    """Получает параметры генерации статьи по ID"""
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена"
        )
    
    return schemas.GenerationParamsResponse(
        article_id=str(article_id),
        topic=article.topic,
        thesis=article.thesis,
        style_examples=article.style_examples or "",
        character_count=article.character_count or 5000,
        model_used=article.model_used,
        status=article.status.value,
        created_at=article.created_at.isoformat() if article.created_at else None,
        updated_at=article.updated_at.isoformat() if article.updated_at else None
    )

@app.delete("/api/articles/{article_id}")
async def delete_article(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    """Удаляет статью"""
    # Отменяем фоновую задачу, если она запущена
    background_task_manager.cancel_task(article_id)
    
    success = crud.delete_article(db, article_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена"
        )
    return {"message": "Статья успешно удалена"}

@app.delete("/api/articles/cleanup/pending")
async def cleanup_pending_articles(
    db: Session = Depends(get_db)
):
    """Удаляет все статьи в статусе ожидания"""
    try:
        deleted_count = crud.delete_articles_by_status(db, models.ArticleStatus.PENDING)
        logger.info(f"🧹 Удалено {deleted_count} статей в статусе ожидания")
        return {
            "message": f"Удалено {deleted_count} статей в статусе ожидания",
            "deleted_count": deleted_count
        }
    except Exception as e:
        logger.error(f"❌ Ошибка при очистке статей: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при очистке статей: {str(e)}"
        )

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
    
    # Проверяем, что статья завершена
    if article.status != ArticleStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SEO-рекомендации доступны только для завершенных статей"
        )
    
    recommendations = seo_service.get_seo_recommendations(
        article.article, 
        article.keywords, 
        article.seo_score
    )
    
    return {
        "article_id": str(article_id),
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
            "version": "0.2.0",
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
            "version": "0.2.0",
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