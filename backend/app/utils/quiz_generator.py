# app/services/quiz_generator.py (or similar file)

import time
import json
import os
from typing import Dict, Any
from bson import ObjectId
from fastapi import HTTPException

from app.models.quiz import QuizCreate, AIQuizResponse
from app.models.ai_models import SourceTypes
from app.services.youtube import get_video_id, get_transcript
from app.services.article_extraction import get_article_transcript
from app.services.generate_ai_response import generate_response
from app.services.mistakes_transcript import get_mistake_context_transcript


def add_ids_to_quiz(quiz: dict) -> dict:
    """
    Add unique IDs to quiz, questions, and choices using ObjectId
    Updates the quiz object in place and returns it
    """
    quiz_id = str(ObjectId())
    quiz["quiz_id"] = quiz_id

    # Update questions and choices
    for q_idx, question in enumerate(quiz["questions"]):
        question_id = f"{quiz_id}-{q_idx+1}"
        question["question_id"] = question_id

        # Store old correct choice ID before updating choice IDs
        old_correct_id = question["correct_choice_id"]

        # Update choice IDs and track the correct one
        for c_idx, choice in enumerate(question["choices"]):
            choice_id = f"{question_id}-{c_idx+1}"
            # Update correct_choice_id if this was the correct choice
            if choice.get("choice_id") == old_correct_id:
                question["correct_choice_id"] = choice_id
            # update choice id for each choice.
            choice["choice_id"] = choice_id

    return quiz


def get_source_content(quiz_source, source_url):
    if quiz_source == SourceTypes.YOUTUBE:
        transcript = get_transcript(source_url)
        if not transcript:
            raise ValueError(f"Failed to get transcript for YouTube URL: {source_url}")
        return transcript, get_video_id(source_url)
    elif quiz_source == SourceTypes.ARTICLE:
        content = get_article_transcript(source_url)
        if not content:
            raise ValueError(f"Failed to extract content from article URL: {source_url}")
        return content, source_url
    else:
        return "", ""

# --- REMOVE OLD HELPER FUNCTIONS ---
# generate_quiz_prompt
# generate_with_gemini
# generate_with_groq
# SERVICE_ROUTER
# clean_ai_response
# generate_quiz_from_audio (unless you plan to re-implement audio input separately)
# ---

def determine_task_name(quiz_data: QuizCreate, is_mistake_quiz: bool) -> str:
    if is_mistake_quiz:
        return "quiz_from_mistakes_analysis"

    difficulty = quiz_data.difficulty or "medium"

    if difficulty == "easy":
        return "quiz_easy_general"
    elif difficulty == "medium":
        return "quiz_medium_general"
    elif difficulty == "hard":
        return "quiz_hard_general"
    else:
        print(f"Warning: Unknown difficulty '{quiz_data.difficulty}'. Defaulting to medium task.")
        return "quiz_medium_general"


async def generate_quiz_2(quiz_data: QuizCreate, user_id) -> dict:
    start_time = time.time()
    quiz_source = quiz_data.quiz_source
    source_url = quiz_data.content_source.url if hasattr(quiz_data, "content_source") and quiz_data.content_source else ""
    is_mistake_quiz = quiz_source == SourceTypes.MISTAKES
    print("quiz_source", quiz_source)

    # 1. Determine Task Name
    try:
        task_name = determine_task_name(quiz_data, is_mistake_quiz)
    except Exception as e:
        return {"error": f"Failed to determine task configuration: {e}"}

    # 2. Prepare Input Text and Source ID
    input_text = ""
    source_id = ""
    try:
        if quiz_source in [SourceTypes.YOUTUBE, SourceTypes.ARTICLE]:
            content, source_id = get_source_content(quiz_source, source_url)
            input_text = content
            if quiz_data.prompt:
                input_text += f"\n\nAdditional Instructions:\n{quiz_data.prompt}"

        elif quiz_source == SourceTypes.MANUAL:
            if not quiz_data.quiz_topic:
                return {"error": "Quiz topic is mandatory for manual quiz."}
            input_text = f"Topic: {quiz_data.quiz_topic}"
            if quiz_data.prompt:
                input_text += f"\n\nSpecific Instructions:\n{quiz_data.prompt}"

        elif quiz_source == SourceTypes.MISTAKES:
            print("mistakes in source types. ")
            if not user_id:
                return {"error": "User ID is mandatory for mistakes quiz."}
            input_text = await get_mistake_context_transcript(user_id)
            print("input text")
        else:
            return {"error": f"Unsupported quiz source: {quiz_source}"}

    except ValueError as e:  # Catch errors from get_source_content
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error preparing quiz input: {e}"}
    print("in quiz generator")
    # 3. Call Langchain Generator
    try:
        # Prepare kwargs for generate_response based on the task's needs
        # Common kwargs are 'input_text' and 'num_questions' based on your config
        kwargs_for_llm = {
            "input_text": input_text,
            "num_questions": quiz_data.number_of_questions
            # Add other kwargs here if your tasks/prompts require them
        }
        # Filter out None values, though generate_response might handle them
        kwargs_for_llm = {k: v for k, v in kwargs_for_llm.items() if v is not None}

        ai_quiz_response_obj = generate_response(task=task_name, **kwargs_for_llm)

        # Check if the response is the expected Pydantic object
        if not isinstance(ai_quiz_response_obj, AIQuizResponse):
            # If it failed parsing and returned raw content (or None)
            print(f"Warning: generate_response did not return an AIQuizResponse object. Type: {type(ai_quiz_response_obj)}")
            # Try to log the raw response if possible and not too large
            raw_content_preview = str(ai_quiz_response_obj)[:500] if ai_quiz_response_obj else "None"
            return {"error": f"AI generation failed to produce valid structured data. Received: {raw_content_preview}..."}

        # Convert Pydantic object to dictionary
        quiz_dict = ai_quiz_response_obj.model_dump()  # Use .dict() for Pydantic v1

        # Add unique IDs
        quiz_dict_with_ids = add_ids_to_quiz(quiz_dict)

    except ValueError as e: # Catch ValueErrors from generate_response (e.g., unknown task, missing vars)
        print(f"Configuration or input error during LLM call: {e}")
        return {"error": f"Quiz generation configuration error: {e}"}
    except ImportError as e: # Catch missing dependency errors
        print(f"Import error during LLM call: {e}")
        return {"error": f"Missing required library for AI generation: {e}"}
    except Exception as e:
        print(f"Error during AI quiz generation or processing: {e}")
        # Log the full exception traceback here in real application
        return {"error": f"AI generation failed: {str(e)}"}

    # 4. Prepare Metadata (Simplified)
    end_time = time.time()
    # Get model info from the task config if possible (requires access or passing it back)
    # For now, just log the task name used.
    metadata = {
        "task_used": task_name,
        # "model_config_name": TASK_CONFIGURATIONS[task_name]["model_config_name"], # Requires access to TASK_CONFIGURATIONS
        "time_taken": round(end_time - start_time, 2),
        # Add other relevant info if available
    }

    # 5. Return Result
    return {
        "quiz": quiz_dict_with_ids,
        "quiz_source": quiz_source,
        "source_id": source_id,
        "metadata": metadata,
    }
