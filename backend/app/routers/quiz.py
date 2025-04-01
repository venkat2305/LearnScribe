from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import get_database
from app.utils.auth import get_current_user, User
from app.utils.quiz import generate_quiz
from app.models.common_schemas import SourceTypes
from app.models.quiz import (
    QuizCreate,
    QuizAttemptCreate,
    Quiz,
    DifficultyEnum
)
import random

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_quiz(quiz_data: QuizCreate,
                      current_user: User = Depends(get_current_user)
                      ):
    # Special handling for mistakes-based practice quiz
    if quiz_data.quiz_source == SourceTypes.MISTAKES:
        # Get user's wrong answers using aggregation pipeline
        db = get_database()
        pipeline = [
            {
                '$match': {
                    'user_id': current_user.user_id
                }
            }, {
                '$lookup': {
                    'from': 'quizzes',
                    'let': {
                        'quizId': '$quiz_id'
                    }, 
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': ['$quiz_id', '$$quizId']
                                }
                            }
                        }
                    ], 
                    'as': 'quiz'
                }
            }, {
                '$unwind': '$quiz'
            }, {
                '$project': {
                    'responses': {
                        '$filter': {
                            'input': '$responses',
                            'as': 'response',
                            'cond': {
                                '$eq': ['$$response.is_correct', False]
                            }
                        }
                    },
                    'quiz': 1
                }
            }
        ]

        wrong_answers = await db.quiz_attempts.aggregate(pipeline).to_list(length=None)

        if not wrong_answers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No wrong answers found to create a practice quiz"
            )

        # Create context for AI from wrong answers
        mistake_contexts = []
        for attempt in wrong_answers:
            quiz = attempt['quiz']
            for response in attempt['responses']:
                question = next(
                    (q for q in quiz['questions'] if q['question_id'] == response['question_id']),
                    None
                )
                if question:
                    selected_choice = next(
                        (c for c in question['choices'] if c['choice_id'] == response['selected_choice_id']),
                        None
                    )
                    if selected_choice:
                        mistake_contexts.append({
                            'question': question['question_text'],
                            'selected_answer': selected_choice['choice_text'],
                            'correct_answer': next(
                                (c['choice_text'] for c in question['choices'] 
                                 if c['choice_id'] == question['correct_choice_id']),
                                None
                            ),
                            'explanation': question['answer_explanation']
                        })

        # Create a practice context for the prompt
        practice_context = "\n".join([
            f"Question: {m['question']}\n"
            f"User's incorrect answer: {m['selected_answer']}\n"
            f"Correct answer: {m['correct_answer']}\n"
            f"Explanation: {m['explanation']}\n"
            for m in mistake_contexts[:5]  # Limit to 5 mistakes for context
        ])

        # Set quiz topic and prompt for practice quiz
        quiz_data.quiz_topic = "Practice Quiz Based on Previous Mistakes"
        quiz_data.prompt = (
            f"Based on the following user's previous mistakes:\n\n"
            f"{practice_context}\n\n"
            f"Generate questions that:\n"
            f"1. Address similar concepts where the user made mistakes\n"
            f"2. Include variations of questions they got wrong\n"
            f"3. Focus on the specific areas of misunderstanding\n"
            f"4. Provide detailed explanations for correct and incorrect answers"
        )

    # Continue with normal quiz generation flow
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
        "quiz_title": ai_quiz.get("quiz_title", "Practice Quiz - Learning from Mistakes") if quiz_data.quiz_source == SourceTypes.MISTAKES else ai_quiz.get("quiz_title", "Untitled Quiz"),
        "difficulty": quiz_data.difficulty,
        "category": ai_quiz.get("category", "Practice") if quiz_data.quiz_source == SourceTypes.MISTAKES else ai_quiz.get("category", ""),
        "quiz_source": result.get("quiz_source"),
        "source_id": result.get("source_id"),
        "created_by": current_user.user_id,
        "created_at": datetime.utcnow(),
        "questions": ai_quiz.get("questions", []),
        "metadata": {
            **result.get("metadata", {}),
            "is_practice_quiz": quiz_data.quiz_source == SourceTypes.MISTAKES
        },
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
            "questions.correct_choice_id": 0,
            "questions.answer_explanation": 0,
            "questions.choices.choice_explanation": 0,
            "metadata": 0
        }}
    ]
    result = await db.quizzes.aggregate(pipeline).to_list(length=1)
    if not result:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    quiz = result[0]

    # Randomize choices order for each question and then randomize question order
    if "questions" in quiz:
        for question in quiz["questions"]:
            if "choices" in question and isinstance(question["choices"], list):
                random.shuffle(question["choices"])
        random.shuffle(quiz["questions"])

    return quiz


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

    await db.quiz_attempts.insert_one(attempt_doc)
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


@router.get("/practice/mistakes", status_code=status.HTTP_200_OK)
async def get_practice_quiz(current_user: User = Depends(get_current_user)):
    user_id = current_user.user_id
    db = get_database()
    print(user_id)
    # Get all quiz attempts by the user
    pipeline = [
        {
            '$match': {
                'user_id': user_id, 
                'stats.wrong_question_ids': {
                    '$ne': []
                }
            }
        }, {
            '$lookup': {
                'from': 'quizzes', 
                'let': {
                    'quizId': '$quiz_id', 
                    'wrongIds': '$stats.wrong_question_ids', 
                    'responses': '$responses'
                }, 
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$eq': [
                                    '$quiz_id', '$$quizId'
                                ]
                            }
                        }
                    }, {
                        '$project': {
                            'questions': {
                                '$filter': {
                                    'input': '$questions', 
                                    'as': 'q', 
                                    'cond': {
                                        '$in': [
                                            '$$q.question_id', '$$wrongIds'
                                        ]
                                    }
                                }
                            }
                        }
                    }
                ], 
                'as': 'quiz'
            }
        }, {
            '$unwind': '$quiz'
        }, {
            '$addFields': {
                'wrongDetails': {
                    '$map': {
                        'input': '$stats.wrong_question_ids', 
                        'as': 'qid', 
                        'in': {
                            '$let': {
                                'vars': {
                                    'question': {
                                        '$arrayElemAt': [
                                            {
                                                '$filter': {
                                                    'input': '$quiz.questions', 
                                                    'as': 'q', 
                                                    'cond': {
                                                        '$eq': [
                                                            '$$q.question_id', '$$qid'
                                                        ]
                                                    }
                                                }
                                            }, 0
                                        ]
                                    }, 
                                    'response': {
                                        '$arrayElemAt': [
                                            {
                                                '$filter': {
                                                    'input': '$responses', 
                                                    'as': 'r', 
                                                    'cond': {
                                                        '$eq': [
                                                            '$$r.question_id', '$$qid'
                                                        ]
                                                    }
                                                }
                                            }, 0
                                        ]
                                    }
                                }, 
                                'in': {
                                    'question_text': '$$question.question_text', 
                                    'selected_choice_text': {
                                        '$arrayElemAt': [
                                            {
                                                '$filter': {
                                                    'input': '$$question.choices', 
                                                    'as': 'c', 
                                                    'cond': {
                                                        '$eq': [
                                                            '$$c.choice_id', '$$response.selected_choice_id'
                                                        ]
                                                    }
                                                }
                                            }, 0
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }, {
            '$project': {
                '_id': 0, 
                'wrongDetails': 1
            }
        }
    ]

    result = await db.quiz_attempts.aggregate(pipeline).to_list(length=None)

    prompt_parts = []
    for attempt in result:
        for wrong_detail in attempt.get('wrongDetails', []):
            if wrong_detail.get('question_text') and wrong_detail.get('selected_choice_text', {}).get('choice_text'):
                prompt_parts.append(
                    f"For the question '{wrong_detail['question_text']}', "
                    f"user selected '{wrong_detail['selected_choice_text']['choice_text']}'."
                )
    qa_data = " ".join(prompt_parts)


    # print(wrong_answered_questions)
    # if not wrong_answered_questions:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="No wrong answers found to create a practice quiz"
    #     )
    
    # # Collect all wrongly answered questions
    # wrong_questions = []
    # for attempt in attempts:
    #     for question in attempt.get("questions", []):
    #         if question.get("selected_choice_id") != question.get("correct_choice_id"):
    #             # Add quiz metadata to the question
    #             quiz = await db.quizzes.find_one({"quiz_id": attempt["quiz_id"]})
    #             if quiz:
    #                 question["original_quiz_title"] = quiz.get("quiz_title")
    #                 question["original_quiz_id"] = quiz.get("quiz_id")
    #                 wrong_questions.append(question)
    
    # if not wrong_questions:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="No wrong answers found to create a practice quiz"
    #     )
    
    # # Create a new practice quiz from wrong questions
    # practice_quiz = {
    #     "quiz_id": str(ObjectId()),
    #     "quiz_title": "Practice Quiz - Learning from Mistakes",
    #     "difficulty": "practice",
    #     "category": "Practice",
    #     "quiz_source": "practice",
    #     "source_id": "",
    #     "created_by": current_user.user_id,
    #     "created_at": datetime.utcnow(),
    #     "questions": wrong_questions[:10],  # Limit to 10 questions for better practice experience
    #     "metadata": {
    #         "practice_quiz": True,
    #         "generated_from_mistakes": True
    #     }
    # }
    
    # # Save the practice quiz
    # insert_result = await db.quizzes.insert_one(practice_quiz)
    # if not insert_result.inserted_id:
    #     raise HTTPException(status_code=500, detail="Unable to create practice quiz.")
    
    # return {"message": "Practice quiz created successfully", "quiz_id": practice_quiz["quiz_id"]}
