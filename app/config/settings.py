from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")

    ALLOWED_MODEL_NAMES = ["openai/gpt-oss-120b", "llama-3.1-8b-instant"]


settings = Settings()
