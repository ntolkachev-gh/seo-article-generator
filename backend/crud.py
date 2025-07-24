from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import models
import schemas

def create_article(db: Session, article_data: dict) -> models.Article:
    """Создает новую статью"""
    db_article = models.Article(**article_data)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

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
    """Получает список статей с пагинацией"""
    return db.query(models.Article).order_by(models.Article.created_at.desc()).offset(skip).limit(limit).all()

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