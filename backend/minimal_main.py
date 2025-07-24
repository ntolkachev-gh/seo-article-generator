#!/usr/bin/env python3
"""
Minimal FastAPI app for Heroku deployment
"""

import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid

app = FastAPI(
    title="SEO Article Generator",
    description="API для генерации SEO-статей с помощью OpenAI",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple data models
class GenerationRequest(BaseModel):
    topic: str
    thesis: str
    model: str

class OpenAIUsageResponse(BaseModel):
    id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    created_at: datetime

class GenerationResponse(BaseModel):
    id: str
    topic: str
    thesis: str
    keywords: List[str]
    structure: str
    article: str
    seo_score: float
    model_used: str
    created_at: datetime
    openai_usage: OpenAIUsageResponse

class ArticleListResponse(BaseModel):
    id: str
    topic: str
    thesis: str
    seo_score: float
    model_used: str
    created_at: datetime

# In-memory storage (for demo purposes)
articles_db = []

@app.get("/")
async def root():
    return {"message": "SEO Article Generator API is running!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

@app.post("/api/articles/generate", response_model=GenerationResponse)
async def generate_article(request: GenerationRequest):
    try:
        # Generate a mock article for demo
        article_id = str(uuid.uuid4())
        
        # Mock data
        keywords = ["SEO", "оптимизация", "контент", "статья", request.topic.lower()]
        structure = f"""# {request.topic}

## Введение
Краткое введение в тему.

## Основная часть
{request.thesis}

## Заключение
Подведение итогов.

## Ключевые моменты
- Пункт 1
- Пункт 2
- Пункт 3"""
        
        article_text = f"""# {request.topic}

## Введение

{request.topic} - это важная тема, которая интересует многих людей. В данной статье мы рассмотрим основные аспекты и предоставим полезную информацию.

## Основная часть

{request.thesis}

Этот раздел содержит подробную информацию по теме. Мы рассмотрим различные подходы и методы, которые помогут лучше понять предмет.

### Подраздел 1

Здесь мы детально разбираем первый аспект темы. Важно отметить, что правильный подход к решению проблемы может значительно улучшить результаты.

### Подраздел 2

Второй аспект не менее важен. Рассмотрим практические примеры и рекомендации экспертов.

## Заключение

Подводя итоги, можно сказать, что {request.topic} требует внимательного изучения и практического применения. Используя полученные знания, вы сможете достичь лучших результатов.

## Ключевые моменты

- Важность правильного подхода
- Практическое применение
- Постоянное развитие навыков

Надеемся, что данная статья была полезной и информативной."""
        
        seo_score = 8.5  # Mock SEO score
        
        # Create article object
        article = {
            'id': article_id,
            'topic': request.topic,
            'thesis': request.thesis,
            'keywords': keywords,
            'structure': structure,
            'article': article_text,
            'seo_score': seo_score,
            'model_used': request.model,
            'created_at': datetime.utcnow()
        }
        
        # Store in memory
        articles_db.append(article)
        
        # Mock OpenAI usage
        usage = OpenAIUsageResponse(
            id=str(uuid.uuid4()),
            model=request.model,
            prompt_tokens=1500,
            completion_tokens=800,
            total_tokens=2300,
            cost_usd=0.05,
            created_at=datetime.utcnow()
        )
        
        return GenerationResponse(
            id=article['id'],
            topic=article['topic'],
            thesis=article['thesis'],
            keywords=article['keywords'],
            structure=article['structure'],
            article=article['article'],
            seo_score=article['seo_score'],
            model_used=article['model_used'],
            created_at=article['created_at'],
            openai_usage=usage
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating article: {str(e)}"
        )

@app.get("/api/articles", response_model=List[ArticleListResponse])
async def get_articles(skip: int = 0, limit: int = 100):
    articles = articles_db[skip:skip + limit]
    return [
        ArticleListResponse(
            id=article['id'],
            topic=article['topic'],
            thesis=article['thesis'],
            seo_score=article['seo_score'],
            model_used=article['model_used'],
            created_at=article['created_at']
        )
        for article in articles
    ]

@app.get("/api/articles/{article_id}", response_model=GenerationResponse)
async def get_article(article_id: str):
    article = next((a for a in articles_db if a['id'] == article_id), None)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Mock OpenAI usage
    usage = OpenAIUsageResponse(
        id=str(uuid.uuid4()),
        model=article['model_used'],
        prompt_tokens=1500,
        completion_tokens=800,
        total_tokens=2300,
        cost_usd=0.05,
        created_at=article['created_at']
    )
    
    return GenerationResponse(
        id=article['id'],
        topic=article['topic'],
        thesis=article['thesis'],
        keywords=article['keywords'],
        structure=article['structure'],
        article=article['article'],
        seo_score=article['seo_score'],
        model_used=article['model_used'],
        created_at=article['created_at'],
        openai_usage=usage
    )

@app.delete("/api/articles/{article_id}")
async def delete_article(article_id: str):
    global articles_db
    articles_db = [a for a in articles_db if a['id'] != article_id]
    return {"message": "Article deleted successfully"} 