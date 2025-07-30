"""Add missing columns for async support

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    # Проверяем и добавляем только недостающие колонки
    connection = op.get_bind()
    
    # Проверяем существование колонки status
    result = connection.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'articles' AND column_name = 'status'
    """)).fetchone()
    
    if not result:
        # Создаем enum тип для статуса
        article_status_enum = postgresql.ENUM('pending', 'generating', 'completed', 'failed', name='articlestatus')
        article_status_enum.create(connection)
        op.add_column('articles', sa.Column('status', article_status_enum, nullable=False, server_default='pending'))
    
    # Проверяем существование колонки error_message
    result = connection.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'articles' AND column_name = 'error_message'
    """)).fetchone()
    
    if not result:
        op.add_column('articles', sa.Column('error_message', sa.Text(), nullable=True))
    
    # Проверяем существование колонки updated_at
    result = connection.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'articles' AND column_name = 'updated_at'
    """)).fetchone()
    
    if not result:
        op.add_column('articles', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    
    # Проверяем существование колонки style_examples
    result = connection.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'articles' AND column_name = 'style_examples'
    """)).fetchone()
    
    if not result:
        op.add_column('articles', sa.Column('style_examples', sa.Text(), nullable=True))
    
    # Делаем существующие колонки nullable для поддержки асинхронной генерации
    # Проверяем, не nullable ли уже колонки
    for column in ['keywords', 'structure', 'article', 'seo_score']:
        result = connection.execute(text(f"""
            SELECT is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'articles' AND column_name = '{column}'
        """)).fetchone()
        
        if result and result[0] == 'NO':
            op.alter_column('articles', column, nullable=True)
    
    # Обновляем существующие записи - устанавливаем статус 'completed' для уже сгенерированных статей
    connection.execute("UPDATE articles SET status = 'completed' WHERE article IS NOT NULL AND article != '' AND status = 'pending'")

def downgrade():
    # Возвращаем обратно nullable=False для основных полей
    op.alter_column('articles', 'seo_score', nullable=False)
    op.alter_column('articles', 'article', nullable=False)
    op.alter_column('articles', 'structure', nullable=False)
    op.alter_column('articles', 'keywords', nullable=False)
    
    # Удаляем новые колонки
    op.drop_column('articles', 'style_examples')
    op.drop_column('articles', 'updated_at')
    op.drop_column('articles', 'error_message')
    op.drop_column('articles', 'status')
    
    # Удаляем enum тип
    connection = op.get_bind()
    article_status_enum = postgresql.ENUM('pending', 'generating', 'completed', 'failed', name='articlestatus')
    article_status_enum.drop(connection) 