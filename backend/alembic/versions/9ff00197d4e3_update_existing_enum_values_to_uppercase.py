"""Update existing enum values to uppercase

Revision ID: 9ff00197d4e3
Revises: 004
Create Date: 2025-07-30 03:56:09.631717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '9ff00197d4e3'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Обновляем существующие записи с маленькими буквами на большие
    connection = op.get_bind()
    
    # Обновляем все возможные значения статуса
    connection.execute(text("UPDATE articles SET status = 'PENDING' WHERE status = 'pending'"))
    connection.execute(text("UPDATE articles SET status = 'GENERATING' WHERE status = 'generating'"))
    connection.execute(text("UPDATE articles SET status = 'COMPLETED' WHERE status = 'completed'"))
    connection.execute(text("UPDATE articles SET status = 'FAILED' WHERE status = 'failed'"))


def downgrade() -> None:
    # Возвращаем обратно к маленьким буквам
    connection = op.get_bind()
    
    connection.execute(text("UPDATE articles SET status = 'pending' WHERE status = 'PENDING'"))
    connection.execute(text("UPDATE articles SET status = 'generating' WHERE status = 'GENERATING'"))
    connection.execute(text("UPDATE articles SET status = 'completed' WHERE status = 'COMPLETED'"))
    connection.execute(text("UPDATE articles SET status = 'failed' WHERE status = 'FAILED'"))
