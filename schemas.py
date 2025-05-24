from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
from models import StatusEnum

# User関連のスキーマ
class UserBase(BaseModel):
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str
    is_admin: Optional[bool] = False

class User(UserBase):
    id: int
    is_admin: bool
    
    class Config:
        from_attributes = True

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

class KnowledgeCreate(KnowledgeBase):
    pass

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

class StatusUpdate(BaseModel):
    status: StatusEnum

class Knowledge(KnowledgeBase):
    id: int
    status: StatusEnum
    created_by: int
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    author: User
    
    class Config:
        from_attributes = True

# レスポンス用のスキーマ
class UserWithKnowledge(User):
    knowledge_items: List[Knowledge] = []
