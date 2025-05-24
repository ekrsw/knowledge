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

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # リレーションシップ
    knowledge_items = relationship("Knowledge", back_populates="author")

class Knowledge(Base):
    __tablename__ = "knowledge"

    id = Column(Integer, primary_key=True, index=True)
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーションシップ
    author = relationship("User", back_populates="knowledge_items")
