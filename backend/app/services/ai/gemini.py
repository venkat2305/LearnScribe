from google import genai
from google.genai import types
from app.config import config
import os

GOOGLE_GEMINI_KEY = config.GOOGLE_GEMINI_KEY


def get_gemini_client():
    return genai.Client(
        api_key=GOOGLE_GEMINI_KEY,
    )


def audio_to_json_gemini(audio_file, prompt, model, question_count):
    client = get_gemini_client()

    # Validate that the audio file exists and is readable
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found at path: {audio_file}")
        return None

    file_size = os.path.getsize(audio_file)
    if file_size == 0:
        print(f"Error: Audio file is empty: {audio_file}")
        return None

    print(f"Processing audio file: {audio_file} (Size: {file_size} bytes)")

    files = [
        client.files.upload(file=audio_file),
    ]

    # use question_count in the chat prompt
    parts_prompt = f"create a quiz, {question_count} questions" 
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(
                    file_uri=files[0].uri,
                    mime_type=files[0].mime_type,
                ),
                types.Part.from_text(
                    text=parts_prompt
                ),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=0.6,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
    )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    return response.text


def generate_quiz_from_topic(quiz_topic: str = "", prompt: str = "", difficulty=None, question_count: int = 5, transcript: str = None):
    client = get_gemini_client()
    model = "gemini-1.5-pro"

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
              "correctChoicesId": 0,
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
    - Specify the correctChoicesId as the index of the correct answer (0, 1, 2, or 3)
    - Provide a detailed answerExplanation for each question

    The output should be ONLY the JSON object with no additional text.
    """

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=quiz_prompt)]
        )
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.44,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
    )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    return response.text
