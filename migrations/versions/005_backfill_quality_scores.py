"""Backfill quality scores for existing per-set rows

Revision ID: 005
Revises: 004
Create Date: 2025-09-23

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Compute composite quality where missing and inputs are present
    op.execute(
        """
        UPDATE exercise_set_log
        SET quality_score = form_score * (effort_score / 10.0)
        WHERE quality_score IS NULL
          AND form_score IS NOT NULL
          AND effort_score IS NOT NULL
        """
    )


def downgrade() -> None:
    # Revert only values that were computed by this migration (best-effort):
    # We clear quality_score where it's exactly equal to form_score * (effort_score/10)
    op.execute(
        """
        UPDATE exercise_set_log AS s
        JOIN (
          SELECT id, form_score * (effort_score / 10.0) AS computed
          FROM exercise_set_log
        ) c ON c.id = s.id
        SET s.quality_score = NULL
        WHERE s.quality_score = c.computed
        """
    )
