from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import models
import schemas
from models import StatusEnum
from auth import get_password_hash, verify_password

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

def create_knowledge(db: Session, knowledge: schemas.KnowledgeCreate, user_id: int) -> models.Knowledge:
    """新しいナレッジを作成"""
    db_knowledge = models.Knowledge(
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
    
    # 作成者の場合
    if db_knowledge.created_by == user.id:
        # draft → submitted, submitted → draft のみ許可
        if (current_status == StatusEnum.draft and new_status == StatusEnum.submitted) or \
           (current_status == StatusEnum.submitted and new_status == StatusEnum.draft):
            pass
        else:
            return None
    # 管理者の場合
    elif user.is_admin:
        # 全てのステータス変更を許可
        pass
    else:
        # その他のユーザーは変更不可
        return None
    
    db_knowledge.status = new_status
    
    # submitted状態になった時にsubmitted_atを設定
    if new_status == StatusEnum.submitted and current_status != StatusEnum.submitted:
        db_knowledge.submitted_at = datetime.utcnow()
    
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
