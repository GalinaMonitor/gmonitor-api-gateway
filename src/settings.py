import logging

from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.WARNING)


class Settings(BaseSettings):
    groq_token: str = "token"
    gigachat_token: str = "token"

    kafka_host: str = "localhost"
    kafka_port: int = 9092

    aws_host: str = "host"
    aws_bucket_name: str = "bucket"
    aws_access_key_id: str = "access_key_id"
    aws_secret_access_key: str = "secret_access_key"


settings = Settings()
