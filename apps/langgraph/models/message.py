from apps.db.session import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB


class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, index=True)
    messages_json = Column(JSONB)
