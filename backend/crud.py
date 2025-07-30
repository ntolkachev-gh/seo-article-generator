from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import models
import schemas

def create_article(db: Session, article_data: dict) -> models.Article:
    """Создает новую статью"""
    db_article = models.Article(**article_data)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def create_article_for_async_generation(db: Session, request: schemas.GenerationRequest) -> models.Article:
    """Создает статью с минимальными данными для асинхронной генерации"""
    article_data = {
        "topic": request.topic,
        "thesis": request.thesis,
        "style_examples": request.style_examples or "",
        "character_count": request.character_count or 5000,
        "model_used": request.model,
        "status": models.ArticleStatus.PENDING,
        "keywords": None,
        "structure": None,
        "article": None,
        "seo_score": None,
        "error_message": None
    }
    
    db_article = models.Article(**article_data)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def update_article_status(db: Session, article_id: UUID, status: models.ArticleStatus, error_message: Optional[str] = None) -> bool:
    """Обновляет статус статьи"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if article:
        article.status = status
        article.updated_at = datetime.utcnow()
        if error_message:
            article.error_message = error_message
        db.commit()
        return True
    return False

def update_article_content(db: Session, article_id: UUID, content_data: dict) -> bool:
    """Обновляет содержимое статьи после генерации"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if article:
        for key, value in content_data.items():
            if hasattr(article, key):
                setattr(article, key, value)
        article.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False

def create_openai_usage(db: Session, usage_data: dict) -> models.OpenAIUsage:
    """Создает запись об использовании OpenAI"""
    db_usage = models.OpenAIUsage(**usage_data)
    db.add(db_usage)
    db.commit()
    db.refresh(db_usage)
    return db_usage

def get_article(db: Session, article_id: UUID) -> Optional[models.Article]:
    """Получает статью по ID"""
    return db.query(models.Article).filter(models.Article.id == article_id).first()

def get_articles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Article]:
    """Получает список статей с пагинацией, отсортированный по дате обновления"""
    return db.query(models.Article).order_by(models.Article.updated_at.desc()).offset(skip).limit(limit).all()

def get_articles_by_status(db: Session, status: models.ArticleStatus, skip: int = 0, limit: int = 100) -> List[models.Article]:
    """Получает список статей по статусу"""
    return db.query(models.Article).filter(models.Article.status == status).order_by(models.Article.updated_at.desc()).offset(skip).limit(limit).all()

def get_pending_articles(db: Session) -> List[models.Article]:
    """Получает список статей, ожидающих генерации"""
    return db.query(models.Article).filter(models.Article.status == models.ArticleStatus.PENDING).all()

def get_article_usage(db: Session, article_id: UUID) -> List[models.OpenAIUsage]:
    """Получает информацию об использовании OpenAI для статьи"""
    return db.query(models.OpenAIUsage).filter(models.OpenAIUsage.article_id == article_id).all()

def delete_article(db: Session, article_id: UUID) -> bool:
    """Удаляет статью"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if article:
        db.delete(article)
        db.commit()
        return True
    return False 