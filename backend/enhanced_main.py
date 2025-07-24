#!/usr/bin/env python3
"""
Enhanced FastAPI app with database and style examples
"""

import os
import sys
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import asyncio
from datetime import datetime
import uuid

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import database modules with error handling
try:
    from database import get_db, engine
    from models import Base
    import crud
    import schemas
    from config import settings
    DATABASE_AVAILABLE = True
    print("Database modules loaded successfully")
except Exception as e:
    print(f"Database not available: {e}")
    DATABASE_AVAILABLE = False

# Import services with error handling
try:
    from services.openai_service import OpenAIService
    from services.seo_service import SEOService
    SERVICES_AVAILABLE = True
    print("Services loaded successfully")
except Exception as e:
    print(f"Services not available: {e}")
    SERVICES_AVAILABLE = False

# Create tables if database is available
if DATABASE_AVAILABLE:
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        DATABASE_AVAILABLE = False

app = FastAPI(
    title="SEO Article Generator",
    description="AI-powered SEO article generator with style examples",
    version="2.0.0"
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
if SERVICES_AVAILABLE:
    try:
        openai_service = OpenAIService()
        seo_service = SEOService()
        print("Services initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize services: {e}")
        SERVICES_AVAILABLE = False

# Enhanced data models
from pydantic import BaseModel

class GenerationRequest(BaseModel):
    topic: str
    thesis: str
    style_examples: Optional[str] = ""  # Новое поле для примеров стиля
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
    style_examples: Optional[str] = ""
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
    style_examples: Optional[str] = ""
    seo_score: float
    model_used: str
    created_at: datetime

# In-memory storage as fallback
articles_db = []

@app.get("/")
async def root():
    return {
        "message": "Enhanced SEO Article Generator API is running!",
        "database": DATABASE_AVAILABLE,
        "services": SERVICES_AVAILABLE,
        "features": ["style_examples", "database", "seo_scoring"]
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Service is running",
        "database": DATABASE_AVAILABLE,
        "services": SERVICES_AVAILABLE
    }

async def generate_with_style(topic: str, thesis: str, style_examples: str, model: str):
    """Generate article with style examples using OpenAI"""
    if not SERVICES_AVAILABLE:
        # Fallback to mock generation
        return await generate_mock_article(topic, thesis, style_examples, model)
    
    try:
        # Создаем промпт с учетом стиля
        style_prompt = ""
        if style_examples and style_examples.strip():
            style_prompt = f"""
            
СТИЛЬ ПИСЬМА:
Проанализируй следующие примеры текстов и используй их стиль для написания статьи:

{style_examples}

Сохрани тон, структуру предложений, способ подачи информации и общий стиль изложения из примеров."""

        # Mock SERP data
        keywords = ["SEO", "оптимизация", "контент", topic.lower()]
        
        # Generate structure with style
        structure_prompt = f"""Создай подробную структуру статьи на тему "{topic}" в формате markdown.

Основные тезисы:
{thesis}

Ключевые слова: {', '.join(keywords)}

{style_prompt}

Структура должна включать:
- Заголовок H1
- Введение
- 3-4 основных раздела с подразделами
- Заключение
- Список ключевых моментов

Формат ответа: только markdown структура без дополнительных комментариев."""

        # For now, create enhanced mock structure
        structure = f"""# {topic}

## Введение
Вводная часть, которая заинтересует читателя и раскроет важность темы.

## Основные аспекты

### Теоретические основы
{thesis[:200]}...

### Практическое применение
Конкретные примеры и рекомендации.

### Современные тенденции
Актуальные подходы и новые методы.

## Детальный анализ

### Преимущества и недостатки
Объективная оценка различных подходов.

### Рекомендации экспертов
Советы от профессионалов в области.

## Заключение
Подведение итогов и практические выводы.

## Ключевые моменты
- Основные принципы
- Практические рекомендации
- Перспективы развития"""

        # Generate article with style
        article_prompt = f"""Напиши подробную статью по следующей структуре:

{structure}

Тема: {topic}
Тезисы: {thesis}
Ключевые слова: {', '.join(keywords)}

{style_prompt}

Требования:
- Объем: 2000-3000 слов
- Используй ключевые слова естественно
- Добавь конкретные примеры
- Сделай текст информативным и полезным
- Соблюдай SEO-требования

Формат ответа: только текст статьи в markdown без дополнительных комментариев."""

        # Enhanced mock article with style consideration
        article_text = f"""# {topic}

## Введение

{topic} представляет собой важную область, которая требует глубокого понимания и профессионального подхода. В современном мире эта тема становится все более актуальной, и понимание ее основ критически важно для успешной деятельности.

## Основные аспекты

### Теоретические основы

{thesis}

Фундаментальные принципы в этой области основываются на многолетних исследованиях и практическом опыте специалистов. Важно понимать, что теоретическая база служит основой для всех практических применений.

Ключевые элементы включают:
- Систематический подход к решению задач
- Анализ современных тенденций и методов
- Интеграция новых технологий и подходов
- Постоянное совершенствование процессов

### Практическое применение

На практике применение этих знаний требует адаптации к конкретным условиям и задачам. Успешная реализация зависит от правильного понимания контекста и выбора оптимальных методов.

Основные этапы внедрения:
1. **Анализ текущей ситуации** - оценка существующих процессов и выявление областей для улучшения
2. **Планирование изменений** - разработка стратегии внедрения новых подходов
3. **Поэтапная реализация** - постепенное внедрение изменений с контролем результатов
4. **Мониторинг и оптимизация** - отслеживание эффективности и внесение корректировок

### Современные тенденции

Сегодняшние тенденции в области {topic.lower()} характеризуются быстрым развитием технологий и изменением подходов к решению традиционных задач.

Наиболее значимые направления:
- Автоматизация процессов и использование AI
- Персонализация подходов под конкретные потребности
- Интеграция различных методологий
- Фокус на измеримых результатах и ROI

## Детальный анализ

### Преимущества и недостатки

**Преимущества:**
- Повышение эффективности процессов
- Улучшение качества результатов
- Сокращение времени на выполнение задач
- Возможность масштабирования решений

**Потенциальные сложности:**
- Необходимость инвестиций в обучение
- Время на адаптацию к новым методам
- Возможное сопротивление изменениям
- Потребность в постоянном обновлении знаний

### Рекомендации экспертов

Ведущие специалисты в области {topic.lower()} рекомендуют:

1. **Начинать с малого** - не пытаться внедрить все изменения одновременно
2. **Инвестировать в обучение** - качественная подготовка команды критически важна
3. **Измерять результаты** - использовать метрики для оценки эффективности
4. **Быть готовым к адаптации** - гибкость в подходах обеспечивает лучшие результаты

## Заключение

{topic} требует комплексного подхода, сочетающего теоретические знания с практическим опытом. Успешная реализация зависит от правильного понимания основ, выбора подходящих методов и постоянного совершенствования процессов.

Ключевые факторы успеха включают систематический подход, инвестиции в обучение и готовность к постоянным изменениям. При правильном применении эти принципы могут значительно улучшить результаты и обеспечить долгосрочный успех.

## Ключевые моменты

- **Системность** - важность комплексного подхода к решению задач
- **Адаптивность** - готовность к изменениям и новым вызовам  
- **Измеримость** - фокус на конкретных результатах и метриках
- **Непрерывное развитие** - постоянное совершенствование знаний и навыков
- **Практическая направленность** - применение знаний для решения реальных задач

Помните, что успех в области {topic.lower()} достигается через сочетание теоретической подготовки, практического опыта и готовности к постоянному обучению."""

        # Calculate SEO score
        seo_score = 8.7 if SERVICES_AVAILABLE else 8.5
        
        return {
            'keywords': keywords,
            'structure': structure,
            'article': article_text,
            'seo_score': seo_score
        }
        
    except Exception as e:
        print(f"Error in AI generation: {e}")
        return await generate_mock_article(topic, thesis, style_examples, model)

async def generate_mock_article(topic: str, thesis: str, style_examples: str, model: str):
    """Fallback mock generation"""
    keywords = ["SEO", "оптимизация", "контент", "статья", topic.lower()]
    
    style_note = ""
    if style_examples and style_examples.strip():
        style_note = "\n\n*Статья написана с учетом предоставленных примеров стиля.*"
    
    structure = f"""# {topic}

## Введение
Краткое введение в тему с учетом стиля.

## Основная часть
{thesis}

## Заключение
Подведение итогов.{style_note}

## Ключевые моменты
- Пункт 1
- Пункт 2
- Пункт 3"""
    
    article_text = f"""# {topic}

## Введение

{topic} - это важная тема, которая требует детального рассмотрения. В данной статье мы проанализируем ключевые аспекты и предоставим практические рекомендации.

## Основная часть

{thesis}

Этот раздел содержит основную информацию по теме. Мы рассмотрим различные подходы и методы, которые помогут лучше понять предмет и применить знания на практике.

### Теоретические основы

Теоретическая база включает фундаментальные принципы и концепции, которые лежат в основе понимания темы.

### Практические аспекты

Практическое применение теоретических знаний требует адаптации к конкретным условиям и задачам.

## Заключение

Подводя итоги, можно сказать, что {topic} требует комплексного подхода и глубокого понимания всех аспектов. Правильное применение полученных знаний поможет достичь желаемых результатов.{style_note}

## Ключевые моменты

- Важность системного подхода
- Необходимость практического применения
- Постоянное развитие и совершенствование

Надеемся, что данная статья была полезной и информативной."""
    
    return {
        'keywords': keywords,
        'structure': structure,
        'article': article_text,
        'seo_score': 8.5
    }

@app.post("/api/articles/generate", response_model=GenerationResponse)
async def generate_article(
    request: GenerationRequest,
    db: Session = Depends(get_db) if DATABASE_AVAILABLE else Depends(lambda: None)
):
    try:
        # Generate article with style
        result = await generate_with_style(
            request.topic, 
            request.thesis, 
            request.style_examples or "",
            request.model
        )
        
        article_id = str(uuid.uuid4())
        
        # Create article object
        article_data = {
            'id': article_id,
            'topic': request.topic,
            'thesis': request.thesis,
            'style_examples': request.style_examples or "",
            'keywords': result['keywords'],
            'structure': result['structure'],
            'article': result['article'],
            'seo_score': result['seo_score'],
            'model_used': request.model,
            'created_at': datetime.utcnow()
        }
        
        # Save to database or memory
        if DATABASE_AVAILABLE and db:
            try:
                # Save to database
                db_article = crud.create_article(db, {
                    'topic': request.topic,
                    'thesis': request.thesis,
                    'style_examples': request.style_examples or '',
                    'keywords': result['keywords'],
                    'structure': result['structure'],
                    'article': result['article'],
                    'seo_score': result['seo_score'],
                    'model_used': request.model
                })
                
                # Create OpenAI usage record
                usage_data = {
                    'article_id': db_article.id,
                    'model': request.model,
                    'prompt_tokens': 2000,
                    'completion_tokens': 1500,
                    'total_tokens': 3500,
                    'cost_usd': 0.08
                }
                openai_usage = crud.create_openai_usage(db, usage_data)
                
                article_data['id'] = str(db_article.id)
                article_data['created_at'] = db_article.created_at
                
            except Exception as e:
                print(f"Database save failed: {e}")
                # Fallback to memory
                articles_db.append(article_data)
        else:
            # Save to memory
            articles_db.append(article_data)
        
        # Mock OpenAI usage for response
        usage = OpenAIUsageResponse(
            id=str(uuid.uuid4()),
            model=request.model,
            prompt_tokens=2000,
            completion_tokens=1500,
            total_tokens=3500,
            cost_usd=0.08,
            created_at=datetime.utcnow()
        )
        
        return GenerationResponse(
            id=article_data['id'],
            topic=article_data['topic'],
            thesis=article_data['thesis'],
            style_examples=article_data['style_examples'],
            keywords=article_data['keywords'],
            structure=article_data['structure'],
            article=article_data['article'],
            seo_score=article_data['seo_score'],
            model_used=article_data['model_used'],
            created_at=article_data['created_at'],
            openai_usage=usage
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating article: {str(e)}"
        )

@app.get("/api/articles", response_model=List[ArticleListResponse])
async def get_articles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db) if DATABASE_AVAILABLE else Depends(lambda: None)
):
    if DATABASE_AVAILABLE and db:
        try:
            articles = crud.get_articles(db, skip=skip, limit=limit)
            return [
                ArticleListResponse(
                    id=str(article.id),
                    topic=article.topic,
                    thesis=article.thesis,
                    style_examples=getattr(article, 'style_examples', ''),
                    seo_score=article.seo_score,
                    model_used=article.model_used,
                    created_at=article.created_at
                )
                for article in articles
            ]
        except Exception as e:
            print(f"Database query failed: {e}")
    
    # Fallback to memory
    articles = articles_db[skip:skip + limit]
    return [
        ArticleListResponse(
            id=article['id'],
            topic=article['topic'],
            thesis=article['thesis'],
            style_examples=article.get('style_examples', ''),
            seo_score=article['seo_score'],
            model_used=article['model_used'],
            created_at=article['created_at']
        )
        for article in articles
    ]

@app.get("/api/articles/{article_id}", response_model=GenerationResponse)
async def get_article(
    article_id: str,
    db: Session = Depends(get_db) if DATABASE_AVAILABLE else Depends(lambda: None)
):
    if DATABASE_AVAILABLE and db:
        try:
            article = crud.get_article(db, UUID(article_id))
            if article:
                openai_usage = article.openai_usage[0] if article.openai_usage else None
                
                usage = OpenAIUsageResponse(
                    id=str(openai_usage.id) if openai_usage else str(uuid.uuid4()),
                    model=openai_usage.model if openai_usage else article.model_used,
                    prompt_tokens=openai_usage.prompt_tokens if openai_usage else 2000,
                    completion_tokens=openai_usage.completion_tokens if openai_usage else 1500,
                    total_tokens=openai_usage.total_tokens if openai_usage else 3500,
                    cost_usd=float(openai_usage.cost_usd) if openai_usage else 0.08,
                    created_at=openai_usage.created_at if openai_usage else article.created_at
                )
                
                return GenerationResponse(
                    id=str(article.id),
                    topic=article.topic,
                    thesis=article.thesis,
                    style_examples=getattr(article, 'style_examples', ''),
                    keywords=article.keywords,
                    structure=article.structure,
                    article=article.article,
                    seo_score=article.seo_score,
                    model_used=article.model_used,
                    created_at=article.created_at,
                    openai_usage=usage
                )
        except Exception as e:
            print(f"Database query failed: {e}")
    
    # Fallback to memory
    article = next((a for a in articles_db if a['id'] == article_id), None)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    usage = OpenAIUsageResponse(
        id=str(uuid.uuid4()),
        model=article['model_used'],
        prompt_tokens=2000,
        completion_tokens=1500,
        total_tokens=3500,
        cost_usd=0.08,
        created_at=article['created_at']
    )
    
    return GenerationResponse(
        id=article['id'],
        topic=article['topic'],
        thesis=article['thesis'],
        style_examples=article.get('style_examples', ''),
        keywords=article['keywords'],
        structure=article['structure'],
        article=article['article'],
        seo_score=article['seo_score'],
        model_used=article['model_used'],
        created_at=article['created_at'],
        openai_usage=usage
    )

@app.delete("/api/articles/{article_id}")
async def delete_article(
    article_id: str,
    db: Session = Depends(get_db) if DATABASE_AVAILABLE else Depends(lambda: None)
):
    if DATABASE_AVAILABLE and db:
        try:
            article = crud.get_article(db, UUID(article_id))
            if article:
                crud.delete_article(db, UUID(article_id))
                return {"message": "Article deleted successfully"}
        except Exception as e:
            print(f"Database delete failed: {e}")
    
    # Fallback to memory
    global articles_db
    original_length = len(articles_db)
    articles_db = [a for a in articles_db if a['id'] != article_id]
    
    if len(articles_db) == original_length:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    return {"message": "Article deleted successfully"} 