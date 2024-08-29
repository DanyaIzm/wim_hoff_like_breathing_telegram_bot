from collections.abc import Awaitable, Callable
from typing import Any, cast
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from fluentogram import TranslatorHub  # type: ignore[import-untyped]


class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        event = cast(Message, event)

        hub: TranslatorHub = data.get("_translator_hub")
        data["i18n"] = hub.get_translator_by_locale(event.from_user.language_code)  # type: ignore [union-attr]
        # data["i18n"] = hub.get_translator_by_locale("en")  # type: ignore [union-attr]
        return await handler(event, data)
