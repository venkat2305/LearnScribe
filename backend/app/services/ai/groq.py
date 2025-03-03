from groq import Groq
from app.config import config


def groq_client():
    return Groq(
        api_key=config.GROQ_API_KEY,
    )


def generate_quiz_from_text_groq(quiz_prompt, model):
    client = groq_client()

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": quiz_prompt,
            }
        ],
        model=model,
        temperature=0.6,
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
        top_p=0.8,
    )

    return {
        "text": chat_completion.messages[0].content,
        "model": model,
        "input_tokens": chat_completion.messages[0].input_tokens or 0,
        "output_tokens": chat_completion.messages[0].output_tokens or 0,
    }
