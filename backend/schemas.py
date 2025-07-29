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
    id: UUID
    topic: str
    thesis: str
    style_examples: Optional[str] = ""
    character_count: Optional[int] = 5000
    keywords: List[str]
    structure: str
    article: str
    seo_score: float
    model_used: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ArticleListResponse(BaseModel):
    id: UUID
    topic: str
    thesis: str
    style_examples: Optional[str] = ""
    character_count: Optional[int] = 5000
    seo_score: float
    model_used: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class OpenAIUsageResponse(BaseModel):
    id: UUID
    article_id: UUID
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True

class GenerationRequest(BaseModel):
    topic: str
    thesis: str
    style_examples: Optional[str] = ""
    character_count: Optional[int] = 5000
    model: str = "gpt-4o-mini"  # Изменен дефолт на самую быструю модель

class GenerationResponse(BaseModel):
    article_id: UUID
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

class ModelInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    pricing: dict

class ModelsResponse(BaseModel):
    models: List[ModelInfo] 