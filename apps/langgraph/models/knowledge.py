from apps.db.session import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB


class Knowledge(Base):
    __tablename__ = "knowledge"
    id = Column(String, primary_key=True, index=True)
    content = Column(JSONB)
