from enum import StrEnum

from faststream import FastStream
from faststream.kafka import KafkaBroker
from pydantic import BaseModel

from src.settings import settings
from src.client import GroqClient


class TopicsEnum(StrEnum):
    GPT_BOT_RESULT = "gpt_bot_result"
    GPT_BOT_REQUEST = "gpt_bot_request"


class GptResponse(BaseModel):
    chat_id: int
    text: str


class GptRequest(BaseModel):
    chat_id: int
    text: str


broker = KafkaBroker(f"{settings.kafka_host}:{settings.kafka_port}")
app = FastStream(broker)


@broker.subscriber(TopicsEnum.GPT_BOT_REQUEST)  # type: ignore
async def wait_gpt_request(gpt_request: GptRequest) -> None:
    client = GroqClient()
    response = await client.send_message_to_llama(gpt_request.text)
    await broker.connect()
    await broker.publish(
        GptResponse(chat_id=gpt_request.chat_id, text=response),
        TopicsEnum.GPT_BOT_RESULT,
    )
