"""create devices table

Revision ID: 20261123_001
Revises:
Create Date: 2026-11-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261123_001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("part_number", sa.String(length=100), nullable=False),
        sa.Column("device_type", sa.String(length=20), nullable=False),
        sa.Column("manufacturer", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("package_type", sa.String(length=50), nullable=True),
        sa.Column("datasheet_reference", sa.String(length=255), nullable=True),
        sa.Column("rated_voltage", sa.Float(), nullable=True),
        sa.Column("rated_current", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("part_number"),
    )
    op.create_index("ix_devices_device_type", "devices", ["device_type"])
    op.create_index("ix_devices_part_number", "devices", ["part_number"])


def downgrade() -> None:
    op.drop_index("ix_devices_part_number", table_name="devices")
    op.drop_index("ix_devices_device_type", table_name="devices")
    op.drop_table("devices")
