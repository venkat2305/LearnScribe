class ServiceModelPair:
    def __init__(self, service, model_id, description=""):
        self.service = service
        self.model_id = model_id
        self.description = description

# Available service providers
class Services:
    GEMINI = "gemini"
    GROQ = "groq"

# Define all available service-model pairs
class ModelPairs:
    # Gemini models
    GEMINI_FLASH = ServiceModelPair(Services.GEMINI, "gemini-2.0-flash", "Fast Gemini model")
    GEMINI_PRO = ServiceModelPair(Services.GEMINI, "gemini-1.5-pro", "Balanced Gemini model")
    GEMINI_PRO_VISION = ServiceModelPair(Services.GEMINI, "gemini-2.0-pro-vision", "Powerful Gemini model with vision")

    # Groq models
    GROQ_LLAMA_3_1_FAST = ServiceModelPair(Services.GROQ, "llama-3.1-8b-instant", "Fast Llama 3.1 model")
    GROQ_LLAMA_3_2_PREVIEW = ServiceModelPair(Services.GROQ, "llama-3.2-1b-preview", "Preview Llama 3.2 model")
    GROQ_LLAMA_3_3 = ServiceModelPair(Services.GROQ, "llama-3.3-70b-versatile", "Powerful Llama 3.3 model")
    GROQ_LLAMA_3_3_SPEC = ServiceModelPair(Services.GROQ, "llama-3.3-70b-specdec", "Specialized Llama 3.3 model")

# Source types
class SourceTypes:
    YOUTUBE = "youtube"
    ARTICLE = "article"
    MANUAL = "manual"

# Map source types directly to service-model pairs
SOURCE_TO_MODEL_MAPPING = {
    SourceTypes.YOUTUBE: ModelPairs.GEMINI_FLASH,  # YouTube uses Gemini Flash
    SourceTypes.ARTICLE: ModelPairs.GEMINI_PRO,    # Article uses Gemini Pro
    SourceTypes.MANUAL: ModelPairs.GROQ_LLAMA_3_3_SPEC,  # Manual uses Groq Llama
    # Fallback configuration
    "default": ModelPairs.GEMINI_FLASH
}
