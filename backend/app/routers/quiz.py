from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, root_validator
from enum import Enum
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import get_database
from app.utils.auth import get_current_user, User
from app.utils.quiz import generate_quiz

router = APIRouter()


class DifficultyEnum(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    very_hard = "very_hard"


class QuizSourceEnum(str, Enum):
    manual = "manual"
    youtube = "youtube"
    article = "article"


class ContentSource(BaseModel):
    url: Optional[str] = None
    # pdfId: Optional[str] = None
    # ...other possible fields...


class QuizCreate(BaseModel):
    quizSource: QuizSourceEnum
    quizTopic: Optional[str] = None
    difficulty: DifficultyEnum
    contentSource: Optional[ContentSource] = None
    prompt: Optional[str] = None
    numberOfQuestions: int = 5  # added new field for number of questions

    @root_validator(pre=True)
    def check_content_source(cls, values):
        quiz_source = values.get("quizSource")
        content_source = values.get("contentSource")
        if quiz_source in {"youtube", "article"}:
            if not (content_source and content_source.get("url")):
                raise ValueError("ContentSource.url is required for youtube and article quizzes.")
        return values


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_quiz(quiz_data: QuizCreate,
                      current_user: User = Depends(get_current_user)
                      ):
    result = generate_quiz(quiz_data)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    ai_quiz = result.get("quiz", {})
    # If ai_quiz is a list, wrap it into a dict
    if isinstance(ai_quiz, list):
        ai_quiz = {
            "quizTitle": "Untitled Quiz",
            "questions": ai_quiz,
            "category": ""
        }
    quiz_doc = {
        "quiz_id": ai_quiz.get("quiz_id", str(ObjectId())),
        "quizTitle": ai_quiz.get("quizTitle", "Untitled Quiz"),
        "difficulty": quiz_data.difficulty,
        "category": ai_quiz.get("category", ""),
        "quiz_source": result.get("quiz_source"),
        "source_id": result.get("source_id"),
        "created_by": current_user.user_id,
        "created_at": datetime.utcnow(),
        "questions": ai_quiz.get("questions", []),
    }

    db = get_database()
    insert_result = await db.quizzes.insert_one(quiz_doc)
    if not insert_result.inserted_id:
        raise HTTPException(status_code=500, detail="Unable to create quiz.")

    return {"message": "Quiz created successfully", "quiz_id": quiz_doc["quiz_id"]}


@router.get("/myquizzes", status_code=200)
async def get_all_quizzes(current_user: User = Depends(get_current_user)):
    db = get_database()
    quizzes = await db.quizzes.find(
        {"created_by": current_user.user_id}, 
        {
            "_id": 0,  # Exclude _id
            "quiz_id": 1,
            "quiz_title": 1,
            "difficulty": 1,
            "category": 1,
            "quiz_source": 1,
            "created_at": 1
        }
    ).to_list(length=None)

    return {"quizzes": quizzes}


@router.get("/attempt/{quiz_id}", status_code=200)
async def get_quiz_for_attempt(quiz_id: str, current_user: User = Depends(get_current_user)):
    db = get_database()
    pipeline = [
        {"$match": {"quiz_id": quiz_id}},
        {"$project": {
            "_id": 0,
            "questions.correctChoicesId": 0,
            "questions.answerExplanation": 0,
            "questions.choices.choiceExplanation": 0
        }}
    ]
    result = await db.quizzes.aggregate(pipeline).to_list(length=1)
    if not result:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return result[0]
