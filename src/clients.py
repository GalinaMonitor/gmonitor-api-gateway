import logging
import re
from typing import Generator

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole, Image
from gmonitor_lib.clients import BaseHttpxClient, HttpMethod
from httpx import Response, Auth, Request

from settings import settings

logger = logging.getLogger(__name__)


class TokenAuth(Auth):
    def __init__(self, token: str):
        self.token = f"Bearer {token}"

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.headers["Authorization"] = self.token
        yield request


class GroqClient(BaseHttpxClient):  # type: ignore
    def __init__(
        self,
        verify: bool = True,
    ):
        super().__init__(verify)
        self._base_url = "https://api.groq.com"
        self._auth = TokenAuth(settings.groq_token)

    async def send_message_to_llama(self, message: str) -> str:
        response = await self._send_request(
            path="/openai/v1/chat/completions",
            method=HttpMethod.POST,
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ],
            },
        )
        return str(response["choices"][0]["message"]["content"])


class GigaChatClient(BaseHttpxClient):  # type: ignore
    def __init__(
        self,
        verify: bool = True,
    ):
        super().__init__(verify)
        self._base_url = "https://gigachat.devices.sberbank.ru"
        self.gigachat = GigaChat(
            credentials=settings.gigachat_token,
            verify_ssl_certs=False,
        )

    def _parse_image_uuid(self, input_string: str) -> str | None:
        uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        match = re.search(uuid_pattern, input_string)
        if match:
            return match.group()
        else:
            return None

    def _prepare_message(self, message: str) -> str:
        return f"{message} в формате jpg"

    def send_message_to_gigachat(self, message: str) -> str | None:
        payload = Chat(
            messages=[
                Messages(role=MessagesRole.SYSTEM, content="Ты — Василий Кандинский"),
                Messages(role=MessagesRole.USER, content=self._prepare_message(message)),
            ],
            function_call="auto",
        )
        response = self.gigachat.chat(payload)
        return self._parse_image_uuid(response.choices[0].message.content)

    async def download_image(self, image_guid: str) -> Image:
        return self.gigachat.get_image(image_guid)
