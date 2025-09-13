from pydantic import BaseModel, Field


class InterviewQA(BaseModel):
    id: str = Field()
    topic: str = Field()
    difficulty: str = Field()

    question: str = Field(default=[], description="The question you want to ask")
    hint: str = Field(default=[], description="A hint regarding how to solve such problem")
    user_answer: str | None = Field(default=[], description="")
    correct_answer: str | None = Field(default=[], description="")
    feedback_answer: str | None = Field(default=[], description="")
    answer_matching: str | None = Field(default=[], description="A float value from 0.0 to 1.0 to compare the matching from my answer to the correct answer.")
    references: list | None = Field(default=[], description="Urls that may help user in the question.")
