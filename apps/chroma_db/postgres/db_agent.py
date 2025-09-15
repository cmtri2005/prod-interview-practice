from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import yaml
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB


DATABASE_URL = f"postgresql://k1:k1@localhost:5435/k2"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# class JD(Base):
#     __tablename__ = "jd"
#     id = Column(String, primary_key=True, index=True)
#     jd_text = Column(Text)
#     jd_json = Column(JSONB)

# class LearningProgress(Base):
#     __tablename__ = "learning_progress"
#     id = Column(String, primary_key=True, index=True)
#     learning_progress_json = Column(JSONB)

# class Message(Base):
#     __tablename__ = "messages"
#     id = Column(String, primary_key=True, index=True)
#     messages_json = Column(JSONB)

# class Knowledge(Base):
#     __tablename__ = "knowledge"
#     id = Column(String, primary_key=True, index=True)
#     content = Column(JSONB)
    
def create_table():
    Base.metadata.create_all(engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    create_table()
    print("Table created!")