from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.db.mongodb import get_database
from app.utils.auth import get_current_user, User

router = APIRouter()


class AttemptChoice(BaseModel):
    question_id: str
    selected_choice_id: str


class QuizAttemptCreate(BaseModel):
    quiz_id: str
    responses: List[AttemptChoice]


@router.post("/", summary="Attempt a quiz and get results")
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
