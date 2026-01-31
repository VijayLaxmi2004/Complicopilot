"""init tables

Revision ID: 20250823_0001
Revises: 
Create Date: 2025-08-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250823_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'receipts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('vendor', sa.String(), nullable=False),
        sa.Column('date', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), server_default='INR'),
        sa.Column('category', sa.String(), server_default='uncategorized', nullable=False),
        sa.Column('gstin', sa.String(), server_default=''),
        sa.Column('tax_amount', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), server_default='needs_review', nullable=False),
        sa.Column('filename', sa.String(), nullable=True),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('extracted', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        'compliance_issues',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('receipt_id', sa.String(), sa.ForeignKey('receipts.id'), nullable=False),
        sa.Column('level', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('resolved', sa.Boolean(), server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    op.drop_table('compliance_issues')
    op.drop_table('receipts')
