"""
User model for authentication and authorization
"""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as PyEnum

from ..database import Base
from .base import TimestampMixin


class UserRole(str, PyEnum):
    """User roles"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(Base, TimestampMixin):
    """User model for storing user accounts"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_user_email_active', 'email', 'is_active'),
        Index('ix_user_role', 'role'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role={self.role})>"

    def to_dict(self):
        """Convert to dictionary, excluding sensitive data"""
        data = super().to_dict()
        data.pop("hashed_password", None)
        return data
