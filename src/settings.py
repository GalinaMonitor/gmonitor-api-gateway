import logging

from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.WARNING)


class Settings(BaseSettings):
    groq_token: str = "token"
    gigachat_token: str = "token"

    kafka_host: str = "localhost"
    kafka_port: int = 9092


settings = Settings()
