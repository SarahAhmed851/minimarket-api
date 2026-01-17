"""create products table

Revision ID: 15f0120a75f4
Revises: feed21286
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '15f0120a75f4'  # ← Paste the ID you copied!
down_revision = 'feed21286'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create the products table.
    
    This table stores:
    - id: unique product identifier
    - name: product name
    - description: what the product is
    - price: how much it costs
    - user_id: who created this product (foreign key to users.id)
    - created_at: when product was listed
    - updated_at: last modification time
    """
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        
        # Foreign key: user_id must reference a real user
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create index for faster queries by user
    op.create_index('ix_products_user_id', 'products', ['user_id'])


def downgrade() -> None:
    """
    Remove the products table (if we need to rollback).
    """
    op.drop_index('ix_products_user_id', 'products')
    op.drop_table('products')