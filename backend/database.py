# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://<username>:<password>@<endpoint>:3306/<database_name>"

# <username>: RDS 생성 시 설정한 마스터 사용자 이름.
# <password>: RDS 생성 시 설정한 비밀번호.
# <endpoint>: RDS 인스턴스의 엔드포인트.
# <database_name>: 사용할 데이터베이스 이름.

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)