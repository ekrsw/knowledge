from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.api.deps import get_current_user, get_admin_user
from app.core.logging import get_request_logger
from app.core.exceptions import KnowledgeNotFoundError, ArticleNotFoundError, InvalidKnowledgeStatusError
from app.db.session import get_async_session
from app.models import User, StatusEnum
from app.schemas import Knowledge, KnowledgeCreate, KnowledgeUpdate, StatusUpdate
from app.crud import knowledge_crud, article_crud

router = APIRouter()


@router.get("/", response_model=List[Knowledge])
async def read_knowledge_list(
    request: Request,
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する最大件数"),
    status: Optional[StatusEnum] = Query(None, description="ステータスでフィルタ"),
    user_id: Optional[int] = Query(None, description="ユーザーIDでフィルタ"),
    article_number: Optional[str] = Query(None, description="記事番号でフィルタ"),
    db: AsyncSession = Depends(get_async_session)
):
    """ナレッジ一覧を取得"""
    logger = get_request_logger(request)
    logger.info(f"ナレッジ一覧取得リクエスト: skip={skip}, limit={limit}, status={status}, user_id={user_id}, article_number={article_number}")
    
    try:
        if status:
            knowledge_list = await knowledge_crud.get_by_status(db, status=status, skip=skip, limit=limit)
        elif user_id:
            knowledge_list = await knowledge_crud.get_by_user(db, user_id=user_id, skip=skip, limit=limit)
        elif article_number:
            knowledge_list = await knowledge_crud.get_by_article(db, article_number=article_number, skip=skip, limit=limit)
        else:
            knowledge_list = await knowledge_crud.get_multi(db, skip=skip, limit=limit)
        
        logger.info(f"ナレッジ一覧取得成功: {len(knowledge_list)}件")
        return knowledge_list
        
    except Exception as e:
        logger.error(f"ナレッジ一覧取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ナレッジ一覧の取得中にエラーが発生しました"
        )


@router.get("/{knowledge_id}", response_model=Knowledge)
async def read_knowledge(
    request: Request,
    knowledge_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """特定のナレッジを取得"""
    logger = get_request_logger(request)
    logger.info(f"ナレッジ取得リクエスト: knowledge_id={knowledge_id}")
    
    try:
        knowledge = await knowledge_crud.get(db, id=knowledge_id)
        if not knowledge:
            logger.warning(f"ナレッジが見つかりません: knowledge_id={knowledge_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ナレッジが見つかりません"
            )
        
        logger.info(f"ナレッジ取得成功: knowledge_id={knowledge_id}")
        return knowledge
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ナレッジ取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ナレッジの取得中にエラーが発生しました"
        )


@router.post("/", response_model=Knowledge, status_code=status.HTTP_201_CREATED)
async def create_knowledge(
    request: Request,
    knowledge: KnowledgeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """新しいナレッジを作成"""
    logger = get_request_logger(request)
    logger.info(f"ナレッジ作成リクエスト: user_id={current_user.id}, article_number={knowledge.article_number}")
    
    try:
        # 記事番号の存在チェック
        article = await article_crud.get_by_number(db, knowledge.article_number)
        if not article:
            logger.warning(f"記事が見つかりません: article_number={knowledge.article_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"記事番号 '{knowledge.article_number}' が見つかりません"
            )
        
        # ナレッジ作成
        new_knowledge = await knowledge_crud.create(db, obj_in=knowledge, user_id=current_user.id)
        
        logger.info(f"ナレッジ作成成功: knowledge_id={new_knowledge.id}")
        return new_knowledge
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ナレッジ作成エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ナレッジの作成中にエラーが発生しました"
        )


@router.put("/{knowledge_id}", response_model=Knowledge)
async def update_knowledge(
    request: Request,
    knowledge_id: int,
    knowledge_update: KnowledgeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """ナレッジを更新"""
    logger = get_request_logger(request)
    logger.info(f"ナレッジ更新リクエスト: knowledge_id={knowledge_id}, user_id={current_user.id}")
    
    try:
        # ナレッジの存在チェック
        knowledge = await knowledge_crud.get(db, id=knowledge_id)
        if not knowledge:
            logger.warning(f"ナレッジが見つかりません: knowledge_id={knowledge_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ナレッジが見つかりません"
            )
        
        # 権限チェック（作成者または管理者のみ）
        if knowledge.created_by != current_user.id and not current_user.is_admin:
            logger.warning(f"ナレッジ更新権限なし: knowledge_id={knowledge_id}, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="このナレッジを更新する権限がありません"
            )
        
        # ナレッジ更新
        updated_knowledge = await knowledge_crud.update(db, db_obj=knowledge, obj_in=knowledge_update)
        
        logger.info(f"ナレッジ更新成功: knowledge_id={knowledge_id}")
        return updated_knowledge
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ナレッジ更新エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ナレッジの更新中にエラーが発生しました"
        )


@router.patch("/{knowledge_id}/status", response_model=Knowledge)
async def update_knowledge_status(
    request: Request,
    knowledge_id: int,
    status_update: StatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """ナレッジのステータスを更新"""
    logger = get_request_logger(request)
    logger.info(f"ナレッジステータス更新リクエスト: knowledge_id={knowledge_id}, new_status={status_update.status}, user_id={current_user.id}")
    
    try:
        # ナレッジの存在チェック
        knowledge = await knowledge_crud.get(db, id=knowledge_id)
        if not knowledge:
            logger.warning(f"ナレッジが見つかりません: knowledge_id={knowledge_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ナレッジが見つかりません"
            )
        
        # ステータス更新（権限チェックはCRUD内で実行）
        try:
            updated_knowledge = await knowledge_crud.update_status(
                db, db_obj=knowledge, new_status=status_update.status, user=current_user
            )
            
            logger.info(f"ナレッジステータス更新成功: knowledge_id={knowledge_id}, new_status={status_update.status}")
            return updated_knowledge
            
        except KnowledgeNotFoundError:
            logger.warning(f"ナレッジステータス更新権限なし: knowledge_id={knowledge_id}, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="このナレッジのステータスを変更する権限がありません"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ナレッジステータス更新エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ナレッジステータスの更新中にエラーが発生しました"
        )


@router.post("/{knowledge_id}/submit", response_model=Knowledge)
async def submit_knowledge(
    request: Request,
    knowledge_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """ナレッジを提出（ステータスをsubmittedに変更）"""
    logger = get_request_logger(request)
    logger.info(f"ナレッジ提出リクエスト: knowledge_id={knowledge_id}, user_id={current_user.id}")
    
    try:
        # ナレッジの存在チェック
        knowledge = await knowledge_crud.get(db, id=knowledge_id)
        if not knowledge:
            logger.warning(f"ナレッジが見つかりません: knowledge_id={knowledge_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ナレッジが見つかりません"
            )
        
        # ステータス更新（submitted）
        try:
            updated_knowledge = await knowledge_crud.update_status(
                db, db_obj=knowledge, new_status=StatusEnum.submitted, user=current_user
            )
            
            logger.info(f"ナレッジ提出成功: knowledge_id={knowledge_id}")
            return updated_knowledge
            
        except KnowledgeNotFoundError:
            logger.warning(f"ナレッジ提出権限なし: knowledge_id={knowledge_id}, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="このナレッジを提出する権限がありません"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ナレッジ提出エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ナレッジの提出中にエラーが発生しました"
        )




@router.post("/{knowledge_id}/approve", response_model=Knowledge)
async def approve_knowledge(
    request: Request,
    knowledge_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session)
):
    """ナレッジを承認（ステータスをapprovedに変更）"""
    logger = get_request_logger(request)
    logger.info(f"ナレッジ承認リクエスト: knowledge_id={knowledge_id}, user_id={current_user.id}")
    
    try:
        # ナレッジの存在チェック
        knowledge = await knowledge_crud.get(db, id=knowledge_id)
        if not knowledge:
            logger.warning(f"ナレッジが見つかりません: knowledge_id={knowledge_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ナレッジが見つかりません"
            )
        
        # ステータスチェック（submittedである必要がある）
        if knowledge.status != StatusEnum.submitted:
            logger.warning(f"ナレッジのステータスが無効: knowledge_id={knowledge_id}, current_status={knowledge.status.value}")
            raise InvalidKnowledgeStatusError(
                knowledge_id=knowledge_id,
                current_status=knowledge.status.value,
                required_status=StatusEnum.submitted.value
            )
        
        # ステータス更新（approved）
        try:
            updated_knowledge = await knowledge_crud.update_status(
                db, db_obj=knowledge, new_status=StatusEnum.approved, user=current_user
            )
            
            logger.info(f"ナレッジ承認成功: knowledge_id={knowledge_id}")
            return updated_knowledge
            
        except KnowledgeNotFoundError:
            logger.warning(f"ナレッジ承認権限なし: knowledge_id={knowledge_id}, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="このナレッジを承認する権限がありません"
            )
        
    except InvalidKnowledgeStatusError as e:
        logger.warning(f"ナレッジステータスエラー: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ナレッジ承認エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ナレッジの承認中にエラーが発生しました"
        )


@router.delete("/{knowledge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge(
    request: Request,
    knowledge_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """ナレッジを削除"""
    logger = get_request_logger(request)
    logger.info(f"ナレッジ削除リクエスト: knowledge_id={knowledge_id}, user_id={current_user.id}")
    
    try:
        # 削除実行（権限チェックはCRUD内で実行）
        deleted = await knowledge_crud.delete(db, id=knowledge_id, user_id=current_user.id)
        
        if not deleted:
            logger.warning(f"ナレッジ削除権限なしまたは見つかりません: knowledge_id={knowledge_id}, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ナレッジが見つからないか、削除する権限がありません"
            )
        
        logger.info(f"ナレッジ削除成功: knowledge_id={knowledge_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ナレッジ削除エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ナレッジの削除中にエラーが発生しました"
        )
