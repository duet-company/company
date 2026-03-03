"""
Session model for authentication token management
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index, func, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from ..database import Base
from .base import TimestampMixin


class Session(Base, TimestampMixin):
    """Session model for storing user authentication sessions"""

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, index=True, nullable=False)
    refresh_token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    # Indexes
    __table_args__ = (
        Index('ix_session_user_active', 'user_id', 'is_revoked'),
        Index('ix_session_expires', 'expires_at'),
    )

    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if session is valid (not expired and not revoked)"""
        return not self.is_expired and not self.is_revoked

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
