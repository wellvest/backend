"""Add total_invested_amount to Profile model

Revision ID: 56a223a64930
Revises: add_payments_table
Create Date: 2025-07-20 20:42:32.750743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56a223a64930'
down_revision = 'add_payments_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add total_invested_amount column to profiles table
    op.add_column('profiles', sa.Column('total_invested_amount', sa.Float(), nullable=True, server_default='0.0'))
    
    # Update existing profiles to have total_invested_amount = 0.0
    op.execute("UPDATE profiles SET total_invested_amount = 0.0 WHERE total_invested_amount IS NULL")
    
    # Make the column non-nullable after setting default values
    op.alter_column('profiles', 'total_invested_amount', nullable=False)


def downgrade() -> None:
    # Remove total_invested_amount column from profiles table
    op.drop_column('profiles', 'total_invested_amount')
