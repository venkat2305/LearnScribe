from app.services.youtube import get_video_id, download_youtube_audio
from app.services.ai.gemini import generate_quiz_from_text, audio_to_json_gemini
from app.services.article_extraction import get_article_transcript
import json
import os
import time
from bson import ObjectId


MODEL = "gemini-2.0-flash"


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
    Generate a quiz as a valid JSON object with exactly the following structure:
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
    - Provide a detailed answerExplanation for each question

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


def generate_quiz(quiz_data) -> dict:
    quiz_source = quiz_data.quizSource
    quiz_topic = quiz_data.quizTopic or ""
    prompt = quiz_data.prompt or ""
    question_count = quiz_data.numberOfQuestions
    source_url = quiz_data.contentSource.url if quiz_data.contentSource else ""
    difficulty = quiz_data.difficulty

    if hasattr(quiz_data, "contentSource") and quiz_data.contentSource:
        source_url = quiz_data.contentSource.url or ""

    if quiz_source == "youtube":
        if not source_url:
            return {"error": "YouTube URL is required."}
        video_id = get_video_id(source_url)
        audio_file = download_youtube_audio(source_url)
        if not audio_file:
            return {"error": "Failed to download YouTube audio."}
        ai_response_text = audio_to_json_gemini(audio_file, prompt, MODEL, question_count)  # pass question_count
        os.remove(audio_file)
        source_id = video_id

    elif quiz_source == "article":
        if not source_url:
            return {"error": "Article URL is required."}
        time1 = time.time()
        transcript = get_article_transcript(source_url)
        time2 = time.time()
        quiz_prompt = generate_quiz_prompt(quiz_topic, prompt, difficulty, question_count, transcript)
        ai_response_text = generate_quiz_from_text(quiz_prompt)
        time3 = time.time()
        print("Time to get transcript: ", time2 - time1)
        print("Time to generate quiz: ", time3 - time2)
        source_id = ""

    elif quiz_source == "manual":
        if not quiz_topic:
            return {"error": "Quiz topic mandatory for manual quiz."}
        quiz_prompt = generate_quiz_prompt(quiz_topic, prompt, difficulty, question_count, transcript)
        ai_response_text = generate_quiz_from_text(quiz_prompt)
        source_id = ""
    else:
        return {"error": "Invalid quiz source provided."}

    try:
        quiz = json.loads(ai_response_text)
        quiz = add_ids_to_quiz(quiz)
        print(quiz)
    except Exception:
        return {"error": "AI generation failed."}

    return {
        "quiz": quiz,
        "quiz_source": quiz_source,
        "source_id": source_id
    }
