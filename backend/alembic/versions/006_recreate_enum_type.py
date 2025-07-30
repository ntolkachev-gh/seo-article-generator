"""Recreate enum type to fix SQLAlchemy mapping

Revision ID: 006
Revises: 005
Create Date: 2025-07-30 04:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаляем enum из колонки
    op.execute("ALTER TABLE articles ALTER COLUMN status TYPE VARCHAR(20)")
    
    # Удаляем старый enum тип
    op.execute("DROP TYPE IF EXISTS articlestatus")
    
    # Создаем новый enum тип с нижним регистром
    article_status_enum = postgresql.ENUM('pending', 'generating', 'completed', 'failed', name='articlestatus')
    article_status_enum.create(op.get_bind())
    
    # Возвращаем enum в колонку
    op.execute("ALTER TABLE articles ALTER COLUMN status TYPE articlestatus USING status::articlestatus")


def downgrade() -> None:
    # Удаляем enum из колонки
    op.execute("ALTER TABLE articles ALTER COLUMN status TYPE VARCHAR(20)")
    
    # Удаляем enum тип
    op.execute("DROP TYPE IF EXISTS articlestatus")
    
    # Создаем старый enum тип с верхним регистром
    article_status_enum = postgresql.ENUM('PENDING', 'GENERATING', 'COMPLETED', 'FAILED', name='articlestatus')
    article_status_enum.create(op.get_bind())
    
    # Возвращаем enum в колонку
    op.execute("ALTER TABLE articles ALTER COLUMN status TYPE articlestatus USING status::articlestatus")