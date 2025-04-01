from pydantic import BaseModel, root_validator
from enum import Enum
from typing import Optional, List
from datetime import datetime
from app.models.common_schemas import SourceTypes

class DifficultyEnum(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    very_hard = "very_hard"


class ContentSource(BaseModel):
    url: Optional[str] = None


class QuizCreate(BaseModel):
    quiz_source: SourceTypes  # Updated to use SourceTypes
    quiz_topic: Optional[str] = None
    difficulty: DifficultyEnum
    content_source: Optional[ContentSource] = None
    prompt: Optional[str] = None
    number_of_questions: int = 5

    @root_validator(pre=True)
    def check_content_source(cls, values):
        quiz_source = values.get("quiz_source")
        content_source = values.get("content_source")
        if quiz_source in {SourceTypes.YOUTUBE, SourceTypes.ARTICLE}:
            if not (content_source and content_source.get("url")):
                raise ValueError("ContentSource.url is required for youtube and article quizzes.")
        return values


class AttemptChoice(BaseModel):
    question_id: str
    selected_choice_id: str


class QuizAttemptCreate(BaseModel):
    quiz_id: str
    responses: List[AttemptChoice]


class QuizChoice(BaseModel):
    choice_id: str
    choice_text: str
    choice_explanation: str


class QuizQuestion(BaseModel):
    question_id: str
    question_text: str
    choices: List[QuizChoice]
    correct_choice_id: str
    answer_explanation: str


class AIQuizResponse(BaseModel):
    quiz_title: str
    difficulty: str
    category: str
    questions: List[QuizQuestion]


class Question(BaseModel):
    question_id: str
    question_text: str
    choices: List[dict]
    correct_choice_id: str
    answer_explanation: str


class Quiz(BaseModel):
    quiz_id: str
    quiz_title: str
    difficulty: DifficultyEnum
    category: str
    questions: List[Question]
    quiz_source: SourceTypes  # Updated to use SourceTypes
    source_id: str
    created_by: str
    created_at: datetime
    metadata: dict
