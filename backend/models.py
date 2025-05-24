from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class StatusEnum(enum.Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    published = "published"

class ChangeTypeEnum(enum.Enum):
    modify = "modify"
    delete = "delete"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # リレーションシップ
    knowledge_items = relationship("Knowledge", back_populates="author", foreign_keys="Knowledge.created_by")
    approved_knowledge_items = relationship("Knowledge", back_populates="approver", foreign_keys="Knowledge.approved_by")

class Article(Base):
    __tablename__ = "articles"
    
    article_uuid = Column(String(36), primary_key=True, index=True)  # URL生成用UUID
    article_number = Column(String(20), unique=True, nullable=False, index=True)  # KBA-01234-AB567
    title = Column(String(200), nullable=False)  # 既存記事タイトル
    content = Column(Text, nullable=True)  # 既存記事内容（参考用）
    is_active = Column(Boolean, default=True, nullable=False)  # 有効フラグ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Knowledge(Base):
    __tablename__ = "knowledge"

    id = Column(Integer, primary_key=True, index=True)
    article_number = Column(String(20), nullable=False, index=True)  # 対象記事番号
    change_type = Column(Enum(ChangeTypeEnum), nullable=False)  # 修正案 or 削除案
    title = Column(String(200), nullable=False)
    info_category = Column(String(100), nullable=True)
    keywords = Column(String(500), nullable=True)
    importance = Column(Boolean, default=False, nullable=False)
    target = Column(String(200), nullable=True)
    open_publish_start = Column(Date, nullable=True)
    open_publish_end = Column(Date, nullable=True)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    add_comments = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.draft, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)  # 承認日時
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 承認者ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーションシップ
    author = relationship("User", back_populates="knowledge_items", foreign_keys=[created_by])
    approver = relationship("User", back_populates="approved_knowledge_items", foreign_keys=[approved_by])
