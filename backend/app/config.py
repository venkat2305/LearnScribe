from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    MONGO_URI: str

    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 600

    # AI KEYS
    GOOGLE_GEMINI_KEY: str
    GROQ_API_KEY: str

    # API KEYS
    RAPID_API_KEY: str
    SUPADATA_API_KEY: str


config = Config()
