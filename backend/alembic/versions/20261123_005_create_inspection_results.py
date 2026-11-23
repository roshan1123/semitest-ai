"""create inspection results

Revision ID: 20261123_005
Revises: 20261123_004
Create Date: 2026-11-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261123_005"
down_revision: Union[str, Sequence[str], None] = "20261123_004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inspection_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("device_id", sa.String(length=36), nullable=True),
        sa.Column("image_filename", sa.String(length=255), nullable=False),
        sa.Column("image_path", sa.String(length=500), nullable=False),
        sa.Column("inspection_type", sa.String(length=50), nullable=False),
        sa.Column("result", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("analysis_metadata", sa.Text(), nullable=False),
        sa.Column("human_review_status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("inspection_results")
