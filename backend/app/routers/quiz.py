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
    quiz_source: QuizSourceEnum
    quiz_topic: Optional[str] = None
    difficulty: DifficultyEnum
    content_source: Optional[ContentSource] = None
    prompt: Optional[str] = None
    number_of_questions: int = 5  # renamed

    @root_validator(pre=True)
    def check_content_source(cls, values):
        quiz_source = values.get("quiz_source")  # renamed
        content_source = values.get("content_source")  # renamed
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
            "quiz_title": "Untitled Quiz",
            "questions": ai_quiz,
            "category": ""
        }
    quiz_doc = {
        "quiz_id": ai_quiz.get("quiz_id", str(ObjectId())),
        "quiz_title": ai_quiz.get("quiz_title", "Untitled Quiz"),
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


@router.get("/myquizzes")
async def get_all_quizzes(current_user: User = Depends(get_current_user)):
    db = get_database()
    user_id = current_user.user_id

    pipeline = [
        {
            '$match': {
                'created_by': user_id
            }
        }, {
            '$lookup': {
                'from': 'quiz_attempts', 
                'localField': 'quiz_id', 
                'foreignField': 'quiz_id', 
                'as': 'attempts'
            }
        }, {
            '$set': {
                'attempt_count': {
                    '$size': '$attempts'
                }, 
                'questions_count': {
                    '$size': '$questions'
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'quiz_id': 1, 
                'quiz_title': 1, 
                'difficulty': 1, 
                'category': 1, 
                'quiz_source': 1, 
                'source_id': 1, 
                'created_by': 1, 
                'created_at': 1, 
                'attempt_count': 1, 
                'questions_count': 1
            }
        }
    ]

    quizzes = await db.quizzes.aggregate(pipeline).to_list(length=None)

    return {"quizzes": quizzes}


@router.get("/{quiz_id}", status_code=200)
async def get_quiz_for_attempt(quiz_id: str, current_user: User = Depends(get_current_user)):
    db = get_database()
    pipeline = [
        {"$match": {"quiz_id": quiz_id}},
        {"$project": {
            "_id": 0,
            "questions.correct_choice_id": 0,        # renamed
            "questions.answer_explanation": 0,         # renamed
            "questions.choices.choice_explanation": 0, # renamed
            "metadata": 0
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


def process_quiz_responses(quiz, responses):
    """Helper function to process quiz responses and generate results"""
    question_map = {q["question_id"]: q for q in quiz.get("questions", [])}  # renamed key
    total_questions = len(quiz.get("questions", []))
    questions_result = []
    correct_count = 0
    wrong_question_ids = []

    for response in responses:
        question_id = response.get("question_id")
        selected_choice_id = response.get("selected_choice_id")
        question = question_map.get(question_id)
        
        if not question or not selected_choice_id:
            continue

        correct_choice_id = question.get("correct_choice_id")  # renamed key
        is_correct = selected_choice_id == correct_choice_id
        
        if is_correct:
            correct_count += 1
        else:
            wrong_question_ids.append(question_id)

        questions_result.append({
            "question_id": question_id,
            "question_text": question.get("question_text", ""),  # renamed key
            "selected_choice_id": selected_choice_id,
            "correct_choice_id": correct_choice_id,
            "answer_explanation": question.get("answer_explanation", ""),  # renamed key
            "choices": [
                {
                    "choice_id": choice.get("choice_id"),      # renamed
                    "choice_text": choice.get("choice_text", ""), # renamed
                    "choice_explanation": choice.get("choice_explanation", "")  # renamed
                }
                for choice in question.get("choices", [])
            ]
        })

    wrong_count = total_questions - correct_count
    return {
        "questions_result": questions_result,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "wrong_question_ids": wrong_question_ids,
        "total_questions": total_questions,
        "marks_obtained": correct_count,
        "total_marks": total_questions
    }


@router.post("/attempt")
async def create_quiz_attempt(
    data: QuizAttemptCreate, 
    current_user: User = Depends(get_current_user)
):
    db = get_database()
    
    quiz = await db.quizzes.find_one({"quiz_id": data.quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    responses = [r.dict() for r in data.responses]
    processed = process_quiz_responses(quiz, responses)
    # Build question map for lookup
    question_map = {q["question_id"]: q for q in quiz.get("questions", [])}  # renamed key

    attempt_id = str(ObjectId())
    attempt_doc = {
        "user_id": current_user.user_id,  # renamed key
        "quiz_id": data.quiz_id,
        "attempt_id": attempt_id,
        "responses": [
            {
                "question_id": r["question_id"],
                "selected_choice_id": r["selected_choice_id"],
                "is_correct": (question_map[r["question_id"]]["correct_choice_id"] == r["selected_choice_id"])  # renamed
            }
            for r in responses if r["question_id"] in question_map
        ],
        "stats": {
            "correct_count": processed["correct_count"],
            "wrong_count": processed["wrong_count"],
            "wrong_question_ids": processed["wrong_question_ids"]
        },
        "marks_obtained": processed["marks_obtained"],
        "total_marks": processed["total_marks"],
        "attempted_at": datetime.utcnow()
    }

    result = await db.quiz_attempts.insert_one(attempt_doc)
    return {
        "quiz_id": data.quiz_id,
        "attempt_id": attempt_id,
        "attempted_at": attempt_doc["attempted_at"],
    }


@router.get("/attempts/{attempt_id}")
async def get_quiz_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_user)
):
    db = get_database()

    attempt = await db.quiz_attempts.find_one(
        {"attempt_id": attempt_id, "user_id": current_user.user_id}  # renamed key
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    quiz = await db.quizzes.find_one({"quiz_id": attempt["quiz_id"]})  # renamed key
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    processed = process_quiz_responses(quiz, attempt["responses"])

    return {
        "attempt_id": attempt_id,
        "quiz_id": attempt["quiz_id"],
        "attempted_at": attempt["attempted_at"],
        "stats": {
            "correct_count": processed["correct_count"],
            "wrong_count": processed["wrong_count"],
            "wrong_question_ids": processed["wrong_question_ids"],
            "marks_obtained": processed["marks_obtained"],
            "total_marks": processed["total_marks"]
        },
        "questions": processed["questions_result"]
    }


@router.get("/{quiz_id}/attempts", status_code=200)
async def get_quiz_attempts(quiz_id: str, current_user: User = Depends(get_current_user)):
    db = get_database()
    attempts = await db.quiz_attempts.find(
        {"quiz_id": quiz_id, "user_id": current_user.user_id},  # renamed keys
        {
            "_id": 0,
            "marks_obtained": 1,
            "total_marks": 1,
            "stats": 1,
            "attempted_at": 1,
            "attempt_id": 1
        }
    ).to_list(length=None)

    return {"attempts": attempts}
