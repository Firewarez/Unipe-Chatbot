"""config.py - Equiv. appsettings.json."""
from dataclasses import dataclass

@dataclass
class Settings:
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    AI_MODEL: str = "llama3.2:1b"
    AI_BASE_URL: str = "http://localhost:11434"
    CHROMA_COLLECTION: str = "unipe_knowledge"
    FRONTEND_URL: str = "http://localhost:3000"
    MESSAGING_ENABLED: bool = True
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    RABBITMQ_EXCHANGE: str = "chat.events"

settings = Settings()
