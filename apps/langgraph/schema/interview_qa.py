from pydantic import BaseModel, Field


class InterviewQA(BaseModel):
    id: str = Field()
    topic: str = Field()
    difficulty: str = Field()

    question: str = Field()
    hint: str = Field()
    user_answer: str | None = Field()
    correct_answer: str | None = Field()
    feedback_answer: str | None = Field()
    answer_matching: str | None = Field()
    references: list | None = Field()
    
    
