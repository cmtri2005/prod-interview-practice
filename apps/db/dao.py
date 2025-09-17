# db/dao.py
from sqlalchemy.orm import Session
from apps.chroma_db.postgres import models
from typing import Any


class BaseDAO:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, data: Any):
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)
        return data


class JDDAO(BaseDAO):
    def insert(self, jd_id: str, jd_text: str, jd_json: dict):
        data = models.JD(id=jd_id, jd_text=jd_text, jd_json=jd_json)
        return super().insert(data)


class LearningProgressDAO:
    def insert(self, lp_id: str, lp_json: dict):
        data = models.LearningProgress(id=lp_id, learning_progress_json=lp_json)
        return super().insert(data)


class MessageDAO:
    def insert(self, msg_id: str, msg_json: dict):
        data = models.Message(id=msg_id, messages_json=msg_json)
        return super().insert(data)


class KnowledgeDAO:
    def insert(self, knowledge_text: dict):
        data = models.Knowledge(content=knowledge_text)
        return super().insert(data)
