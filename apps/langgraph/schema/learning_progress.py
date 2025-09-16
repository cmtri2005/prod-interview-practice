from pydantic import BaseModel, Field
from typing import List
from apps.langgraph.schema.interview_quiz import QuizOut


class Topic(BaseModel):
    quiz: List[QuizOut] = Field(
        default_factory=list,
        description=("List of interview-style question/answer objects related to this topic. Each InterviewQA should include the question text, an ideal answer or rubric, hints, and optionally references or metadata for grading."),
    )
    description: str = Field("", description=( "A concise but informative description of the topic. Explain what learners will understand or be able to do after studying this topic and why it matters within the module."),)
    references: List[str] = Field(
        default_factory=list,
        description=("List of supporting resources for the topic (URLs, book titles, articles, course names, etc.) that learners can consult for deeper study or examples."),
    )


class Module(BaseModel):
    name: str = Field(default="Module error", description="Human-readable title of the module (e.g., 'Data Wrangling and Exploration').",)
    topics: List[Topic] = Field(
        default_factory=list,
        description=("Ordered list of Topic objects that make up the module. Each topic should align with the module's aim and contribute to the module learning outcomes."),
    )
    description: str = Field(default="",description=("Short summary of the module content: scope, key themes, and the main competencies covered."),)
    aims: List[str] = Field(default_factory=list, description=("Clear learning objective for the module: what learners should be able to do or demonstrate after completing the module."),)
    sequence_id: int = Field(default=0,description=("Integer that determines the module's order within the overall learning plan (1-based index). Used for sequencing modules in the roadmap or weekly plan."),)


class LearningProgress(BaseModel):
    modules: List[Module] = Field(default_factory=list, description="List of Module objects included in the learner's plan or progress record.",)
    roadmap: str = Field(default="",description=("Human-readable summary or title of the overall learning roadmap (e.g., '12-week Data Scientist roadmap') or a short status string describing progress."),)


    

    

    