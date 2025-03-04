from app.services.youtube import get_video_id, download_youtube_audio, get_transcript
from app.services.ai.gemini import generate_quiz_from_text, audio_to_json_gemini
from app.services.ai.groq import generate_quiz_from_text_groq
from app.services.article_extraction import get_article_transcript
import json
import os
from bson import ObjectId
import time


GEMINI_FLASH_MODEL = "gemini-2.0-flash"
GEMINI_1_5_PRO_MODEL = "gemini-1.5-pro"
LLAMA_3_3 = "llama-3.3-70b-versatile"
GROQ_LLAMA_3_1_8B = "llama-3.1-8b-instant"


def generate_quiz_prompt(quiz_topic: str = "", prompt: str = "", difficulty=None, question_count: int = 5, transcript: str = None) -> str:
    json_structure = """
        {
        "quizTitle": "",
        "difficulty": "",
        "category": "",
        "questions": [
            {
                "questionId": "",
                "questionText": "",
                "choices": [
                    {
                    "choiceId": 0,
                    "choiceText": "",
                    "choiceExplanation": ""
                    }
                ],
                "correctChoiceId": 0,
                "answerExplanation": ""
                }
        ]
        }
    """

    if transcript:
        main_text = f"transcript: {transcript}"
    elif quiz_topic:
        main_text = f"topic: {quiz_topic}"
    else:
        main_text = ""
    difficulty_text = f"difficulty level: {difficulty}" if difficulty else ""

    quiz_prompt = f"""
    Generate a quiz in English as a valid JSON object with exactly the following structure:
    {json_structure}

    For the quiz:
    - {main_text}
    - {difficulty_text}
    - {prompt}
    - Add an appropriate quizTitle based on the provided information
    - Include the specified difficulty
    - Add a relevant category
    - Create {question_count} questions with unique questionId values
    - Each question should have 4 choices with choiceId
    - For each choice, provide an explanation of why it's correct or incorrect in choiceExplanation
    - Specify the correctChoiceId as the index of the correct answer (0, 1, 2, or 3)
    - Provide a detailed answerExplanation for each question.
    - All text content must be in English.

    The output should be ONLY the JSON object with no additional text.
    """

    return quiz_prompt


def add_ids_to_quiz(quiz: dict) -> dict:
    """
    Add unique IDs to quiz, questions, and choices using ObjectId
    Updates the quiz object in place and returns it
    """
    # Add quiz ID
    quiz["quizId"] = str(ObjectId())

    # Update questions and choices
    for q_idx, question in enumerate(quiz["questions"]):
        question_id = str(ObjectId())
        question["questionId"] = question_id

        # Store old correct choice ID before updating choice IDs
        old_correct_id = question["correctChoiceId"]

        # Update choice IDs and track the correct one
        for c_idx, choice in enumerate(question["choices"]):
            if choice.get("choiceId") == old_correct_id:
                question["correctChoiceId"] = choice_id
            choice_id = str(ObjectId())
            choice["choiceId"] = choice_id
            # Update correctChoiceId if this was the correct choice

    return quiz


def generate_quiz_from_audio(source_url, prompt, question_count):
    video_id = get_video_id(source_url)
    audio_file = download_youtube_audio(source_url)
    if not audio_file:
        return {"error": "Failed to download YouTube audio."}
    ai_response = audio_to_json_gemini(audio_file, prompt, GEMINI_FLASH_MODEL, question_count)
    ai_response_text = ai_response.get('text', '')
    metadata = {
        "model": ai_response.get('model', ""),
        "service": "gemini",
        "input_tokens": ai_response.get('input_tokens', 0),
        "output_tokens": ai_response.get('output_tokens', 0),
    }
    os.remove(audio_file)
    source_id = video_id
    return ai_response_text, metadata, source_id


def generate_quiz(quiz_data) -> dict:
    quiz_source = quiz_data.quizSource
    quiz_topic = quiz_data.quizTopic or ""
    prompt = quiz_data.prompt or ""
    question_count = quiz_data.numberOfQuestions
    source_url = quiz_data.contentSource.url if quiz_data.contentSource else ""
    difficulty = quiz_data.difficulty

    time1 = time.time()

    if hasattr(quiz_data, "contentSource") and quiz_data.contentSource:
        source_url = quiz_data.contentSource.url or ""

    if quiz_source == "youtube":
        if not source_url:
            return {"error": "YouTube URL is required."}
        # ai_response_text, metadata, source_id = generate_quiz_from_audio(source_url)
        transcript = get_transcript(source_url)
        quiz_prompt = generate_quiz_prompt(quiz_topic, prompt, difficulty,
                                           question_count, transcript)
        ai_response = generate_quiz_from_text(quiz_prompt, GEMINI_FLASH_MODEL)
        ai_response_text = ai_response.get('text', '')
        metadata = {
            "model": ai_response.get('model', ""),
            "service": "gemini",
            "input_tokens": ai_response.get('input_tokens', 0),
            "output_tokens": ai_response.get('output_tokens', 0),
        }
        source_id = get_video_id(source_url)

    elif quiz_source == "article":
        if not source_url:
            return {"error": "Article URL is required."}

        transcript = get_article_transcript(source_url)
        quiz_prompt = generate_quiz_prompt(quiz_topic, prompt, difficulty, question_count, transcript)
        ai_response = generate_quiz_from_text(quiz_prompt, GEMINI_FLASH_MODEL)

        ai_response_text = ai_response.get('text', '')
        metadata = {
            "model": ai_response.get('model', ""),
            "service": "gemini",
            "input_tokens": ai_response.get('input_tokens', 0),
            "output_tokens": ai_response.get('output_tokens', 0),
        }
        source_id = ""

    elif quiz_source == "manual":
        if not quiz_topic:
            return {"error": "Quiz topic mandatory for manual quiz."}
        quiz_prompt = generate_quiz_prompt(quiz_topic, prompt, difficulty, question_count, "")
        ai_response = generate_quiz_from_text(quiz_prompt, GEMINI_FLASH_MODEL)
        ai_response_text = ai_response.get('text', '')
        metadata = {
            "model": ai_response.get('model', ""),
            "service": "gemini",
            "input_tokens": ai_response.get('input_tokens', 0),
            "output_tokens": ai_response.get('output_tokens', 0),
        }
        source_id = ""
    else:
        return {"error": "Invalid quiz source provided."}

    try:
        quiz = json.loads(ai_response_text)
        quiz = add_ids_to_quiz(quiz)
    except Exception:
        return {"error": "AI generation failed."}

    time2 = time.time()
    metadata["time_taken"] = time2 - time1
    return {
        "quiz": quiz,
        "quiz_source": quiz_source,
        "source_id": source_id,
        "metadata": metadata,
    }
