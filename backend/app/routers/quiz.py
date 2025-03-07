from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, root_validator
from enum import Enum
from typing import Optional, List
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


# New models for quiz attempts
class AttemptChoice(BaseModel):
    question_id: str
    selected_choice_id: str


class QuizAttemptCreate(BaseModel):
    quiz_id: str
    responses: List[AttemptChoice]


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
        "metadata": result.get("metadata", {}),
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


@router.get("/{quiz_id}", status_code=200)
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


@router.delete("/{quiz_id}", status_code=200)
async def delete_quiz(quiz_id: str, current_user: User = Depends(get_current_user)):
    db = get_database()
    result = await db.quizzes.delete_one({"quiz_id": quiz_id, "created_by": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return {"message": "Quiz deleted successfully"}


@router.post("/attempt", summary="Attempt a quiz and get results")
async def create_quiz_attempt(data: QuizAttemptCreate, current_user: User = Depends(get_current_user)):
    """
    Validate user answers against quiz correctChoiceId, store attempt info, 
    and return stats (correct_count, wrong_count, etc.)
    """
    db = get_database()
    quiz = await db.quizzes.find_one({"quiz_id": data.quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    # Validate that user can attempt the quiz (for example, if only owner can do so, or all users can)
    # For now, allow any authenticated user to attempt.
    correct_count = 0
    wrong_count = 0
    wrong_question_ids = []

    # Map questionId → correctChoiceId for quick lookup
    question_map = {q["questionId"]: q["correctChoiceId"] for q in quiz["questions"]}

    for response in data.responses:
        question_id = response.question_id
        selected_choice_id = response.selected_choice_id
        correct_choice_id = question_map.get(question_id)

        if correct_choice_id == selected_choice_id:
            correct_count += 1
        else:
            wrong_count += 1
            wrong_question_ids.append(question_id)

    # Store attempt info in 'quiz_attempts' or 'quizAttempts'
    total_marks = len(quiz["questions"])
    marks_obtained = correct_count
    attempt_doc = {
        "userId": current_user.user_id,
        "quizId": data.quiz_id,
        "responses": [
            {
                "question_id": r.question_id,
                "selected_choice_id": r.selected_choice_id,
                "is_correct": (question_map.get(r.question_id) == r.selected_choice_id)
            }
            for r in data.responses
        ],
        "stats": {
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "wrong_question_ids": wrong_question_ids
        },
        "marks_obtained": marks_obtained,
        "total_marks": total_marks,
        "attempted_at": datetime.utcnow()
    }

    result = await db.quiz_attempts.insert_one(attempt_doc)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to store quiz attempt.")

    return {
        "quiz_id": data.quiz_id,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "total_questions": correct_count + wrong_count,
        "wrong_questions": wrong_question_ids,
        "marks_obtained": marks_obtained,
        "total_marks": total_marks
    }


# New endpoint to get attempt history for a quiz
@router.get("/{quiz_id}/attempts", status_code=200)
async def get_quiz_attempts(quiz_id: str, current_user: User = Depends(get_current_user)):
    """
    Get all attempts for a specific quiz by the current user
    """
    db = get_database()
    attempts = await db.quiz_attempts.find(
        {"quizId": quiz_id, "userId": current_user.user_id},
        {
            "_id": 0,
            "marks_obtained": 1,
            "total_marks": 1, 
            "stats": 1,
            "attempted_at": 1
        }
    ).to_list(length=None)
    
    return {"attempts": attempts}
