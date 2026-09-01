"""add ticket status

Revision ID: b69669803e95
Revises: 88508026e676
Create Date: 2026-09-01 17:40:41.465969

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b69669803e95"
down_revision: Union[str, Sequence[str], None] = "88508026e676"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "tickets",
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "cancelled",
                name="ticketstatus",
                native_enum=False,
                length=20,
            ),
            nullable=False,
            server_default="active",
        ),
    )
    op.create_index(op.f("ix_tickets_status"), "tickets", ["status"], unique=False)
    op.alter_column("tickets", "status", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_tickets_status"), table_name="tickets")
    op.drop_column("tickets", "status")
