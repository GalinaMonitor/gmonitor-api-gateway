from faststream import FastStream
from faststream.kafka import KafkaBroker

from settings import settings
from gmonitor_lib.schemas import TopicsEnum, GptDto

broker = KafkaBroker(f"{settings.kafka_host}:{settings.kafka_port}")
app = FastStream(broker)


@broker.subscriber(TopicsEnum.GPT_BOT_REQUEST)  # type: ignore
async def wait_gpt_request(gpt_request: GptDto) -> None:
    from service import GptService

    service = GptService()
    await service.process_request(gpt_request)
