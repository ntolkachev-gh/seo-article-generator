"""Change enum values to lowercase

Revision ID: 005
Revises: c2c8128ea0bd
Create Date: 2025-07-30 04:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = 'c2c8128ea0bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Обновляем существующие записи с больших букв на маленькие
    connection = op.get_bind()
    
    # Используем CAST для безопасного обновления enum значений
    connection.execute(text("UPDATE articles SET status = 'pending'::articlestatus WHERE status::text = 'PENDING'"))
    connection.execute(text("UPDATE articles SET status = 'generating'::articlestatus WHERE status::text = 'GENERATING'"))
    connection.execute(text("UPDATE articles SET status = 'completed'::articlestatus WHERE status::text = 'COMPLETED'"))
    connection.execute(text("UPDATE articles SET status = 'failed'::articlestatus WHERE status::text = 'FAILED'"))


def downgrade() -> None:
    # Возвращаем обратно к большим буквам
    connection = op.get_bind()
    
    connection.execute(text("UPDATE articles SET status = 'PENDING'::articlestatus WHERE status::text = 'pending'"))
    connection.execute(text("UPDATE articles SET status = 'GENERATING'::articlestatus WHERE status::text = 'generating'"))
    connection.execute(text("UPDATE articles SET status = 'COMPLETED'::articlestatus WHERE status::text = 'completed'"))
    connection.execute(text("UPDATE articles SET status = 'FAILED'::articlestatus WHERE status::text = 'failed'"))