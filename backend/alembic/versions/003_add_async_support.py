"""Add async article generation support

Revision ID: 003
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Создаем enum тип для статуса
    article_status_enum = postgresql.ENUM('pending', 'generating', 'completed', 'failed', name='articlestatus')
    article_status_enum.create(op.get_bind())
    
    # Добавляем новые колонки
    op.add_column('articles', sa.Column('status', article_status_enum, nullable=False, server_default='pending'))
    op.add_column('articles', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    
    # Добавляем character_count колонку
    op.add_column('articles', sa.Column('character_count', sa.Integer(), nullable=True, server_default='5000'))
    
    # Добавляем style_examples колонку (из миграции 002)
    op.add_column('articles', sa.Column('style_examples', sa.Text(), nullable=True))
    
    # Делаем существующие колонки nullable для поддержки асинхронной генерации
    op.alter_column('articles', 'keywords', nullable=True)
    op.alter_column('articles', 'structure', nullable=True)
    op.alter_column('articles', 'article', nullable=True)
    op.alter_column('articles', 'seo_score', nullable=True)
    
    # Обновляем существующие записи - устанавливаем статус 'completed' для уже сгенерированных статей
    op.execute("UPDATE articles SET status = 'completed' WHERE article IS NOT NULL AND article != ''")

def downgrade():
    # Возвращаем обратно nullable=False для основных полей
    op.alter_column('articles', 'seo_score', nullable=False)
    op.alter_column('articles', 'article', nullable=False)
    op.alter_column('articles', 'structure', nullable=False)
    op.alter_column('articles', 'keywords', nullable=False)
    
    # Удаляем style_examples колонку
    op.drop_column('articles', 'style_examples')
    
    # Удаляем character_count колонку
    op.drop_column('articles', 'character_count')
    
    # Удаляем новые колонки
    op.drop_column('articles', 'updated_at')
    op.drop_column('articles', 'error_message')
    op.drop_column('articles', 'status')
    
    # Удаляем enum тип
    article_status_enum = postgresql.ENUM('pending', 'generating', 'completed', 'failed', name='articlestatus')
    article_status_enum.drop(op.get_bind()) 