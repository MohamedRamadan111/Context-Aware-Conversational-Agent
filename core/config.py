import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class Settings:
    """Manage environment settings centrally and securely."""
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    REQUEST_TIMEOUT: int = 10  

    @classmethod
    def validate(cls) -> None:
        if not cls.GROQ_API_KEY:
            logger.critical("GROQ_API_KEY is missing.")
            raise ValueError("GROQ_API_KEY must be set in .env")
        if not cls.TAVILY_API_KEY:
            logger.critical("TAVILY_API_KEY is missing.")
            raise ValueError("TAVILY_API_KEY must be set in .env")

settings = Settings()