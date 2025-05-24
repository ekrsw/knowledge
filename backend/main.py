from fastapi import FastAPI, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

import models
import schemas
import crud
from database import SessionLocal, engine, get_db
from auth import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from models import StatusEnum, ChangeTypeEnum

# データベーステーブルを作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ナレッジ投稿システム", version="2.0.0")

# セキュリティ設定
security = HTTPBearer()

# 現在のユーザーを取得する依存性
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つかりません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# 管理者権限チェック
def get_admin_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )
    return current_user

# ユーザー関連のエンドポイント
@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """新しいユーザーを作成"""
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="ユーザー名が既に使用されています")
    return crud.create_user(db=db, user=user)

@app.post("/token")
def login_for_access_token(username: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    """ログインしてアクセストークンを取得"""
    user = crud.authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ユーザー一覧を取得"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.UserWithKnowledge)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """特定のユーザーとナレッジを取得"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return db_user

@app.get("/users/me/", response_model=schemas.UserWithKnowledge)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return current_user

# Article関連のエンドポイント
@app.post("/articles/import", status_code=status.HTTP_201_CREATED)
def import_articles(file: UploadFile = File(...), admin_user: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """CSVファイルから記事を一括インポート（管理者のみ）"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="CSVファイルのみアップロード可能です")
    
    try:
        csv_content = file.file.read().decode('utf-8')
        result = crud.import_articles_from_csv(db, csv_content)
        return {
            "message": f"{result['success']}件の記事をインポートしました",
            "success_count": result['success'],
            "errors": result['errors'],
            "duplicates": result['duplicates']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"インポートエラー: {str(e)}")

@app.get("/articles/", response_model=List[schemas.Article])
def read_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """記事一覧を取得"""
    articles = crud.get_articles(db, skip=skip, limit=limit)
    return articles

@app.get("/articles/search", response_model=List[schemas.ArticleSearch])
def search_articles(q: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """記事番号またはタイトルで記事を検索"""
    if not q.strip():
        raise HTTPException(status_code=400, detail="検索クエリが必要です")
    
    articles = crud.search_articles(db, query=q, skip=skip, limit=limit)
    return articles

@app.get("/articles/{article_number}", response_model=schemas.Article)
def read_article_by_number(article_number: str, db: Session = Depends(get_db)):
    """記事番号で特定の記事を取得"""
    article = crud.get_article_by_number(db, article_number=article_number)
    if article is None:
        raise HTTPException(status_code=404, detail="記事が見つかりません")
    return article

@app.get("/articles/uuid/{article_uuid}", response_model=schemas.Article)
def read_article_by_uuid(article_uuid: str, db: Session = Depends(get_db)):
    """UUIDで特定の記事を取得"""
    article = crud.get_article_by_uuid(db, article_uuid=article_uuid)
    if article is None:
        raise HTTPException(status_code=404, detail="記事が見つかりません")
    return article

@app.get("/articles/uuid/{article_uuid}/url", response_model=schemas.ArticleURL)
def get_article_url(article_uuid: str, db: Session = Depends(get_db)):
    """記事の外部システムURLを生成"""
    article = crud.get_article_by_uuid(db, article_uuid=article_uuid)
    if article is None:
        raise HTTPException(status_code=404, detail="記事が見つかりません")
    
    url = crud.generate_article_url(article_uuid)
    return {"url": url}

@app.get("/articles/{article_number}/proposals", response_model=List[schemas.Knowledge])
def read_article_proposals(article_number: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """特定記事に対する修正・削除案一覧を取得"""
    # 記事の存在確認
    article = crud.get_article_by_number(db, article_number=article_number)
    if article is None:
        raise HTTPException(status_code=404, detail="記事が見つかりません")
    
    proposals = crud.get_knowledge_by_article(db, article_number=article_number, skip=skip, limit=limit)
    return proposals

# ナレッジ関連のエンドポイント
@app.post("/knowledge/", response_model=schemas.Knowledge, status_code=status.HTTP_201_CREATED)
def create_knowledge(knowledge: schemas.KnowledgeCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """新しいナレッジ（修正・削除案）を作成"""
    db_knowledge = crud.create_knowledge(db=db, knowledge=knowledge, user_id=current_user.id)
    if db_knowledge is None:
        raise HTTPException(status_code=404, detail="指定された記事番号が見つかりません")
    return db_knowledge

@app.get("/knowledge/", response_model=List[schemas.Knowledge])
def read_knowledge_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ナレッジ一覧を取得"""
    knowledge_list = crud.get_knowledge_list(db, skip=skip, limit=limit)
    return knowledge_list

@app.get("/knowledge/status/{status}", response_model=List[schemas.Knowledge])
def read_knowledge_by_status(status: StatusEnum, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ステータス別ナレッジ一覧を取得"""
    knowledge_list = crud.get_knowledge_by_status(db, status=status, skip=skip, limit=limit)
    return knowledge_list

@app.get("/knowledge/{knowledge_id}", response_model=schemas.Knowledge)
def read_knowledge(knowledge_id: int, db: Session = Depends(get_db)):
    """特定のナレッジを取得"""
    db_knowledge = crud.get_knowledge(db, knowledge_id=knowledge_id)
    if db_knowledge is None:
        raise HTTPException(status_code=404, detail="ナレッジが見つかりません")
    return db_knowledge

@app.put("/knowledge/{knowledge_id}", response_model=schemas.Knowledge)
def update_knowledge(knowledge_id: int, knowledge_update: schemas.KnowledgeUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """ナレッジを更新"""
    db_knowledge = crud.update_knowledge(db, knowledge_id=knowledge_id, knowledge_update=knowledge_update, user_id=current_user.id)
    if db_knowledge is None:
        raise HTTPException(status_code=404, detail="ナレッジが見つからないか、更新権限がありません")
    return db_knowledge

@app.put("/knowledge/{knowledge_id}/status", response_model=schemas.Knowledge)
def update_knowledge_status(knowledge_id: int, status_update: schemas.StatusUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """ナレッジのステータスを更新"""
    db_knowledge = crud.update_knowledge_status(db, knowledge_id=knowledge_id, new_status=status_update.status, user=current_user)
    if db_knowledge is None:
        raise HTTPException(status_code=404, detail="ナレッジが見つからないか、ステータス変更権限がありません")
    return db_knowledge

@app.delete("/knowledge/{knowledge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge(knowledge_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """ナレッジを削除"""
    success = crud.delete_knowledge(db, knowledge_id=knowledge_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="ナレッジが見つからないか、削除権限がありません")

@app.get("/users/{user_id}/knowledge/", response_model=List[schemas.Knowledge])
def read_user_knowledge(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """特定ユーザーのナレッジ一覧を取得"""
    knowledge_list = crud.get_knowledge_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return knowledge_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
