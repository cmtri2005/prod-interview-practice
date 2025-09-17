from apps.db.session import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB


class LearningProgress(Base):
    __tablename__ = "learning_progress"
    id = Column(String, primary_key=True, index=True)
    learning_progress_json = Column(JSONB)
