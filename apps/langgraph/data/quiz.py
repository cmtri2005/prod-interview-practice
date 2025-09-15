from apps.helper.logger import LoggerSingleton
from apps.langgraph.models.quiz import QuizModel
from apps.db.session import SessionLocal
from typing import List
import uuid
from datetime import datetime, timezone

logger = LoggerSingleton().get_instance()


def get_quizzes() -> List[QuizModel]:
    session = SessionLocal()
    try:
        return session.query(QuizModel).all()
    finally:
        session.close()


def get_quiz(quiz_id: str) -> QuizModel:
    session = SessionLocal()
    try:
        # Convert string to UUID
        quiz_uuid = uuid.UUID(quiz_id)
        return session.query(QuizModel).filter(QuizModel.id == quiz_uuid).first()
    finally:
        session.close()

def generate_quiz(
    history: List,
    question: str,
    generated_by_user_id: str,
    hint: str,
    difficulty: str,
    topic: str,
) -> QuizModel:
    session = SessionLocal()
    quiz = QuizModel(
        history=history,
        question=question,
        question_date_created=datetime.now(timezone.utc),
        generated_by_user_id=generated_by_user_id,
        hint=hint,
        difficulty=difficulty,
        topic=topic,
        status="active",
        user_answer=None,
        correct_answer=None,
        answered_by_user_id=None,
        answer_matching=None,
        answer_date_created=None,
        answer_feedback=None,
        references=None,
    )
    session.add(quiz)
    session.commit()
    session.close()
    return quiz
    