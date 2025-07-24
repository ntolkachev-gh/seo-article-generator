"""Add character_count field to articles table

Revision ID: 003
Revises: 002
Create Date: 2025-01-24 21:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    # Add character_count column to articles table
    op.add_column('articles', sa.Column('character_count', sa.Integer(), nullable=True, default=5000))

def downgrade():
    # Remove character_count column from articles table
    op.drop_column('articles', 'character_count') 