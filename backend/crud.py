from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List, Optional
from datetime import datetime
import models
import schemas
from models import StatusEnum, ChangeTypeEnum
from auth import get_password_hash, verify_password
import csv
import io
import uuid

# User関連のCRUD操作
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """IDでユーザーを取得"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """ユーザー名でユーザーを取得"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """ユーザー一覧を取得"""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """新しいユーザーを作成"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """ユーザー認証"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Article関連のCRUD操作
def get_article_by_uuid(db: Session, article_uuid: str) -> Optional[models.Article]:
    """UUIDで記事を取得"""
    return db.query(models.Article).filter(models.Article.article_uuid == article_uuid).first()

def get_article_by_number(db: Session, article_number: str) -> Optional[models.Article]:
    """記事番号で記事を取得"""
    return db.query(models.Article).filter(models.Article.article_number == article_number).first()

def get_articles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Article]:
    """記事一覧を取得"""
    return db.query(models.Article).filter(models.Article.is_active == True).offset(skip).limit(limit).all()

def search_articles(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[models.Article]:
    """記事番号またはタイトルで記事を検索"""
    return db.query(models.Article).filter(
        models.Article.is_active == True,
        or_(
            models.Article.article_number.contains(query),
            models.Article.title.contains(query)
        )
    ).offset(skip).limit(limit).all()

def create_article(db: Session, article: schemas.ArticleCreate) -> models.Article:
    """新しい記事を作成"""
    db_article = models.Article(
        article_uuid=article.article_uuid,
        article_number=article.article_number,
        title=article.title,
        content=article.content
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def import_articles_from_csv(db: Session, csv_content: str) -> dict:
    """CSVから記事を一括インポート"""
    result = {"success": 0, "errors": [], "duplicates": []}
    
    try:
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        for row_num, row in enumerate(csv_reader, start=2):  # ヘッダー行を考慮して2から開始
            try:
                # 必須フィールドのチェック
                if not all(key in row for key in ['article_uuid', 'article_number', 'title']):
                    result["errors"].append(f"行 {row_num}: 必須フィールドが不足しています")
                    continue
                
                # 重複チェック
                existing_article = get_article_by_number(db, row['article_number'])
                if existing_article:
                    result["duplicates"].append(f"行 {row_num}: 記事番号 {row['article_number']} は既に存在します")
                    continue
                
                # 記事作成
                article_data = schemas.ArticleCreate(
                    article_uuid=row['article_uuid'],
                    article_number=row['article_number'],
                    title=row['title'],
                    content=row.get('content', '')
                )
                
                create_article(db, article_data)
                result["success"] += 1
                
            except Exception as e:
                result["errors"].append(f"行 {row_num}: {str(e)}")
                
    except Exception as e:
        result["errors"].append(f"CSV解析エラー: {str(e)}")
    
    return result

def generate_article_url(article_uuid: str) -> str:
    """記事のURLを生成"""
    base_url = "http://sv-vw-ejap:5555/SupportCenter/main.aspx"
    params = f"?etc=127&extraqs=%3fetc%3d127%26id%3d%257b{article_uuid}%257d&newWindow=true&pagetype=entityrecord"
    return base_url + params

# Knowledge関連のCRUD操作
def get_knowledge(db: Session, knowledge_id: int) -> Optional[models.Knowledge]:
    """IDでナレッジを取得"""
    return db.query(models.Knowledge).filter(models.Knowledge.id == knowledge_id).first()

def get_knowledge_list(db: Session, skip: int = 0, limit: int = 100) -> List[models.Knowledge]:
    """ナレッジ一覧を取得（新しい順）"""
    return db.query(models.Knowledge).order_by(desc(models.Knowledge.created_at)).offset(skip).limit(limit).all()

def get_knowledge_by_status(db: Session, status: StatusEnum, skip: int = 0, limit: int = 100) -> List[models.Knowledge]:
    """ステータス別ナレッジ一覧を取得"""
    return db.query(models.Knowledge).filter(models.Knowledge.status == status).order_by(desc(models.Knowledge.created_at)).offset(skip).limit(limit).all()

def get_knowledge_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Knowledge]:
    """特定ユーザーのナレッジ一覧を取得"""
    return db.query(models.Knowledge).filter(models.Knowledge.created_by == user_id).order_by(desc(models.Knowledge.created_at)).offset(skip).limit(limit).all()

def get_knowledge_by_article(db: Session, article_number: str, skip: int = 0, limit: int = 100) -> List[models.Knowledge]:
    """特定記事に対するナレッジ一覧を取得"""
    return db.query(models.Knowledge).filter(models.Knowledge.article_number == article_number).order_by(desc(models.Knowledge.created_at)).offset(skip).limit(limit).all()

def create_knowledge(db: Session, knowledge: schemas.KnowledgeCreate, user_id: int) -> Optional[models.Knowledge]:
    """新しいナレッジを作成（記事番号バリデーション付き）"""
    # 記事番号の存在チェック
    article = get_article_by_number(db, knowledge.article_number)
    if not article:
        return None
    
    db_knowledge = models.Knowledge(
        article_number=knowledge.article_number,
        change_type=knowledge.change_type,
        title=knowledge.title,
        info_category=knowledge.info_category,
        keywords=knowledge.keywords,
        importance=knowledge.importance,
        target=knowledge.target,
        open_publish_start=knowledge.open_publish_start,
        open_publish_end=knowledge.open_publish_end,
        question=knowledge.question,
        answer=knowledge.answer,
        add_comments=knowledge.add_comments,
        remarks=knowledge.remarks,
        created_by=user_id
    )
    db.add(db_knowledge)
    db.commit()
    db.refresh(db_knowledge)
    return db_knowledge

def update_knowledge(db: Session, knowledge_id: int, knowledge_update: schemas.KnowledgeUpdate, user_id: int) -> Optional[models.Knowledge]:
    """ナレッジを更新"""
    db_knowledge = db.query(models.Knowledge).filter(models.Knowledge.id == knowledge_id, models.Knowledge.created_by == user_id).first()
    if not db_knowledge:
        return None
    
    update_data = knowledge_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_knowledge, field, value)
    
    db.commit()
    db.refresh(db_knowledge)
    return db_knowledge

def update_knowledge_status(db: Session, knowledge_id: int, new_status: StatusEnum, user: models.User) -> Optional[models.Knowledge]:
    """ナレッジのステータスを更新（権限チェック付き）"""
    db_knowledge = db.query(models.Knowledge).filter(models.Knowledge.id == knowledge_id).first()
    if not db_knowledge:
        return None
    
    # 権限チェック
    current_status = db_knowledge.status
    
    # 管理者の場合（最優先）
    if user.is_admin:
        # 全てのステータス変更を許可
        pass
    # 作成者の場合
    elif db_knowledge.created_by == user.id:
        # draft → submitted, submitted → draft のみ許可
        if (current_status == StatusEnum.draft and new_status == StatusEnum.submitted) or \
           (current_status == StatusEnum.submitted and new_status == StatusEnum.draft):
            pass
        else:
            return None
    else:
        # その他のユーザーは変更不可
        return None
    
    db_knowledge.status = new_status
    
    # submitted状態になった時にsubmitted_atを設定
    if new_status == StatusEnum.submitted and current_status != StatusEnum.submitted:
        db_knowledge.submitted_at = datetime.utcnow()
    
    # approved状態になった時にapproved_atとapproved_byを設定
    if new_status == StatusEnum.approved and current_status != StatusEnum.approved:
        db_knowledge.approved_at = datetime.utcnow()
        db_knowledge.approved_by = user.id
    
    # approved状態から他の状態に変更された時にapproved_atとapproved_byをクリア
    if current_status == StatusEnum.approved and new_status != StatusEnum.approved:
        db_knowledge.approved_at = None
        db_knowledge.approved_by = None
    
    db.commit()
    db.refresh(db_knowledge)
    return db_knowledge

def delete_knowledge(db: Session, knowledge_id: int, user_id: int) -> bool:
    """ナレッジを削除"""
    db_knowledge = db.query(models.Knowledge).filter(models.Knowledge.id == knowledge_id, models.Knowledge.created_by == user_id).first()
    if not db_knowledge:
        return False
    
    db.delete(db_knowledge)
    db.commit()
    return True
