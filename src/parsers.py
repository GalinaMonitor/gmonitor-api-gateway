from abc import ABC, abstractmethod
from io import BytesIO

from gmonitor_lib.clients import AWSClient

from gmonitor_lib.schemas import GptResponse, GptRequest, GptResponseType
from src.clients import GigaChatClient, GroqClient


class BaseParser(ABC):
    @abstractmethod
    async def process_request(self, request: GptRequest) -> GptResponse: ...


class ImageParser(BaseParser):
    def __init__(self) -> None:
        self.s3_client = AWSClient()
        self.gigachat_client = GigaChatClient()

    async def process_request(self, request: GptRequest) -> GptResponse:
        image_uuid = self.gigachat_client.send_message_to_gigachat(request.text)
        if image_uuid:
            image_file = await self.gigachat_client.download_image(image_uuid)
            image_filename = f"{image_uuid}.jpg"
            s3_link = self.s3_client.upload_file(
                BytesIO(image_file.content.encode()), image_filename
            )
            return GptResponse(
                text=s3_link, chat_id=request.chat_id, type=GptResponseType.IMAGE
            )
        return GptResponse(
            text="Картинка не сгенерилась",
            chat_id=request.chat_id,
            type=GptResponseType.TEXT,
        )


class TextParser(BaseParser):
    def __init__(self) -> None:
        self.groq_client = GroqClient()

    async def process_request(self, request: GptRequest) -> GptResponse:
        response = await self.groq_client.send_message_to_llama(request.text)
        return GptResponse(
            text=response, chat_id=request.chat_id, type=GptResponseType.TEXT
        )
