"""add_referral_columns_to_users

Revision ID: 87dbd732dfeb
Revises: 7f00d3e4aa19
Create Date: 2025-07-11 00:09:52.851050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87dbd732dfeb'
down_revision = '7f00d3e4aa19'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add referral_code column (unique string)
    op.add_column('users', sa.Column('referral_code', sa.String(length=20), nullable=True, unique=True))
    
    # Add referrer_id column (foreign key to users table)
    op.add_column('users', sa.Column('referrer_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_users_referrer_id', 
        'users', 'users', 
        ['referrer_id'], ['id']
    )


def downgrade() -> None:
    # Drop foreign key constraint first
    op.drop_constraint('fk_users_referrer_id', 'users', type_='foreignkey')
    
    # Drop columns
    op.drop_column('users', 'referrer_id')
    op.drop_column('users', 'referral_code')
