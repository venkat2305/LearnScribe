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

    return {
        "input_tokens": response.usage_metadata.prompt_token_count,
        "output_tokens": response.usage_metadata.candidates_token_count,
        "text": response.text,
        "model": model,
    }


def generate_quiz_from_text(quiz_prompt, model):
    client = get_gemini_client()

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

    return {
        "input_tokens": response.usage_metadata.prompt_token_count,
        "output_tokens": response.usage_metadata.candidates_token_count,
        "text": response.text,
        "model": model,
    }
