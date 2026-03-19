"""config.py - Equiv. appsettings.json."""
from dataclasses import dataclass

@dataclass
class Settings:
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    AI_MODEL: str = "llama3.2:1b"
    AI_BASE_URL: str = "http://localhost:11434"
    CHROMA_COLLECTION: str = "unipe_knowledge"
    FRONTEND_URL: str = "http://localhost:3000"

settings = Settings()
