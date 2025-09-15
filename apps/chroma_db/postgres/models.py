# db/models.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from apps.chroma_db.postgres.db_agent import Base

class JD(Base):
    __tablename__ = "jd"
    id = Column(String, primary_key=True, index=True)
    jd_text = Column(Text)
    jd_json = Column(JSONB)

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    id = Column(String, primary_key=True, index=True)
    learning_progress_json = Column(JSONB)

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, index=True)
    messages_json = Column(JSONB)

class Knowledge(Base):
    __tablename__ = "knowledge"
    id = Column(String, primary_key=True, index=True)
    content = Column(JSONB)
    