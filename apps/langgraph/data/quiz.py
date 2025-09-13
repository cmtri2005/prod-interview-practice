from apps.helper.logger import LoggerSingleton
from apps.langgraph.models.quiz import QuizModel
from apps.db.session import SessionLocal
from typing import List

logger = LoggerSingleton().get_instance()

session = SessionLocal()


def get_quizzes() -> List[QuizModel]:
    try:
        return session.query(QuizModel).all()
    finally:
        session.close()


def get_quiz(quiz_id: str) -> QuizModel:
    try:
        return session.query(QuizModel).filter(QuizModel.id == quiz_id)
    finally:
        session.close()
