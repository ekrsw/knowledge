from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLiteデータベースを使用（本番環境ではPostgreSQLやMySQLを推奨）
SQLALCHEMY_DATABASE_URL = "sqlite:///./knowledge.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# データベースセッションの依存性注入用
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
