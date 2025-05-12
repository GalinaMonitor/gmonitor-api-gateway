import logging

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    logging_level: int = logging.WARNING

    groq_token: str = "token"
    gigachat_token: str = "token"

    kafka_host: str = "localhost"
    kafka_port: int = 9092

    text_llm: str = "compound-beta-mini"
    transcription_llm: str = "whisper-large-v3-turbo"


settings = Settings()
logging.basicConfig(level=settings.logging_level)
