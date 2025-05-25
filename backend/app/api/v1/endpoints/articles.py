from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.api.deps import get_current_user, get_admin_user
from app.core.logging import get_request_logger
from app.core.exceptions import ArticleNotFoundError, DuplicateArticleError
from app.db.session import get_async_session
from app.models import User
from app.schemas import Article, ArticleCreate, ArticleURL
from app.crud import article_crud

router = APIRouter()


@router.get("/", response_model=List[Article])
async def read_articles(
    request: Request,
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する最大件数"),
    db: AsyncSession = Depends(get_async_session)
):
    """記事一覧を取得"""
    logger = get_request_logger(request)
    logger.info(f"記事一覧取得リクエスト: skip={skip}, limit={limit}")
    
    try:
        articles = await article_crud.get_multi(db, skip=skip, limit=limit)
        logger.info(f"記事一覧取得成功: {len(articles)}件")
        return articles
        
    except Exception as e:
        logger.error(f"記事一覧取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="記事一覧の取得中にエラーが発生しました"
        )


@router.get("/search", response_model=List[Article])
async def search_articles(
    request: Request,
    q: str = Query(..., min_length=1, description="検索クエリ"),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する最大件数"),
    db: AsyncSession = Depends(get_async_session)
):
    """記事を検索"""
    logger = get_request_logger(request)
    logger.info(f"記事検索リクエスト: query={q}, skip={skip}, limit={limit}")
    
    try:
        articles = await article_crud.search(db, query=q, skip=skip, limit=limit)
        logger.info(f"記事検索成功: {len(articles)}件")
        return articles
        
    except Exception as e:
        logger.error(f"記事検索エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="記事検索中にエラーが発生しました"
        )


@router.get("/{article_number}", response_model=Article)
async def read_article(
    request: Request,
    article_number: str,
    db: AsyncSession = Depends(get_async_session)
):
    """特定の記事を取得"""
    logger = get_request_logger(request)
    logger.info(f"記事取得リクエスト: article_number={article_number}")
    
    try:
        article = await article_crud.get_by_number(db, article_number=article_number)
        if not article:
            logger.warning(f"記事が見つかりません: article_number={article_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="記事が見つかりません"
            )
        
        logger.info(f"記事取得成功: article_number={article_number}")
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"記事取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="記事の取得中にエラーが発生しました"
        )


@router.post("/", response_model=Article, status_code=status.HTTP_201_CREATED)
async def create_article(
    request: Request,
    article: ArticleCreate,
    current_user: User = Depends(get_admin_user),  # 管理者のみ
    db: AsyncSession = Depends(get_async_session)
):
    """新しい記事を作成（管理者のみ）"""
    logger = get_request_logger(request)
    logger.info(f"記事作成リクエスト: user_id={current_user.id}, article_number={article.article_number}")
    
    try:
        new_article = await article_crud.create(db, obj_in=article)
        logger.info(f"記事作成成功: article_number={new_article.article_number}")
        return new_article
        
    except DuplicateArticleError as e:
        logger.warning(f"記事番号重複エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"記事作成エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="記事の作成中にエラーが発生しました"
        )


@router.post("/import", status_code=status.HTTP_200_OK)
async def import_articles_from_csv(
    request: Request,
    file: UploadFile = File(..., description="CSVファイル"),
    current_user: User = Depends(get_admin_user),  # 管理者のみ
    db: AsyncSession = Depends(get_async_session)
):
    """CSVファイルから記事を一括インポート（管理者のみ）"""
    logger = get_request_logger(request)
    logger.info(f"記事CSVインポートリクエスト: user_id={current_user.id}, filename={file.filename}")
    
    try:
        # ファイル形式チェック
        if not file.filename.endswith('.csv'):
            logger.warning(f"無効なファイル形式: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSVファイルのみサポートされています"
            )
        
        # ファイル内容を読み取り
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # インポート実行
        result = await article_crud.import_from_csv(db, csv_content=csv_content)
        
        logger.info(f"記事CSVインポート完了: 成功={result['success']}件, エラー={len(result['errors'])}件, 重複={len(result['duplicates'])}件")
        
        return {
            "message": "CSVインポートが完了しました",
            "success_count": result["success"],
            "error_count": len(result["errors"]),
            "duplicate_count": len(result["duplicates"]),
            "errors": result["errors"],
            "duplicates": result["duplicates"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"記事CSVインポートエラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CSVインポート中にエラーが発生しました"
        )


@router.post("/{article_uuid}/url", response_model=ArticleURL)
async def get_article_url(
    request: Request,
    article_uuid: str,
    db: AsyncSession = Depends(get_async_session)
):
    """記事のURLを生成"""
    logger = get_request_logger(request)
    logger.info(f"記事URL生成リクエスト: article_uuid={article_uuid}")
    
    try:
        # 記事の存在チェック
        article = await article_crud.get_by_uuid(db, article_uuid=article_uuid)
        if not article:
            logger.warning(f"記事が見つかりません: article_uuid={article_uuid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="記事が見つかりません"
            )
        
        # URL生成
        url = article_crud.generate_article_url(article_uuid)
        
        logger.info(f"記事URL生成成功: article_uuid={article_uuid}")
        return ArticleURL(url=url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"記事URL生成エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="記事URLの生成中にエラーが発生しました"
        )
