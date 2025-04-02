import time
from bson import ObjectId
from app.services.youtube import get_video_id, get_transcript
from app.services.article_extraction import get_article_transcript
from app.services.generate_ai_response import generate_response
from app.models.common_schemas import SourceTypes


def determine_summary_task(summary_source, length):
    """Determine which task configuration to use based on source and length"""
    if summary_source == "youtube":
        if length == "short":
            return "summary_youtube_short"
        else:
            return "summary_youtube_medium"
    elif summary_source == "article":
        return "summary_article_medium"
    else:  # Default for text input
        if length == "short":
            return "summary_short"
        elif length == "long":
            return "summary_long"
        else:
            return "summary_medium"


def get_source_content(summary_source, source_url):
    """Get content to be summarized from the appropriate source"""
    if summary_source == SourceTypes.YOUTUBE:
        transcript = get_transcript(source_url)
        if not transcript:
            raise ValueError(f"Failed to get transcript for YouTube URL: {source_url}")
        return transcript, get_video_id(source_url)
    elif summary_source == SourceTypes.ARTICLE:
        content = get_article_transcript(source_url)
        if not content:
            raise ValueError(f"Failed to extract content from article URL: {source_url}")
        return content, source_url
    else:
        return "", ""


def generate_summary_from_content(source_type, content, prompt="", length="medium", source_url="", source_id=""):
    """Generate summary from content regardless of source type"""
    start_time = time.time()
    
    task_name = determine_summary_task(source_type, length)
    additional_instructions = prompt if prompt else ""
    
    try:
        summary_response = generate_response(
            task=task_name,
            input_text=content,
            additional_instructions=additional_instructions
        )
        
        end_time = time.time()
        
        # Create metadata
        metadata = {
            "time_taken": round(end_time - start_time, 2),
            "task_used": task_name,
        }
        
        # Add source-specific metadata
        if source_type == SourceTypes.YOUTUBE:
            metadata.update({
                "video_id": source_id,
                "transcript_length": len(content)
            })
        elif source_type == SourceTypes.ARTICLE:
            metadata.update({
                "article_url": source_url,
                "article_length": len(content)
            })
        
        # Set source type
        if isinstance(summary_response, dict):
            summary_response.source_type = source_type
        else:
            summary_response.source_type = source_type
            
        result = {
            "summary_response": summary_response,
            "source_type": source_type,
            "metadata": metadata
        }
        
        # Add source identifiers based on source type
        if source_type == SourceTypes.YOUTUBE:
            result["source_id"] = source_id
        elif source_type == SourceTypes.ARTICLE:
            result["source_url"] = source_url
            
        return result
        
    except Exception as e:
        return {"error": f"Failed to generate summary: {str(e)}"}


def generate_summary(summary_data):
    summary_source = summary_data.summarySource
    prompt = summary_data.prompt or ""
    source_url = summary_data.contentSource.url if summary_data.contentSource else ""
    text_content = summary_data.textContent if hasattr(summary_data, "textContent") else ""
    length = summary_data.length if hasattr(summary_data, "length") else "medium"

    try:
        if summary_source in [SourceTypes.YOUTUBE, SourceTypes.ARTICLE]:
            if not source_url:
                return {"error": f"{summary_source.capitalize()} URL is required."}
            
            content, source_id = get_source_content(summary_source, source_url)
            result = generate_summary_from_content(
                source_type=summary_source,
                content=content,
                prompt=prompt,
                length=length,
                source_url=source_url,
                source_id=source_id
            )
        elif summary_source == SourceTypes.TEXT:
            if not text_content:
                return {"error": "Text content is required for summarization."}
            
            result = generate_summary_from_content(
                source_type=SourceTypes.MANUAL,
                content=text_content,
                prompt=prompt,
                length=length
            )
        else:
            return {"error": f"Invalid summary source provided: {summary_source}"}
    
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error generating summary: {str(e)}"}

    # Check for errors in result
    if "error" in result:
        return result

    # Process the LLM response
    summary_response = result.get("summary_response")

    # Create the final result document
    summary_doc = {
        "summary_id": str(ObjectId()),
        "title": getattr(summary_response, "title", "Untitled Summary"),
        "summary_text": getattr(summary_response, "summary_text", ""),
        "related_questions": getattr(summary_response, "related_questions", []),
        "source_type": result.get("source_type"),
        "source_id": result.get("source_id", ""),
        "source_url": result.get("source_url", source_url),
        "metadata": result.get("metadata", {}),
    }

    return summary_doc
