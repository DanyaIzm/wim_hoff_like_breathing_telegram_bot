import asyncio
from dataclasses import dataclass
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from fluent_compiler.bundle import FluentBundle  # type: ignore[import-untyped]
from fluentogram import FluentTranslator, TranslatorHub  # type: ignore[import-untyped]

from exceptions import LoadConfigException
from handlers import include_handlers
from middlewares import TranslatorRunnerMiddleware


# TODO: refactor
t_hub = TranslatorHub(
    {"ru": ("ru", "en"), "en": ("en",)},
    translators=[
        FluentTranslator(
            locale="en",
            translator=FluentBundle.from_files("en-US", ["translations/en.ftl"]),
        ),
        FluentTranslator(
            locale="ru",
            translator=FluentBundle.from_files("ru", ["translations/ru.ftl"]),
        ),
    ],
    root_locale="en",
)


@dataclass
class Config:
    bot_token: str


def get_config() -> Config:
    load_dotenv(".env")

    bot_token = getenv("BOT_TOKEN")

    if not bot_token:
        raise LoadConfigException("BOT_TOKEN config variable is required")

    return Config(bot_token=bot_token)


async def main() -> None:
    config = get_config()

    dispatcher = Dispatcher()

    include_handlers(dispatcher)

    translator_runner_middleware = TranslatorRunnerMiddleware()

    dispatcher.message.middleware(translator_runner_middleware)
    dispatcher.callback_query.middleware(translator_runner_middleware)

    bot = Bot(token=config.bot_token)

    await dispatcher.start_polling(bot, _translator_hub=t_hub)


if __name__ == "__main__":
    asyncio.run(main())
