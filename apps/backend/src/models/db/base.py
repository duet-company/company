"""
Base model with common fields
"""

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declared_attr
from ..database import Base


class TimestampMixin:
    """Mixin for adding timestamp fields"""
    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base):
    """Base model with common fields and methods"""
    __abstract__ = True

    def to_dict(self):
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        """String representation"""
        class_name = self.__class__.__name__
        return f"<{class_name} {self.to_dict()}>"
