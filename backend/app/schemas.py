from pydantic import BaseModel, field_validator
from datetime import datetime, date
from typing import List, Optional
from app.models import StatusEnum, ChangeTypeEnum

# User関連のスキーマ
class UserBase(BaseModel):
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str
    is_admin: Optional[bool] = False

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

class User(UserBase):
    id: int
    is_admin: bool
    
    class Config:
        from_attributes = True

# Article関連のスキーマ
class ArticleBase(BaseModel):
    article_number: str
    title: str
    content: Optional[str] = None

class ArticleCreate(ArticleBase):
    article_uuid: str

class ArticleImport(BaseModel):
    article_uuid: str
    article_number: str
    title: str
    content: Optional[str] = None

class Article(ArticleBase):
    article_uuid: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ArticleSearch(BaseModel):
    article_uuid: str
    article_number: str
    title: str
    is_active: bool

class ArticleURL(BaseModel):
    url: str

# Knowledge関連のスキーマ
class KnowledgeBase(BaseModel):
    title: str
    info_category: Optional[str] = None
    keywords: Optional[str] = None
    importance: bool = False
    target: Optional[str] = None
    open_publish_start: Optional[date] = None
    open_publish_end: Optional[date] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    add_comments: Optional[str] = None
    remarks: Optional[str] = None

    @field_validator('open_publish_start', 'open_publish_end', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

class KnowledgeCreate(KnowledgeBase):
    article_number: str
    change_type: ChangeTypeEnum

class KnowledgeUpdate(BaseModel):
    title: Optional[str] = None
    info_category: Optional[str] = None
    keywords: Optional[str] = None
    importance: Optional[bool] = None
    target: Optional[str] = None
    open_publish_start: Optional[date] = None
    open_publish_end: Optional[date] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    add_comments: Optional[str] = None
    remarks: Optional[str] = None

    @field_validator('open_publish_start', 'open_publish_end', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

class StatusUpdate(BaseModel):
    status: StatusEnum

class Knowledge(KnowledgeBase):
    id: int
    article_number: str
    change_type: ChangeTypeEnum
    status: StatusEnum
    created_by: int
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None  # 承認日時
    approved_by: Optional[int] = None  # 承認者ID
    created_at: datetime
    updated_at: datetime
    author: User
    approver: Optional[User] = None  # 承認者情報
    
    class Config:
        from_attributes = True

# 認証関連のスキーマ
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# レスポンス用のスキーマ
class UserWithKnowledge(User):
    knowledge_items: List[Knowledge] = []
