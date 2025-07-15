"""add_payments_table

Revision ID: add_payments_table
Revises: add_plans_and_relationships
Create Date: 2025-07-14 08:27:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func
import uuid

# revision identifiers, used by Alembic.
revision = 'add_payments_table'
down_revision = 'add_plans_and_relationships'
branch_labels = None
depends_on = None


def generate_uuid():
    return str(uuid.uuid4())


def upgrade() -> None:
    # Create payments table
    op.create_table('payments',
        sa.Column('id', sa.String(), nullable=False, default=generate_uuid),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('plan_id', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('upi_ref_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), default='pending'),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=func.now()),
        sa.Column('updated_at', sa.DateTime(), default=func.now(), onupdate=func.now()),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop payments table
    op.drop_table('payments')
