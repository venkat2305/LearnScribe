# task_configurations.py (or in your main file)
from app.models.quiz import AIQuizResponse
from app.models.summary import AISummaryResponse
# from config_components import SCHEMAS, MODEL_CONFIGS # Assumed available

SCHEMAS = {
    "quiz": AIQuizResponse,
    "summary": AISummaryResponse,
    # "flashcard": FlashcardResponse, # Example
    "raw_text": None, # Use None for tasks that don't need structured output
}

PROMPT_TEMPLATES = {
    "quiz_easy": (
        "Generate an easy quiz with {num_questions} questions on the topic derived from the following input. "
        "Ensure questions cover fundamental concepts. Format the output as JSON:\n"
        "{format_instructions}\n\nInput Text:\n{input_text}"
    ),
    "quiz_hard": (
        "Generate a challenging quiz with {num_questions} questions on the topic derived from the following input. "
        "Focus on advanced concepts, nuances, or complex applications. Format the output as JSON:\n"
        "{format_instructions}\n\nInput Text:\n{input_text}"
    ),
    "quiz_from_mistakes": (
        "Analyze the following text which contains mistakes i made in a lot of quizzes."
        "Generate a quiz with {num_questions} questions specifically designed to test understanding and correct these mistakes. "
        "Format the output as JSON:\n"
        "{format_instructions}\n\nInput Text (containing mistakes):\n{input_text}"
    ),
    
    # Summary templates
    "summary_detailed": (
        "Create a comprehensive summary of the following content:\n\n"
        "{input_text}\n\n"
        "Length: {length}\n"
        "{additional_instructions}\n\n"
        "The summary should:\n"
        "- Capture all key points and main ideas\n"
        "- Be well-structured with clear paragraphs\n"
        "- Be written in professional language\n"
        "- Maintain the original meaning and important details\n"
        "- Use markdown formatting for better readability\n\n"
        "Also include 4 thought-provoking questions with answers related to the content.\n\n"
        "{format_instructions}"
    ),
    "summarize_youtube_transcript": (
        "Create a summary of the following YouTube video transcript:\n\n"
        "{input_text}\n\n"
        "Length: {length}\n"
        "{additional_instructions}\n\n"
        "The summary should:\n"
        "- Provide a concise overview of the main topics covered\n"
        "- Extract key insights and information from the video\n"
        "- Be well-structured and easy to follow\n"
        "- Use markdown formatting for better readability\n\n"
        "Also include 4 thought-provoking questions with answers that would help reinforce learning from this video.\n\n"
        "{format_instructions}"
    ),
    "summarize_article": (
        "Create a summary of the following article:\n\n"
        "{input_text}\n\n"
        "Length: {length}\n"
        "{additional_instructions}\n\n"
        "The summary should:\n"
        "- Capture the article's key arguments, findings, and conclusions\n"
        "- Preserve the author's main points and supporting evidence\n"
        "- Be well-structured and flow logically\n"
        "- Use markdown formatting for better readability\n\n"
        "Also include 4 thought-provoking questions with answers related to the content.\n\n"
        "{format_instructions}"
    ),
}

TASK_CONFIGURATIONS = {
    "quiz_easy_general": {
        "schema_name": "quiz",
        "model_config_name": "groq_llama3_70b_fast", # Use a precise model for easy qns
        "prompt_template_name": "quiz_easy",
        "prompt_input_variables": ["input_text", "num_questions"], # Vars expected by the template (excluding format_instructions)
        "default_params": {"num_questions": 5}, # Default values for prompt vars
    },
    "quiz_medium_general": {
        "schema_name": "quiz",
        "model_config_name": "gemini_flash_2_strict", # Allow a bit more creativity/flexibility
        "prompt_template_name": "quiz_easy", # Reuse 'easy' template, difficulty comes from model/temp maybe? Or define quiz_medium template
        "prompt_input_variables": ["input_text", "num_questions"],
        "default_params": {"num_questions": 7},
    },
    "quiz_hard_general": {
        "schema_name": "quiz",
        "model_config_name": "gemini_flash_2_strict", # Use a more capable/creative model for hard qns
        "prompt_template_name": "quiz_hard",
        "prompt_input_variables": ["input_text", "num_questions"],
        "default_params": {"num_questions": 5},
    },
    "quiz_hard_fast_experimental": { # Example using a different provider
        "schema_name": "quiz",
        "model_config_name": "groq_llama3_70b_fast",
        "prompt_template_name": "quiz_hard",
        "prompt_input_variables": ["input_text", "num_questions"],
        "default_params": {"num_questions": 5},
    },
    "quiz_from_mistakes_analysis": {
        "schema_name": "quiz",
        "model_config_name": "gemini_flash_2_strict", # Need precise analysis
        "prompt_template_name": "quiz_from_mistakes",
        "prompt_input_variables": ["input_text", "num_questions"],
        "default_params": {"num_questions": 3},
    },

    # --- Summary Tasks ---
    "summary_general": {
        "schema_name": "summary",
        "model_config_name": "gemini_flash_2_strict", # Fast and cheap for summaries
        "prompt_template_name": "summary_detailed",
        "prompt_input_variables": ["input_text"],
        "default_params": {},
    },
    "summary_youtube": {
        "schema_name": "summary",
        "model_config_name": "gemini_flash_2_strict", # Example: Use fast Groq for YT summaries
        "prompt_template_name": "summarize_youtube_transcript", # Source-specific prompt
        "prompt_input_variables": ["input_text"],
        "default_params": {},
    },

    "simple_explanation": {
        "schema_name": "raw_text",  # No Pydantic parsing needed
        "model_config_name": "gemini_flash_2_strict",
        "prompt_template_name": "simple_explanation_template", # Assume this template exists in PROMPT_TEMPLATES
        "prompt_input_variables": ["input_text", "target_audience"],
        "default_params": {"target_audience": "a 5 year old"},
     },
     
    # Summary Tasks
    "summary_short": {
        "schema_name": "summary",
        "model_config_name": "gemini_flash_2_strict",
        "prompt_template_name": "summary_detailed",
        "prompt_input_variables": ["input_text", "length", "additional_instructions"],
        "default_params": {"length": "Short (2-3 paragraphs)", "additional_instructions": ""},
    },
    "summary_medium": {
        "schema_name": "summary",
        "model_config_name": "gemini_flash_2_strict",
        "prompt_template_name": "summary_detailed",
        "prompt_input_variables": ["input_text", "length", "additional_instructions"],
        "default_params": {"length": "Medium (3-5 paragraphs)", "additional_instructions": ""},
    },
    "summary_long": {
        "schema_name": "summary",
        "model_config_name": "groq_llama3_70b_fast", # More detailed summaries might benefit from llama
        "prompt_template_name": "summary_detailed",
        "prompt_input_variables": ["input_text", "length", "additional_instructions"],
        "default_params": {"length": "Long (5-8 paragraphs)", "additional_instructions": ""},
    },
    "summary_youtube_short": {
        "schema_name": "summary",
        "model_config_name": "gemini_flash_2_strict",
        "prompt_template_name": "summarize_youtube_transcript",
        "prompt_input_variables": ["input_text", "length", "additional_instructions"],
        "default_params": {"length": "Short (2-3 paragraphs)", "additional_instructions": ""},
    },
    "summary_youtube_medium": {
        "schema_name": "summary",
        "model_config_name": "gemini_flash_2_strict",
        "prompt_template_name": "summarize_youtube_transcript",
        "prompt_input_variables": ["input_text", "length", "additional_instructions"],
        "default_params": {"length": "Medium (3-5 paragraphs)", "additional_instructions": ""},
    },
    "summary_article_medium": {
        "schema_name": "summary",
        "model_config_name": "gemini_flash_2_strict",
        "prompt_template_name": "summarize_article",
        "prompt_input_variables": ["input_text", "length", "additional_instructions"],
        "default_params": {"length": "Medium (3-5 paragraphs)", "additional_instructions": ""},
    },

    # Add configurations for other tasks (flashcards, analysis, etc.)
}

# Add the 'simple_explanation_template' to PROMPT_TEMPLATES if using the above example
# PROMPT_TEMPLATES["simple_explanation_template"] = "Explain the following concept to {target_audience}:\n\n{input_text}"