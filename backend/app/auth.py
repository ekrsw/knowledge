from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import secrets

from app.core.config import settings
from app.models import User

# パスワードハッシュ化の設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT設定（設定ファイルから取得）
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """プレーンパスワードとハッシュ化されたパスワードを検証"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """パスワードをハッシュ化"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JTI付きアクセストークンを作成"""
    to_encode = data.copy()
    jti = str(uuid.uuid4())
    to_encode.update({"jti": jti})
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """トークンを検証してユーザー名を返す"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

async def verify_token_with_blacklist(token: str, db: AsyncSession) -> Optional[Dict[str, Any]]:
    """ブラックリストチェック付きトークン検証"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # ブラックリスト機能が有効な場合のみチェック
        if settings.TOKEN_BLACKLIST_ENABLED:
            jti = payload.get("jti")
            if jti:
                # ブラックリストチェック
                from app.crud.token_blacklist import token_blacklist_crud
                is_blacklisted = await token_blacklist_crud.is_blacklisted(db, jti)
                if is_blacklisted:
                    return None
        
        return payload
    except JWTError:
        return None


async def blacklist_token(token: str, db: AsyncSession) -> bool:
    """トークンをブラックリストに追加"""
    if not settings.TOKEN_BLACKLIST_ENABLED:
        return True
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if not jti:
            return False
            
        exp = payload.get("exp")
        expires_at = datetime.utcfromtimestamp(exp)
        
        from app.crud.token_blacklist import token_blacklist_crud
        await token_blacklist_crud.create_blacklist_entry(db, jti, expires_at)
        return True
    except Exception:
        return False


async def create_refresh_token(user_id: int, db: AsyncSession) -> str:
    """リフレッシュトークンを作成してデータベースに保存"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    from app.crud.refresh_token import refresh_token_crud
    await refresh_token_crud.create_refresh_token(db, token, user_id, expires_at)
    return token


async def verify_refresh_token(token: str, db: AsyncSession) -> Optional[int]:
    """リフレッシュトークンを検証してユーザーIDを返す"""
    from app.crud.refresh_token import refresh_token_crud
    refresh_token_obj = await refresh_token_crud.get_by_token(db, token)
    
    if not refresh_token_obj:
        return None
        
    # 有効期限チェック
    if refresh_token_obj.expires_at < datetime.utcnow():
        # 期限切れのトークンを削除
        await refresh_token_crud.delete_refresh_token(db, token)
        return None
        
    return refresh_token_obj.user_id


async def revoke_refresh_token(token: str, db: AsyncSession) -> bool:
    """リフレッシュトークンを無効化"""
    from app.crud.refresh_token import refresh_token_crud
    return await refresh_token_crud.delete_refresh_token(db, token)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """ユーザー認証（非同期版）"""
    from app.crud.user import user_crud
    return await user_crud.authenticate(db, username, password)
