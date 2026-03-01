"""Initial database schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-02-28 18:03:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'user', 'guest', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_user_email_active', 'users', ['email', 'is_active'])
    op.create_index('ix_user_role', 'users', ['role'])

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(500), nullable=False),
        sa.Column('refresh_token', sa.String(500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_sessions_token', 'sessions', ['token'], unique=True)
    op.create_index('ix_sessions_refresh_token', 'sessions', ['refresh_token'], unique=True)
    op.create_index('ix_session_user_active', 'sessions', ['user_id', 'is_revoked'])
    op.create_index('ix_session_expires', 'sessions', ['expires_at'])


def downgrade() -> None:
    # Drop sessions table
    op.drop_index('ix_session_expires', table_name='sessions')
    op.drop_index('ix_session_user_active', table_name='sessions')
    op.drop_index('ix_sessions_refresh_token', table_name='sessions')
    op.drop_index('ix_sessions_token', table_name='sessions')
    op.drop_table('sessions')

    # Drop users table
    op.drop_index('ix_user_role', table_name='users')
    op.drop_index('ix_user_email_active', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')

    # Drop enum type
    op.execute('DROP TYPE IF EXISTS userrole')
