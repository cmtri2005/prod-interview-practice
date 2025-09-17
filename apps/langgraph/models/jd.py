from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from apps.db.session import Base


class JD(Base):
    __tablename__ = "jd"
    id = Column(String, primary_key=True, index=True)
    jd_text = Column(Text)
    jd_json = Column(JSONB)
