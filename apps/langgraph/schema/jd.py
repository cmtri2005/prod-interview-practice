from pydantic import BaseModel, Field
from typing import List


class JD(BaseModel):
    required_hard_skill: List[str] = Field(default=[])
    optional_hard_skill: List[str] = Field(default=[])
    required_soft_skill: List[str] = Field(default=[])
    optional_soft_skill: List[str] = Field(default=[])
