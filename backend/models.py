from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, DECIMAL, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from database import Base

class ArticleStatus(enum.Enum):
    PENDING = "pending"          # Ожидает генерации
    GENERATING = "generating"    # В процессе генерации
    COMPLETED = "completed"      # Генерация завершена
    FAILED = "failed"           # Ошибка генерации

class Article(Base):
    __tablename__ = "articles"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(Text, nullable=False)
    thesis = Column(Text, nullable=False)
    style_examples = Column(Text, nullable=True)  # Новое поле для примеров стиля
    character_count = Column(Integer, nullable=True, default=5000)  # Новое поле для количества знаков
    keywords = Column(JSONB, nullable=True)  # Делаем nullable для асинхронной генерации
    structure = Column(Text, nullable=True)  # Делаем nullable для асинхронной генерации
    article = Column(Text, nullable=True)  # Делаем nullable для асинхронной генерации
    seo_score = Column(Float, nullable=True)  # Делаем nullable для асинхронной генерации
    model_used = Column(String(50), nullable=False, default="unknown")
    status = Column(Enum(ArticleStatus), nullable=False, default=ArticleStatus.PENDING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    openai_usage = relationship("OpenAIUsage", back_populates="article")

class OpenAIUsage(Base):
    __tablename__ = "openai_usage"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    model = Column(String(50), nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    cost_usd = Column(DECIMAL(10, 6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    article = relationship("Article", back_populates="openai_usage") 