"""add_user_record_fields

Revision ID: 5e3c8f2a1b9d
Revises: 512cd24e1346
Create Date: 2026-06-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e3c8f2a1b9d'
down_revision: Union[str, Sequence[str], None] = '512cd24e1346'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema — add tags, private, ep_status columns to user_records."""
    op.add_column('user_records', sa.Column('tags', sa.JSON(), nullable=True))
    op.add_column('user_records', sa.Column('private', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    op.add_column('user_records', sa.Column('ep_status', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema — remove new columns from user_records."""
    op.drop_column('user_records', 'ep_status')
    op.drop_column('user_records', 'private')
    op.drop_column('user_records', 'tags')
