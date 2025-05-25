from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
from typing import Optional, List
from datetime import datetime, date

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

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # リレーションシップ
    knowledge_items: Mapped[List["Knowledge"]] = relationship("Knowledge", back_populates="author", foreign_keys="Knowledge.created_by")
    approved_knowledge_items: Mapped[List["Knowledge"]] = relationship("Knowledge", back_populates="approver", foreign_keys="Knowledge.approved_by")

class Article(Base):
    __tablename__ = "articles"
    
    article_uuid: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)  # URL生成用UUID
    article_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # KBA-01234-AB567
    title: Mapped[str] = mapped_column(String(200))  # 既存記事タイトル
    content: Mapped[Optional[str]] = mapped_column(Text)  # 既存記事内容（参考用）
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # 有効フラグ
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Knowledge(Base):
    __tablename__ = "knowledge"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    article_number: Mapped[str] = mapped_column(String(20), index=True)  # 対象記事番号
    change_type: Mapped[ChangeTypeEnum] = mapped_column(Enum(ChangeTypeEnum))  # 修正案 or 削除案
    title: Mapped[str] = mapped_column(String(200))
    info_category: Mapped[Optional[str]] = mapped_column(String(100))
    keywords: Mapped[Optional[str]] = mapped_column(String(500))
    importance: Mapped[bool] = mapped_column(Boolean, default=False)
    target: Mapped[Optional[str]] = mapped_column(String(200))
    open_publish_start: Mapped[Optional[date]] = mapped_column(Date)
    open_publish_end: Mapped[Optional[date]] = mapped_column(Date)
    question: Mapped[Optional[str]] = mapped_column(Text)
    answer: Mapped[Optional[str]] = mapped_column(Text)
    add_comments: Mapped[Optional[str]] = mapped_column(Text)
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum), default=StatusEnum.draft)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))  # 承認日時
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))  # 承認者ID
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーションシップ
    author: Mapped["User"] = relationship("User", back_populates="knowledge_items", foreign_keys=[created_by])
    approver: Mapped[Optional["User"]] = relationship("User", back_populates="approved_knowledge_items", foreign_keys=[approved_by])
