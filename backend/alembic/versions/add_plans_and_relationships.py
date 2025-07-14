"""Add plans table and relationships

Revision ID: add_plans_and_relationships
Revises: 
Create Date: 2025-07-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func
import uuid


# revision identifiers, used by Alembic.
revision = 'add_plans_and_relationships'
down_revision = 'e24f446c9953'  # Link to the existing migration chain
branch_labels = None
depends_on = None


def generate_uuid():
    return str(uuid.uuid4())


def upgrade():
    # Create plans table first
    op.create_table('plans',
        sa.Column('id', sa.String(), nullable=False, default=generate_uuid),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('duration_months', sa.Integer(), nullable=False),
        sa.Column('interest_rate', sa.Float(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=func.now()),
        sa.Column('updated_at', sa.DateTime(), default=func.now(), onupdate=func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add current_plan_id to profiles table
    op.add_column('profiles', sa.Column('current_plan_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_profiles_current_plan_id', 'profiles', 'plans',
        ['current_plan_id'], ['id'], ondelete='SET NULL'
    )
    
    # Add plan_id to investments table
    op.add_column('investments', sa.Column('plan_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_investments_plan_id', 'investments', 'plans',
        ['plan_id'], ['id'], ondelete='SET NULL'
    )


def downgrade():
    # Remove foreign key constraints first
    op.drop_constraint('fk_investments_plan_id', 'investments', type_='foreignkey')
    op.drop_constraint('fk_profiles_current_plan_id', 'profiles', type_='foreignkey')
    
    # Remove columns
    op.drop_column('investments', 'plan_id')
    op.drop_column('profiles', 'current_plan_id')
    
    # Drop plans table
    op.drop_table('plans')
