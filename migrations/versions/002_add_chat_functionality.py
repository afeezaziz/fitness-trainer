"""Add chat functionality

Revision ID: 002
Revises: 001
Create Date: 2025-09-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create chat_room table
    op.create_table(
        'chat_room',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create chat_message table
    op.create_table(
        'chat_message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_edited', sa.Boolean(), nullable=True),
        sa.Column('edited_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['chat_room.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create chat_participant table
    op.create_table(
        'chat_participant',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['chat_room.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create default chat rooms
    op.execute("""
        INSERT INTO chat_room (name, description, created_at, is_active) VALUES
        ('general', 'General fitness discussion and motivation', NOW(), TRUE),
        ('workout-tips', 'Share workout tips and exercise advice', NOW(), TRUE),
        ('nutrition', 'Discuss nutrition and meal planning', NOW(), TRUE),
        ('progress', 'Share your fitness progress and achievements', NOW(), TRUE)
    """)


def downgrade() -> None:
    op.drop_table('chat_participant')
    op.drop_table('chat_message')
    op.drop_table('chat_room')