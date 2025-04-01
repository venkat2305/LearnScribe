from groq import Groq
from app.config import config


def groq_client():
    return Groq(
        api_key=config.GROQ_API_KEY,
    )


def generate_quiz_from_text_groq(quiz_prompt, model, response_schema=None):
    client = groq_client()

    schema_dict = response_schema.schema() if response_schema else None

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"You must respond with JSON that matches this schema: {schema_dict}" if schema_dict else "Respond with JSON"
            },
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
    choice = chat_completion.choices[0]
    message = choice.message

    return {
        "text": message.content,
        "model": model,
        "input_tokens": getattr(message, "input_tokens", 0),
        "output_tokens": getattr(message, "output_tokens", 0),
    }
