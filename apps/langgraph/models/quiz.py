from apps.helper.logger import LoggerSingleton
from sqlalchemy import Column, String, DateTime, Float, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from apps.db.session import Base


logger = LoggerSingleton().get_instance()


class QuizModel(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(String, nullable=False)
    question_date_created = Column(DateTime, nullable=False)
    generated_by_user_id = Column(String, nullable=False)
    hint = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    status = Column(String, nullable=False)

    user_answer = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=True)
    answered_by_user_id = Column(String, nullable=True)
    answer_matching = Column(Float, nullable=True)
    answer_date_created = Column(DateTime, nullable=True)
    answer_feedback = Column(Text, nullable=True)
    references = Column(ARRAY(Text), nullable=True)
