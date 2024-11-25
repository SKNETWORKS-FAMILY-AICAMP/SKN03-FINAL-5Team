from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from config import DATABASE_URL  # settings.py에서 로드한 DATABASE_URL 사용

# MySQL 연결을 위한 엔진 생성
engine = create_engine(DATABASE_URL, pool_recycle=3600)

# 세션 로컬 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 테이블 생성 (없으면 생성)
Base.metadata.create_all(bind=engine)
