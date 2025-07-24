#!/usr/bin/env python3
"""
Simplified FastAPI app for Heroku deployment with full functionality
"""

import os
import sys
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import asyncio

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import all necessary modules
from database import get_db, engine
from models import Base
import crud
import schemas
from services.serp_service import SERPService
from services.openai_service import OpenAIService
from services.seo_service import SEOService
from config import settings

# Create tables when starting the app
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")

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

# Initialize services
serp_service = SERPService()
openai_service = OpenAIService()
seo_service = SEOService()

@app.get("/")
async def root():
    return {"message": "SEO Article Generator API is running!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

@app.post("/api/articles/generate", response_model=schemas.GenerationResponse)
async def generate_article(
    request: schemas.GenerationRequest,
    db: Session = Depends(get_db)
):
    try:
        # 1. SERP Analysis
        print(f"Starting SERP analysis for topic: {request.topic}")
        serp_data = await serp_service.analyze_serp(request.topic)
        
        # 2. Generate Article Structure
        print("Generating article structure...")
        structure = await openai_service.generate_structure(
            request.topic, 
            request.thesis, 
            serp_data['keywords'], 
            serp_data['questions'],
            request.model
        )
        
        # 3. Generate Full Article
        print("Generating full article...")
        article_text = await openai_service.generate_article(
            request.topic,
            structure,
            serp_data['keywords'],
            request.model
        )
        
        # 4. Calculate SEO Score
        print("Calculating SEO score...")
        seo_score = seo_service.calculate_seo_score(article_text, structure)
        
        # 5. Save to Database
        print("Saving to database...")
        article_data = {
            'topic': request.topic,
            'thesis': request.thesis,
            'keywords': serp_data['keywords'],
            'structure': structure,
            'article': article_text,
            'seo_score': seo_score,
            'model_used': request.model
        }
        
        article = crud.create_article(db, article_data)
        
        # 6. Log OpenAI Usage
        usage_data = {
            'article_id': article.id,
            'model': request.model,
            'prompt_tokens': 0,  # Will be updated with actual values
            'completion_tokens': 0,
            'total_tokens': 0,
            'cost_usd': 0.0
        }
        
        openai_usage = crud.create_openai_usage(db, usage_data)
        
        return schemas.GenerationResponse(
            id=str(article.id),
            topic=article.topic,
            thesis=article.thesis,
            keywords=article.keywords,
            structure=article.structure,
            article=article.article,
            seo_score=article.seo_score,
            model_used=article.model_used,
            created_at=article.created_at,
            openai_usage=schemas.OpenAIUsageResponse(
                id=str(openai_usage.id),
                model=openai_usage.model,
                prompt_tokens=openai_usage.prompt_tokens,
                completion_tokens=openai_usage.completion_tokens,
                total_tokens=openai_usage.total_tokens,
                cost_usd=float(openai_usage.cost_usd),
                created_at=openai_usage.created_at
            )
        )
        
    except Exception as e:
        print(f"Error generating article: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating article: {str(e)}"
        )

@app.get("/api/articles", response_model=List[schemas.ArticleListResponse])
async def get_articles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    articles = crud.get_articles(db, skip=skip, limit=limit)
    return [
        schemas.ArticleListResponse(
            id=str(article.id),
            topic=article.topic,
            thesis=article.thesis,
            seo_score=article.seo_score,
            model_used=article.model_used,
            created_at=article.created_at
        )
        for article in articles
    ]

@app.get("/api/articles/{article_id}", response_model=schemas.ArticleResponse)
async def get_article(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    openai_usage = article.openai_usage[0] if article.openai_usage else None
    
    return schemas.ArticleResponse(
        id=str(article.id),
        topic=article.topic,
        thesis=article.thesis,
        keywords=article.keywords,
        structure=article.structure,
        article=article.article,
        seo_score=article.seo_score,
        model_used=article.model_used,
        created_at=article.created_at,
        openai_usage=schemas.OpenAIUsageResponse(
            id=str(openai_usage.id),
            model=openai_usage.model,
            prompt_tokens=openai_usage.prompt_tokens,
            completion_tokens=openai_usage.completion_tokens,
            total_tokens=openai_usage.total_tokens,
            cost_usd=float(openai_usage.cost_usd),
            created_at=openai_usage.created_at
        ) if openai_usage else None
    )

@app.delete("/api/articles/{article_id}")
async def delete_article(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    crud.delete_article(db, article_id)
    return {"message": "Article deleted successfully"}

@app.get("/api/articles/{article_id}/seo-recommendations", response_model=schemas.SEORecommendations)
async def get_seo_recommendations(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    recommendations = seo_service.get_recommendations(article.article, article.structure)
    return schemas.SEORecommendations(
        score=article.seo_score,
        recommendations=recommendations
    ) 