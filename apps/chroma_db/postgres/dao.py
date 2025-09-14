# db/dao.py
from sqlalchemy.orm import Session
from apps.chroma_db.postgres import models

class JDDAO:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, jd_id: str, jd_text: str, jd_json: dict):
        data = models.JD(id=jd_id, jd_text=jd_text, jd_json=jd_json)
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)
        return data

class LearningProgressDAO:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, lp_id: str, lp_json: dict):
        data = models.LearningProgress(id=lp_id, learning_progress_json=lp_json)
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)
        return data

class MessageDAO:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, msg_id : str, msg_json: dict):
        data = models.Message(id = msg_id, messages_json=msg_json)
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)
        return data

class KnowledgeDAO:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, know_text: dict):
        data = models.Knowledge(know_content=know_text)
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)
        return data