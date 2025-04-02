from pydantic import BaseModel
from typing import Optional, List
from app.models.common_schemas import SourceTypes


class SummaryQuestion(BaseModel):
    question: str
    answer: str


class AISummaryResponse(BaseModel):
    title: str
    summary_text: str
    source_type: SourceTypes
    related_questions: Optional[List[SummaryQuestion]] = None
    metadata: Optional[dict] = None
