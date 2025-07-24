"""Add style_examples field to articles table

Revision ID: 002
Revises: 001
Create Date: 2025-01-24 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Add style_examples column to articles table
    op.add_column('articles', sa.Column('style_examples', sa.Text(), nullable=True))

def downgrade():
    # Remove style_examples column from articles table
    op.drop_column('articles', 'style_examples') 