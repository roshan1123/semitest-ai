"""create test executions and measurement results

Revision ID: 20261123_004
Revises: 20261123_002
Create Date: 2026-11-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261123_004"
down_revision: Union[str, Sequence[str], None] = "20261123_002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "test_executions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("device_part_number", sa.String(length=100), nullable=False),
        sa.Column("device_category", sa.String(length=20), nullable=False),
        sa.Column("profile_id", sa.String(length=36), nullable=False),
        sa.Column("profile_version", sa.Integer(), nullable=False),
        sa.Column("scenario", sa.String(length=20), nullable=False),
        sa.Column("simulation_mode", sa.String(length=30), nullable=False),
        sa.Column("simulator_version", sa.String(length=50), nullable=False),
        sa.Column("random_seed", sa.Integer(), nullable=True),
        sa.Column("operator", sa.String(length=100), nullable=False),
        sa.Column("overall_status", sa.String(length=20), nullable=False),
        sa.Column("execution_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("execution_completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("test_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.ForeignKeyConstraint(["profile_id"], ["test_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_test_executions_device_id", "test_executions", ["device_id"])
    op.create_index("ix_test_executions_profile_id", "test_executions", ["profile_id"])

    op.create_table(
        "measurement_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("test_execution_id", sa.String(length=36), nullable=False),
        sa.Column("parameter_name", sa.String(length=100), nullable=False),
        sa.Column("measured_value", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(length=30), nullable=False),
        sa.Column("lower_limit", sa.Float(), nullable=True),
        sa.Column("upper_limit", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("measurement_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("simulation_flag", sa.Boolean(), nullable=False),
        sa.Column("test_conditions", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["test_execution_id"],
            ["test_executions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_measurement_results_test_execution_id",
        "measurement_results",
        ["test_execution_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_measurement_results_test_execution_id",
        table_name="measurement_results",
    )
    op.drop_table("measurement_results")
    op.drop_index("ix_test_executions_profile_id", table_name="test_executions")
    op.drop_index("ix_test_executions_device_id", table_name="test_executions")
    op.drop_table("test_executions")
