from pydantic import BaseModel, Field
from typing import List


class JD(BaseModel):
    required_hard_skill: List[str] = Field(
        default_factory=list,
        description=(
            "List of mandatory technical (hard) skills explicitly required by the job posting."
        ),
    )
    optional_hard_skill: List[str] = Field(
        default_factory=list,
        description=(
            "List of desirable or nice-to-have technical (hard) skills mentioned in the JD but not strictly required."
        ),
    )
    required_soft_skill: List[str] = Field(
        default_factory=list,
        description=(
            "List of mandatory interpersonal or non-technical skills that the employer expects. Examples: 'communication', 'teamwork', 'problem solving'."
        ),
    )
    optional_soft_skill: List[str] = Field(
        default_factory=list,
        description=(
            "List of preferred soft skills that are nice-to-have but not required. Examples: 'leadership', 'mentoring', 'presentation skills'."
        ),
    )
