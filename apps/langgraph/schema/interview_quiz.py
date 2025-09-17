from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from pydantic import ConfigDict


class QuizOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field()
    history: list = Field()

    question: str = Field()
    question_date_created: datetime = Field()
    generated_by_user_id: str = Field()
    hint: str = Field()
    difficulty: str = Field()
    status: str = Field()
    topic: str = Field()

    user_answer: str | None = Field()
    correct_answer: str | None = Field()
    answered_by_user_id: str | None = Field()
    answer_matching: float | None = Field()
    answer_date_created: datetime | None = Field(default=None)
    answer_feedback: str | None = Field()
    references: list | None = Field()
