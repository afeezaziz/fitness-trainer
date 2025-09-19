"""Initial schema migration

Revision ID: 001
Revises:
Create Date: 2025-09-19

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('google_id', sa.String(100), nullable=False),
        sa.Column('email', sa.String(120), nullable=False),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('profile_picture', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id')
    )

    # Create food_log table
    op.create_table(
        'food_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('meal_type', sa.String(50), nullable=False),
        sa.Column('food_name', sa.String(200), nullable=False),
        sa.Column('portion_size', sa.String(100), nullable=False),
        sa.Column('meal_time', sa.DateTime(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create calorie_entry table
    op.create_table(
        'calorie_entry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('food_item', sa.String(200), nullable=False),
        sa.Column('calories', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.String(100), nullable=False),
        sa.Column('entry_time', sa.DateTime(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create exercise_log table
    op.create_table(
        'exercise_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('exercise_name', sa.String(200), nullable=False),
        sa.Column('exercise_type', sa.String(50), nullable=False),
        sa.Column('sets', sa.Integer(), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('workout_time', sa.DateTime(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('exercise_log')
    op.drop_table('calorie_entry')
    op.drop_table('food_log')
    op.drop_table('user')