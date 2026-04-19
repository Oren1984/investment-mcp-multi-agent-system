"""Initial schema — tickers, analysis_runs, agent_outputs, reports

Revision ID: 0001
Revises:
Create Date: 2026-04-19

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable required PostgreSQL extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "tickers",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("symbol", sa.String(10), nullable=False, unique=True, index=True),
        sa.Column("company_name", sa.Text, nullable=True),
        sa.Column("sector", sa.String(100), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("exchange", sa.String(20), nullable=True),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    run_status_enum = postgresql.ENUM(
        "PENDING", "RUNNING", "COMPLETED", "FAILED",
        name="run_status",
        create_type=True,
    )
    op.create_table(
        "analysis_runs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("ticker", sa.String(10), nullable=False, index=True),
        sa.Column(
            "ticker_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("tickers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", run_status_enum, nullable=False, server_default="PENDING"),
        sa.Column("config", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
    )

    op.create_table(
        "agent_outputs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("agent_name", sa.String(50), nullable=False),
        sa.Column("output_data", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("tool_calls", postgresql.JSONB, nullable=True, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("ticker_symbol", sa.String(10), nullable=False, index=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("structured", postgresql.JSONB, nullable=True, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("agent_outputs")
    op.drop_table("analysis_runs")
    op.execute("DROP TYPE IF EXISTS run_status")
    op.drop_table("tickers")
