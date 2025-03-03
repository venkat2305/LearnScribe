from app.services.youtube import get_video_id, get_transcript
from app.services.article_extraction import get_article_transcript
from app.services.ai.gemini import generate_quiz_from_text
import time
from bson import ObjectId

GEMINI_FLASH_MODEL = "gemini-2.0-flash"
GEMINI_1_5_PRO_MODEL = "gemini-1.5-pro"


def generate_summary_prompt(prompt: str = "", transcript: str = None, length: str = "medium") -> str:
    length_instructions = {
        "short": "Create a concise summary in 2-3 paragraphs.",
        "medium": "Create a comprehensive summary in 3-5 paragraphs.",
        "long": "Create a detailed summary in 5-8 paragraphs."
    }

    length_instruction = length_instructions.get(length, length_instructions["medium"])

    if not transcript:
        return "Please provide text to summarize."

    summary_prompt = f"""
    Please summarize the following content:

    {transcript}

    {length_instruction}
    {prompt}

    The summary should:
    - Capture the key points and main ideas
    - Be well-structured with clear paragraphs
    - Be written in professional language
    - Maintain the original meaning and important details
    """

    return summary_prompt


def generate_summary_from_text(text: str, prompt: str = "", length: str = "medium") -> dict:
    summary_prompt = generate_summary_prompt(prompt, text, length)

    time1 = time.time()
    ai_response = generate_quiz_from_text(summary_prompt, GEMINI_FLASH_MODEL)
    time2 = time.time()

    return {
        "summary": ai_response.get('text', ''),
        "metadata": {
            "model": ai_response.get('model', ""),
            "service": "gemini",
            "input_tokens": ai_response.get('input_tokens', 0),
            "output_tokens": ai_response.get('output_tokens', 0),
            "time_taken": time2 - time1
        }
    }


def generate_summary_from_youtube(url: str, prompt: str = "", length: str = "medium") -> dict:
    video_id = get_video_id(url)
    if not video_id:
        return {"error": "Invalid YouTube URL."}

    transcript = get_transcript(url)
    if not transcript:
        return {"error": "Failed to extract transcript from YouTube video."}

    summary_result = generate_summary_from_text(transcript, prompt, length)

    if "error" in summary_result:
        return summary_result

    summary_result["source_id"] = video_id
    summary_result["source_type"] = "youtube"

    return summary_result


def generate_summary_from_article(url: str, prompt: str = "", length: str = "medium") -> dict:
    article_text = get_article_transcript(url)
    if not article_text:
        return {"error": "Failed to extract content from article URL."}

    summary_result = generate_summary_from_text(article_text, prompt, length)

    if "error" in summary_result:
        return summary_result

    summary_result["source_type"] = "article"
    summary_result["source_url"] = url
    return summary_result


def generate_summary(summary_data) -> dict:
    summary_source = summary_data.summarySource
    prompt = summary_data.prompt or ""
    source_url = summary_data.contentSource.url if summary_data.contentSource else ""
    text_content = summary_data.textContent if hasattr(summary_data, "textContent") else ""
    length = summary_data.length if hasattr(summary_data, "length") else "medium"

    if summary_source == "youtube":
        if not source_url:
            return {"error": "YouTube URL is required."}
        result = generate_summary_from_youtube(source_url, prompt, length)

    elif summary_source == "article":
        if not source_url:
            return {"error": "Article URL is required."}
        result = generate_summary_from_article(source_url, prompt, length)

    elif summary_source == "text":
        if not text_content:
            return {"error": "Text content is required for summarization."}
        result = generate_summary_from_text(text_content, prompt, length)
        result["source_type"] = "text"

    else:
        return {"error": "Invalid summary source provided."}

    if "error" in result:
        return result

    # Add a unique ID to the summary
    summary_id = str(ObjectId())

    return {
        "summary_id": summary_id,
        "summary": result.get("summary", ""),
        "source_type": result.get("source_type", ""),
        "source_id": result.get("source_id", ""),
        "source_url": result.get("source_url", source_url),
        "metadata": result.get("metadata", {}),
    }
