from gmonitor_lib.clients import ExternalHttpRequestError

from src.broker import broker
from src.parsers import ImageParser, TextParser, BaseParser
from gmonitor_lib.schemas import GptRequest, TopicsEnum, GptResponse


class GptService:
    async def _send_response(self, response: GptResponse) -> None:
        await broker.connect()
        await broker.publish(
            response,
            TopicsEnum.GPT_BOT_RESULT,
        )

    async def process_request(self, request: GptRequest) -> None:
        parser: BaseParser | None = None
        if "сгенерируй изображение" in request.text.lower():
            parser = ImageParser()
        else:
            parser = TextParser()
        try:
            response = await parser.process_request(request)
        except ExternalHttpRequestError as e:
            response = GptResponse(
                text=f"Ошибка на стороне клиента нейросети: {str(e)}",
                chat_id=request.chat_id,
            )
        await self._send_response(response)
