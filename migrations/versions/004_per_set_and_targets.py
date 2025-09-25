"""Add per-set tracking and user exercise targets

Revision ID: 004
Revises: 003
Create Date: 2025-09-23

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # exercise_set_log table
    op.create_table(
        'exercise_set_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exercise_log_id', sa.Integer(), nullable=False),
        sa.Column('set_number', sa.Integer(), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('form_score', sa.Integer(), nullable=True),
        sa.Column('effort_score', sa.Integer(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['exercise_log_id'], ['exercise_log.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_exercise_set_log_log_id', 'exercise_set_log', ['exercise_log_id'])

    # user_exercise_target table
    op.create_table(
        'user_exercise_target',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('exercise_name', sa.String(length=200), nullable=False),
        sa.Column('min_form_score', sa.Integer(), nullable=True),
        sa.Column('effort_min', sa.Integer(), nullable=True),
        sa.Column('effort_max', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_exercise_target_user_id', 'user_exercise_target', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_user_exercise_target_user_id', table_name='user_exercise_target')
    op.drop_table('user_exercise_target')
    op.drop_index('ix_exercise_set_log_log_id', table_name='exercise_set_log')
    op.drop_table('exercise_set_log')
