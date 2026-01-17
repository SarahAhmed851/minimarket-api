"""create users table

Revision ID: feed21286
Revises: 
Create Date: (keep the date that's there)

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'feed21286'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create the users table.
    
    This table stores:
    - id: unique user identifier
    - username: user's chosen name (must be unique)
    - email: user's email (must be unique)
    - hashed_password: encrypted password
    - created_at: when the user registered
    """
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    # Create indexes for faster lookups
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])


def downgrade() -> None:
    """
    Remove the users table (if we need to rollback).
    """
    op.drop_index('ix_users_email', 'users')
    op.drop_index('ix_users_username', 'users')
    op.drop_table('users')