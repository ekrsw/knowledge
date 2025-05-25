from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from typing import Any

from app.api.deps import get_current_user
from app.auth import create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.config import settings
from app.core.exceptions import InvalidCredentialsError, DuplicateUsernameError
from app.core.logging import get_request_logger
from app.crud.user import user_crud
from app.db.session import get_async_session
from app.models import User
from app.schemas import UserCreate, User as UserSchema

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session)
):
    """ログインしてアクセストークンを取得"""
    logger = get_request_logger(request)
    logger.info(f"ログインリクエスト: ユーザー名={form_data.username}")
    
    try:
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"ログイン失敗: ユーザー名={form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザー名またはパスワードが正しくありません",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        logger.info(f"ログイン成功: ユーザー名={user.username}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ログイン処理中にエラー: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ログイン処理中にエラーが発生しました"
        )


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request,
    user: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """新しいユーザーを作成"""
    logger = get_request_logger(request)
    logger.info(f"ユーザー登録リクエスト: ユーザー名={user.username}")
    
    try:
        # ユーザー名の重複チェック
        existing_user = await user_crud.get_by_username(db, username=user.username)
        if existing_user:
            logger.warning(f"ユーザー名重複: {user.username}")
            raise HTTPException(
                status_code=400, 
                detail="ユーザー名が既に使用されています"
            )
        
        db_user = await user_crud.create(db=db, obj_in=user)
        logger.info(f"ユーザー登録成功: ユーザー名={db_user.username}")
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ユーザー登録中にエラー: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ユーザー登録中にエラーが発生しました"
        )


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return current_user
