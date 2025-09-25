"""Add form and effort scores to exercise_log

Revision ID: 003
Revises: 002
Create Date: 2025-09-23

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('exercise_log', sa.Column('form_score', sa.Integer(), nullable=True))
    op.add_column('exercise_log', sa.Column('effort_score', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('exercise_log', 'effort_score')
    op.drop_column('exercise_log', 'form_score')
