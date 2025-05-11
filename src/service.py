from gmonitor_lib.clients import ExternalHttpRequestError

from broker import broker
from parsers import ImageParser, TextParser, BaseParser, AudioParser
from gmonitor_lib.schemas import TopicsEnum, GptDto, GptDtoType


class GptService:
    async def _send_response(self, response: GptDto) -> None:
        await broker.connect()
        await broker.publish(
            response,
            TopicsEnum.GPT_BOT_RESULT,
        )

    async def process_request(self, request: GptDto) -> None:
        parser: BaseParser | None = None
        if request.type == GptDtoType.AUDIO:
            parser = AudioParser()
        elif "сгенерируй изображение" in request.content.lower():
            parser = ImageParser()
        else:
            parser = TextParser()
        try:
            response = await parser.process_request(request)
        except ExternalHttpRequestError as e:
            response = GptDto(
                content=f"Ошибка на стороне клиента нейросети: {str(e)}",
                chat_id=request.chat_id,
            )
        await self._send_response(response)
