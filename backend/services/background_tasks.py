import asyncio
import logging
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Article, ArticleStatus
import crud
from services.serp_service import SERPService
from services.ai_service import AIService
from services.seo_service import SEOService

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Менеджер для управления фоновыми задачами генерации статей"""
    
    def __init__(self):
        self.serp_service = SERPService()
        self.ai_service = AIService()
        self.seo_service = SEOService()
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    async def start_article_generation(self, article_id: UUID, generation_params: Dict[str, Any]):
        """Запускает фоновую задачу генерации статьи"""
        task_id = str(article_id)
        
        # Проверяем, не запущена ли уже задача для этой статьи
        if task_id in self.running_tasks and not self.running_tasks[task_id].done():
            logger.warning(f"Задача генерации для статьи {article_id} уже запущена")
            return
        
        # Создаем и запускаем задачу
        task = asyncio.create_task(self._generate_article_async(article_id, generation_params))
        self.running_tasks[task_id] = task
        
        logger.info(f"Запущена фоновая задача генерации для статьи {article_id}")
        return task
    
    async def _generate_article_async(self, article_id: UUID, params: Dict[str, Any]):
        """Асинхронная генерация статьи"""
        db = next(get_db())
        
        try:
            # Обновляем статус на "generating"
            await self._update_article_status(db, article_id, ArticleStatus.GENERATING)
            
            logger.info(f"🚀 Начинаем асинхронную генерацию статьи {article_id}")
            
            # 1. Анализ SERP
            logger.info("🔎 Этап 1: Анализ SERP...")
            serp_data = self.serp_service.analyze_topic(params['topic'])
            keywords = serp_data["keywords"]
            questions = serp_data["questions"]
            logger.info(f"✅ SERP анализ завершен. Ключевых слов: {len(keywords)}, вопросов: {len(questions)}")
            
            # 2. Генерация структуры статьи
            logger.info("📋 Этап 2: Генерация структуры статьи...")
            structure, structure_usage = self.ai_service.generate_structure(
                params['topic'], 
                params['thesis'], 
                keywords, 
                questions, 
                params['model']
            )
            logger.info(f"✅ Структура сгенерирована. Токенов использовано: {structure_usage.get('total_tokens', 0)}")
            
            # 3. Генерация полной статьи
            logger.info("📝 Этап 3: Генерация полной статьи...")
            article_text, article_usage = self.ai_service.generate_article(
                params['topic'],
                params['thesis'],
                structure,
                keywords,
                params.get('style_examples', ''),
                params.get('character_count', 5000),
                params['model']
            )
            logger.info(f"✅ Статья сгенерирована. Длина: {len(article_text)} символов")
            
            # 4. Расчет SEO-оценки
            logger.info("📈 Этап 4: Расчет SEO-оценки...")
            seo_score = self.seo_service.calculate_seo_score(article_text, keywords)
            logger.info(f"✅ SEO-оценка рассчитана: {seo_score}")
            
            # 5. Обновление статьи в базе данных
            logger.info("💾 Этап 5: Сохранение результатов...")
            article_data = {
                'keywords': keywords,
                'structure': structure,
                'article': article_text,
                'seo_score': seo_score,
                'status': ArticleStatus.COMPLETED,
                'error_message': None,
                'updated_at': datetime.utcnow()
            }
            
            await self._update_article_data(db, article_id, article_data)
            
            # 6. Сохранение информации об использовании
            logger.info("💰 Этап 6: Сохранение статистики использования...")
            total_usage = {
                "prompt_tokens": structure_usage["prompt_tokens"] + article_usage["prompt_tokens"],
                "completion_tokens": structure_usage["completion_tokens"] + article_usage["completion_tokens"],
                "total_tokens": structure_usage["total_tokens"] + article_usage["total_tokens"]
            }
            
            cost = self.ai_service.calculate_cost(total_usage, params['model'])
            
            usage_data = {
                "article_id": article_id,
                "model": params['model'],
                "prompt_tokens": total_usage["prompt_tokens"],
                "completion_tokens": total_usage["completion_tokens"],
                "total_tokens": total_usage["total_tokens"],
                "cost_usd": cost
            }
            
            crud.create_openai_usage(db, usage_data)
            
            logger.info(f"🎉 Статья {article_id} успешно сгенерирована асинхронно!")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при генерации статьи {article_id}: {str(e)}")
            
            # Обновляем статус на "failed" и сохраняем ошибку
            error_data = {
                'status': ArticleStatus.FAILED,
                'error_message': str(e),
                'updated_at': datetime.utcnow()
            }
            await self._update_article_data(db, article_id, error_data)
            
        finally:
            # Удаляем задачу из списка активных
            task_id = str(article_id)
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            db.close()
    
    async def _update_article_status(self, db: Session, article_id: UUID, status: ArticleStatus):
        """Обновляет статус статьи"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if article:
            article.status = status
            article.updated_at = datetime.utcnow()
            db.commit()
    
    async def _update_article_data(self, db: Session, article_id: UUID, data: Dict[str, Any]):
        """Обновляет данные статьи"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if article:
            for key, value in data.items():
                setattr(article, key, value)
            db.commit()
    
    def get_task_status(self, article_id: UUID) -> str:
        """Получает статус задачи генерации"""
        task_id = str(article_id)
        if task_id not in self.running_tasks:
            return "not_found"
        
        task = self.running_tasks[task_id]
        if task.done():
            if task.exception():
                return "failed"
            return "completed"
        return "running"
    
    def cancel_task(self, article_id: UUID) -> bool:
        """Отменяет задачу генерации"""
        task_id = str(article_id)
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            if not task.done():
                task.cancel()
                return True
        return False

# Глобальный экземпляр менеджера задач
background_task_manager = BackgroundTaskManager() 