import logging
from enum import StrEnum
from json import JSONDecodeError
from typing import Any, Callable, Generator

from httpx import AsyncClient, AsyncHTTPTransport, HTTPError, Response, Auth, Request

from src.settings import settings

logger = logging.getLogger(__name__)


class HttpMethod(StrEnum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


class ExternalHttpRequestError(Exception):
    pass


def convert_httpx_response_to_json(response: Response) -> Any:
    if response.is_error:
        try:
            error_message = response.json()
        except JSONDecodeError:
            error_message = response.text
        raise ExternalHttpRequestError(error_message)
    try:
        return response.json()
    except JSONDecodeError as e:
        logger.error(f"Response body {response.content.decode('utf-8')}")
        raise ExternalHttpRequestError(response.content.decode("utf-8")) from e


class TokenAuth(Auth):
    def __init__(self, token: str):
        self.token = f"Bearer {token}"

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.headers["Authorization"] = self.token
        yield request


class BaseHttpxClient:
    def __init__(
        self,
        verify: bool = True,
    ):
        self._verify = verify
        self._base_url = ""
        self._auth: Auth | None = None

    async def _send_request(
        self,
        path: str,
        method: HttpMethod,
        json: dict[Any, Any] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int = 5,
        parser: Callable[[Response], Any] = convert_httpx_response_to_json,
        retries: int = 0,
        **kwargs: Any,
    ) -> Any:
        """
        Отправка запроса через httpx

        Args:
            url: Полный url
            method: Метод запроса
            data: Данные для post/put/patch запросов
            parser: Парсер для обработки ответа httpx
            **kwargs: Аргументы, передаваемые в httpx.request()
        """
        transport = AsyncHTTPTransport(retries=retries, verify=self._verify)
        async with AsyncClient(
            base_url=self._base_url,
            transport=transport,
            timeout=timeout,
            auth=self._auth,
        ) as client:
            try:
                response = await client.request(
                    method=method, url=path, json=json, params=params, **kwargs
                )
            except HTTPError as e:
                raise ExternalHttpRequestError(str(e))
        if parser is not None:
            return parser(response)
        return response


class GroqClient(BaseHttpxClient):
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
