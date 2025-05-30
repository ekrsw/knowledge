from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from app.core.exceptions import InvalidTokenError, UserNotFoundError
from app.db.session import get_async_session
from app.models import User
from app.auth import verify_token_with_blacklist
from app.crud.user import user_crud

# セキュリティ設定
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session)
) -> User:
    """現在のユーザーを取得する依存性（ブラックリストチェック付き）"""
    token = credentials.credentials
    
    try:
        payload = await verify_token_with_blacklist(token, db)
        if payload is None:
            raise InvalidTokenError()
        
        username = payload.get("sub")
        if username is None:
            raise InvalidTokenError()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user = await user_crud.get_by_username(db, username=username)
        if user is None:
            raise UserNotFoundError(username=username)
        return user
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つかりません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ユーザー情報の取得中にエラーが発生しました"
        )


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """管理者権限チェック"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )
    return current_user
