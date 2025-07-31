"""Convert local schema to match production schema

Revision ID: convert_to_production_schema
Revises: 
Create Date: 2025-08-01 00:43:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'convert_to_production_schema'
down_revision = '56a223a64930'
branch_labels = None
depends_on = None


def upgrade():
    # First, add the new columns that production expects
    op.add_column('plans', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('plans', sa.Column('amount', sa.Float(), nullable=True))
    op.add_column('plans', sa.Column('interest_rate', sa.Float(), nullable=True))
    op.add_column('plans', sa.Column('is_active', sa.Boolean(), nullable=True, default=True))
    
    # Migrate data from old columns to new columns
    # Use min_amount as the amount
    op.execute("UPDATE plans SET amount = min_amount WHERE amount IS NULL")
    op.execute("UPDATE plans SET interest_rate = returns_percentage WHERE interest_rate IS NULL")
    op.execute("UPDATE plans SET is_active = true WHERE is_active IS NULL")
    op.execute("UPDATE plans SET description = 'Migrated from local schema' WHERE description IS NULL")
    
    # Make the new columns non-nullable after data migration
    op.alter_column('plans', 'amount', nullable=False)
    op.alter_column('plans', 'interest_rate', nullable=False)
    op.alter_column('plans', 'duration_months', nullable=False)
    
    # Drop the old columns
    op.drop_column('plans', 'returns_percentage')
    op.drop_column('plans', 'max_amount')
    op.drop_column('plans', 'min_amount')


def downgrade():
    # Add back the old columns
    op.add_column('plans', sa.Column('min_amount', sa.Float(), nullable=True))
    op.add_column('plans', sa.Column('max_amount', sa.Float(), nullable=True))
    op.add_column('plans', sa.Column('returns_percentage', sa.Float(), nullable=True))
    
    # Migrate data back
    op.execute("UPDATE plans SET min_amount = amount WHERE min_amount IS NULL")
    op.execute("UPDATE plans SET max_amount = amount WHERE max_amount IS NULL")
    op.execute("UPDATE plans SET returns_percentage = interest_rate WHERE returns_percentage IS NULL")
    
    # Make old columns non-nullable
    op.alter_column('plans', 'min_amount', nullable=False)
    op.alter_column('plans', 'max_amount', nullable=False)
    op.alter_column('plans', 'duration_months', nullable=True)
    
    # Drop the new columns
    op.drop_column('plans', 'is_active')
    op.drop_column('plans', 'interest_rate')
    op.drop_column('plans', 'amount')
    op.drop_column('plans', 'description')
