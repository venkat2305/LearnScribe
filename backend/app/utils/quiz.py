from app.services.youtube import get_video_id, download_youtube_audio, get_transcript
from app.services.ai.gemini import generate_quiz_from_text, audio_to_json_gemini
from app.services.ai.groq import generate_quiz_from_text_groq
from app.services.article_extraction import get_article_transcript
from app.models.ai_models import Services, SourceTypes, SOURCE_TO_MODEL_MAPPING
import json
import os
from bson import ObjectId
import time

# Service-specific generation functions
def generate_with_gemini(prompt, model_id):
    response = generate_quiz_from_text(prompt, model_id)
    return {
        "text": response.get('text', ''),
        "metadata": {
            "model": response.get('model', ""),
            "service": Services.GEMINI,
            "input_tokens": response.get('input_tokens', 0),
            "output_tokens": response.get('output_tokens', 0),
        }
    }

def generate_with_groq(prompt, model_id):
    response = generate_quiz_from_text_groq(prompt, model_id)
    return {
        "text": response.get('text', ''),
        "metadata": {
            "model": response.get('model', ""),
            "service": Services.GROQ,
            "input_tokens": response.get('input_tokens', 0),
            "output_tokens": response.get('output_tokens', 0),
        }
    }


SERVICE_ROUTER = {
    Services.GEMINI: generate_with_gemini,
    Services.GROQ: generate_with_groq,
}


def generate_quiz_prompt(quiz_topic: str = "", prompt: str = "", difficulty=None, question_count: int = 5, transcript: str = None) -> str:
    json_structure = """
        {
        "quiz_title": "",
        "difficulty": "",
        "category": "",
        "questions": [
            {
                "question_id": "",
                "question_text": "",
                "choices": [
                    {
                        "choice_id": 0,
                        "choice_text": "",
                        "choice_explanation": ""
                    }
                ],
                "correct_choice_id": 0,
                "answer_explanation": ""
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
    quiz should be a JSON object
    """

    return quiz_prompt


def add_ids_to_quiz(quiz: dict) -> dict:
    """
    Add unique IDs to quiz, questions, and choices using ObjectId
    Updates the quiz object in place and returns it
    """
    # Add quiz ID
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


def clean_ai_response(text: str) -> str:
    # Remove markdown code fences if present
    if text.strip().startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2 and lines[0].strip().startswith("```") and lines[-1].strip().startswith("```"):
            text = "\n".join(lines[1:-1])
    return text


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


def get_source_content(quiz_source, source_url):
    """Get content based on source type"""
    if quiz_source == SourceTypes.YOUTUBE:
        return get_transcript(source_url), get_video_id(source_url)
    elif quiz_source == SourceTypes.ARTICLE:
        return get_article_transcript(source_url), ""
    else:
        return "", ""


def generate_quiz(quiz_data) -> dict:
    # Extract data
    quiz_source = quiz_data.quiz_source
    quiz_topic = quiz_data.quiz_topic or ""
    prompt = quiz_data.prompt or ""
    question_count = quiz_data.number_of_questions
    difficulty = quiz_data.difficulty
    source_url = quiz_data.content_source.url if hasattr(quiz_data, "content_source") and quiz_data.content_source else ""
    
    time1 = time.time()
    
    # Validate inputs
    if quiz_source in [SourceTypes.YOUTUBE, SourceTypes.ARTICLE] and not source_url:
        return {"error": f"{quiz_source.capitalize()} URL is required."}
    
    if quiz_source == SourceTypes.MANUAL and not quiz_topic:
        return {"error": "Quiz topic mandatory for manual quiz."}
    
    # Get source content and ID
    content, source_id = get_source_content(quiz_source, source_url)
    
    # Get the service-model pair for this source type
    model_pair = SOURCE_TO_MODEL_MAPPING.get(quiz_source, SOURCE_TO_MODEL_MAPPING["default"])
    service_name = model_pair.service
    model_id = model_pair.model_id
    
    # Generate quiz prompt
    quiz_prompt = generate_quiz_prompt(
        quiz_topic, 
        prompt, 
        difficulty, 
        question_count,
        content if quiz_source != SourceTypes.MANUAL else ""
    )
    
    # Route to appropriate service
    generator_func = SERVICE_ROUTER.get(service_name)
    if not generator_func:
        return {"error": f"Unsupported service: {service_name}"}
    
    ai_response = generator_func(quiz_prompt, model_id)
    ai_response_text = ai_response["text"]
    metadata = ai_response["metadata"]
    
    # Process response
    try:
        cleaned_text = clean_ai_response(ai_response_text)
        quiz = json.loads(cleaned_text)
        quiz = add_ids_to_quiz(quiz)
    except Exception as e:
        return {"error": f"AI generation failed: {str(e)}"}
    
    time2 = time.time()
    metadata["time_taken"] = time2 - time1
    metadata["model_id"] = model_id
    metadata["service"] = service_name
    metadata["model_description"] = model_pair.description
    
    return {
        "quiz": quiz,
        "quiz_source": quiz_source,
        "source_id": source_id,
        "metadata": metadata,
    }
