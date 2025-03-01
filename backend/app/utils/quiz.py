from app.services.youtube import get_video_id, download_youtube_audio
from app.services.ai.gemini import generate_quiz_from_topic, audio_to_json_gemini
from app.services.article_extraction import get_article_transcript
import json
import os

MODEL = "gemini-2.0-flash"


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
        transcript = get_article_transcript(source_url)
        ai_response_text = generate_quiz_from_topic(quiz_topic, prompt, question_count=question_count, transcript=transcript)
        source_id = ""

    elif quiz_source == "manual":
        if not quiz_topic:
            return {"error": "Quiz topic mandatory for manual quiz."}
        ai_response_text = generate_quiz_from_topic(quiz_topic, prompt, difficulty, question_count=question_count)
        source_id = ""
    else:
        return {"error": "Invalid quiz source provided."}

    try:
        quiz = json.loads(ai_response_text)
    except Exception:
        return {"error": "AI generation failed."}

    return {
        "quiz": quiz,
        "quiz_source": quiz_source,
        "source_id": source_id
    }
