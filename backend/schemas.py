from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from config import settings

class ArticleCreate(BaseModel):
    topic: str
    thesis: str
    model_used: str

class ArticleResponse(BaseModel):
    id: str
    topic: str
    thesis: str
    style_examples: Optional[str] = ""
    character_count: Optional[int] = 5000
    keywords: List[str]
    structure: str
    article: str
    seo_score: float
    model_used: str = "unknown"
    created_at: str
    
    class Config:
        from_attributes = True
        protected_namespaces = ()
        
    @classmethod
    def from_orm(cls, obj):
        # Преобразуем UUID и datetime в строки
        data = {
            'id': str(obj.id),
            'topic': obj.topic,
            'thesis': obj.thesis,
            'style_examples': obj.style_examples,
            'character_count': obj.character_count,
            'keywords': obj.keywords,
            'structure': obj.structure,
            'article': obj.article,
            'seo_score': obj.seo_score,
            'model_used': obj.model_used or 'unknown',
            'created_at': obj.created_at.isoformat() if obj.created_at else None
        }
        return cls(**data)

class ArticleListResponse(BaseModel):
    id: str
    topic: str
    thesis: str
    style_examples: Optional[str] = ""
    character_count: Optional[int] = 5000
    seo_score: float
    model_used: str = "unknown"
    created_at: str
    
    class Config:
        from_attributes = True
        protected_namespaces = ()
        
    @classmethod
    def from_orm(cls, obj):
        # Преобразуем UUID и datetime в строки
        data = {
            'id': str(obj.id),
            'topic': obj.topic,
            'thesis': obj.thesis,
            'style_examples': obj.style_examples,
            'character_count': obj.character_count,
            'seo_score': obj.seo_score,
            'model_used': obj.model_used or 'unknown',
            'created_at': obj.created_at.isoformat() if obj.created_at else None
        }
        return cls(**data)

class OpenAIUsageResponse(BaseModel):
    id: str
    article_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: str
    created_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        # Преобразуем UUID, Decimal и datetime в строки
        data = {
            'id': str(obj.id),
            'article_id': str(obj.article_id),
            'model': obj.model,
            'prompt_tokens': obj.prompt_tokens,
            'completion_tokens': obj.completion_tokens,
            'total_tokens': obj.total_tokens,
            'cost_usd': str(obj.cost_usd),
            'created_at': obj.created_at.isoformat() if obj.created_at else None
        }
        return cls(**data)

class GenerationRequest(BaseModel):
    topic: str
    thesis: str
    style_examples: Optional[str] = ""
    character_count: Optional[int] = 5000
    model: str = "gpt-4o-mini"  # Изменен дефолт на самую быструю модель

class GenerationResponse(BaseModel):
    article_id: str
    topic: str
    thesis: str
    style_examples: Optional[str] = ""
    character_count: Optional[int] = 5000
    keywords: List[str]
    structure: str
    article: str
    seo_score: float
    model_used: str
    usage: OpenAIUsageResponse
    
    class Config:
        protected_namespaces = ()

class ModelInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    pricing: dict

class ModelsResponse(BaseModel):
    models: List[ModelInfo] 