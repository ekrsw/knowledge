from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from typing import Any

from app.api.deps import get_current_user
from app.auth import (
    create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES,
    create_refresh_token, verify_refresh_token, blacklist_token, 
    verify_token_with_blacklist
)
from app.core.config import settings
from app.core.exceptions import InvalidCredentialsError, DuplicateUsernameError
from app.core.logging import get_request_logger
from app.crud.user import user_crud
from app.db.session import get_async_session
from app.models import User
from app.schemas import UserCreate, User as UserSchema, TokenResponse, RefreshTokenRequest

router = APIRouter()


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session)
):
    """ログインしてアクセストークンとリフレッシュトークンを取得"""
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
        
        # アクセストークンを作成
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # ユーザー名を事前に取得（セッション競合を避けるため）
        username = user.username
        
        # リフレッシュトークンを作成
        refresh_token = await create_refresh_token(user.id, db)
        
        logger.info(f"ログイン成功: ユーザー名={username}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
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


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """リフレッシュトークンを使用してアクセストークンを更新"""
    logger = get_request_logger(request)
    logger.info("リフレッシュトークンリクエスト")
    
    try:
        # リフレッシュトークンを検証
        user_id = await verify_refresh_token(refresh_request.refresh_token, db)
        if not user_id:
            logger.warning("無効なリフレッシュトークン")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なリフレッシュトークンです"
            )
        
        # ユーザー情報を取得
        user = await user_crud.get(db, id=user_id)
        if not user:
            logger.warning(f"ユーザーが見つかりません: user_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザーが見つかりません"
            )
        
        # 新しいアクセストークンを作成
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # 新しいリフレッシュトークンを作成（トークンローテーション）
        new_refresh_token = await create_refresh_token(user.id, db)
        
        # 古いリフレッシュトークンを削除
        from app.crud.refresh_token import refresh_token_crud
        await refresh_token_crud.delete_refresh_token(db, refresh_request.refresh_token)
        
        logger.info(f"トークン更新成功: ユーザー名={user.username}")
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"トークン更新中にエラー: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="トークン更新中にエラーが発生しました"
        )


@router.post("/logout")
async def logout(
    request: Request,
    refresh_request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """ログアウト（トークンを無効化）"""
    logger = get_request_logger(request)
    logger.info(f"ログアウトリクエスト: ユーザー名={current_user.username}")
    
    try:
        # アクセストークンをブラックリストに追加
        from fastapi.security import HTTPBearer
        from fastapi import Request
        
        # リクエストからトークンを取得
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            await blacklist_token(token, db)
        
        # リフレッシュトークンを削除
        from app.crud.refresh_token import refresh_token_crud
        await refresh_token_crud.delete_refresh_token(db, refresh_request.refresh_token)
        
        logger.info(f"ログアウト成功: ユーザー名={current_user.username}")
        return {"message": "ログアウトしました"}
        
    except Exception as e:
        logger.error(f"ログアウト中にエラー: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ログアウト中にエラーが発生しました"
        )


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return current_user
