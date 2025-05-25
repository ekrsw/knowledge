from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.exceptions import UserNotFoundError, DuplicateUsernameError
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.auth import get_password_hash, verify_password


class UserCRUD:
    """ユーザー関連のCRUD操作"""
    
    async def get(self, db: AsyncSession, id: int) -> Optional[User]:
        """IDでユーザーを取得"""
        result = await db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """ユーザー名でユーザーを取得"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """ユーザー一覧を取得"""
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        """新しいユーザーを作成"""
        # ユーザー名の重複チェック
        existing_user = await self.get_by_username(db, obj_in.username)
        if existing_user:
            raise DuplicateUsernameError(obj_in.username)
        
        hashed_password = get_password_hash(obj_in.password)
        db_obj = User(
            username=obj_in.username,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            is_admin=obj_in.is_admin
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(self, db: AsyncSession, db_obj: User, obj_in: UserUpdate) -> User:
        """ユーザー情報を更新"""
        update_data = obj_in.dict(exclude_unset=True)
        
        # パスワードが含まれている場合はハッシュ化
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, id: int) -> bool:
        """ユーザーを削除"""
        db_obj = await self.get(db, id)
        if not db_obj:
            return False
        
        await db.delete(db_obj)
        await db.commit()
        return True
    
    async def authenticate(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        """ユーザー認証"""
        user = await self.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


# シングルトンインスタンス
user_crud = UserCRUD()
