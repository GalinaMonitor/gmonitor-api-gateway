import base64
from abc import ABC, abstractmethod
from io import BytesIO

from gmonitor_lib.clients import AWSClient

from gmonitor_lib.schemas import GptDto, GptDtoType
from clients import GigaChatClient, GroqClient


class BaseParser(ABC):
    @abstractmethod
    async def process_request(self, request: GptDto) -> GptDto: ...


class ImageParser(BaseParser):
    def __init__(self) -> None:
        self.s3_client = AWSClient()
        self.gigachat_client = GigaChatClient()

    async def process_request(self, request: GptDto) -> GptDto:
        image_uuid = self.gigachat_client.send_message_to_gigachat(request.content)
        if image_uuid:
            image_file = await self.gigachat_client.download_image(image_uuid)
            image_filename = f"{image_uuid}.jpg"
            s3_link = self.s3_client.upload_file(
                BytesIO(base64.b64decode(image_file.content)), image_filename
            )
            return GptDto(
                content=s3_link, chat_id=request.chat_id, type=GptDtoType.IMAGE
            )
        return GptDto(
            content="Картинка не сгенерилась",
            chat_id=request.chat_id,
            type=GptDtoType.TEXT,
        )


class TextParser(BaseParser):
    def __init__(self) -> None:
        self.groq_client = GroqClient()

    async def process_request(self, request: GptDto) -> GptDto:
        response = await self.groq_client.text_generation(request.content)
        return GptDto(
            content=response, chat_id=request.chat_id, type=GptDtoType.TEXT
        )


class AudioParser(BaseParser):
    def __init__(self) -> None:
        self.groq_client = GroqClient()

    async def process_request(self, request: GptDto) -> GptDto:
        transcription = await self.groq_client.speech_to_text(request.content)
        response = await self.groq_client.text_generation(transcription)
        return GptDto(
            content=response, chat_id=request.chat_id, type=GptDtoType.TEXT
        )
