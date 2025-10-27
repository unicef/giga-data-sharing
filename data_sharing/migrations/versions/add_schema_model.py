"""Add schema model and associations

Revision ID: add_schema_model
Revises: c2ed12933e52
Create Date: 2024-12-19 12:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_schema_model"
down_revision: Union[str, None] = "c2ed12933e52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create schemas table
    op.create_table(
        "schemas",
        sa.Column("id", sa.VARCHAR(length=50), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_schemas_id"), "schemas", ["id"], unique=False)
    
    # Create apikey_schema_association_table
    op.create_table(
        "apikey_schema_association_table",
        sa.Column("api_key_id", sa.Uuid(), nullable=False),
        sa.Column("schema_id", sa.VARCHAR(length=50), nullable=False),
        sa.ForeignKeyConstraint(["api_key_id"], ["api_keys.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["schema_id"], ["schemas.id"], ondelete="CASCADE"),
    )
    
    # Create schema_role_association_table
    op.create_table(
        "schema_role_association_table",
        sa.Column("schema_id", sa.VARCHAR(length=50), nullable=False),
        sa.Column("role_id", sa.VARCHAR(length=5), nullable=False),
        sa.ForeignKeyConstraint(["schema_id"], ["schemas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("schema_role_association_table")
    op.drop_table("apikey_schema_association_table")
    op.drop_index(op.f("ix_schemas_id"), table_name="schemas")
    op.drop_table("schemas")

