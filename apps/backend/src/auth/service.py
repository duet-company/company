"""
Authentication service - user management
"""

from datetime import datetime
from typing import Optional, Dict
import uuid
from models.user import UserInDB, UserCreate, UserRole
from auth.security import get_password_hash, verify_password


# In-memory user storage (replace with PostgreSQL in production)
users_db: Dict[str, UserInDB] = {}


class AuthService:
    """Authentication service for user management"""

    @staticmethod
    async def create_user(user_data: UserCreate) -> UserInDB:
        """Create a new user"""
        # Check if email already exists
        for user in users_db.values():
            if user.email == user_data.email:
                raise ValueError("Email already registered")

        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_data.password)

        user = UserInDB(
            id=user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=user_data.is_active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        users_db[user_id] = user
        return user

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        return users_db.get(user_id)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[UserInDB]:
        """Get user by email"""
        for user in users_db.values():
            if user.email == email:
                return user
        return None

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password"""
        user = await AuthService.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    async def update_user(user_id: str, updates: dict) -> Optional[UserInDB]:
        """Update user"""
        user = users_db.get(user_id)
        if not user:
            return None

        update_data = user.model_dump()
        update_data.update(updates)

        # Handle password update
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        update_data["updated_at"] = datetime.utcnow()

        updated_user = UserInDB(**update_data)
        users_db[user_id] = updated_user
        return updated_user

    @staticmethod
    async def delete_user(user_id: str) -> bool:
        """Delete user"""
        if user_id in users_db:
            del users_db[user_id]
            return True
        return False

    @staticmethod
    async def list_users(skip: int = 0, limit: int = 100) -> list[UserInDB]:
        """List all users"""
        return list(users_db.values())[skip:skip + limit]

    @staticmethod
    async def create_default_admin() -> UserInDB:
        """Create default admin user if none exists"""
        admin_exists = any(
            user.role == UserRole.ADMIN for user in users_db.values()
        )

        if not admin_exists:
            admin_user = UserCreate(
                email="admin@aidatalabs.ai",
                password="admin123",  # Change in production!
                full_name="Admin User",
                role=UserRole.ADMIN,
                is_active=True,
            )
            return await AuthService.create_user(admin_user)

        # Return first admin user
        for user in users_db.values():
            if user.role == UserRole.ADMIN:
                return user
        return None
