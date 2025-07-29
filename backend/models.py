from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database import Base

class Article(Base):
    __tablename__ = "articles"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(Text, nullable=False)
    thesis = Column(Text, nullable=False)
    style_examples = Column(Text, nullable=True)  # Новое поле для примеров стиля
    character_count = Column(Integer, nullable=True, default=5000)  # Новое поле для количества знаков
    keywords = Column(JSONB, nullable=False)
    structure = Column(Text, nullable=False)
    article = Column(Text, nullable=False)
    seo_score = Column(Float, nullable=False)
    model_used = Column(String(50), nullable=False, default="unknown")
    created_at = Column(DateTime, default=datetime.utcnow)
    
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