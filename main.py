import asyncio
from dataclasses import dataclass
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from exceptions import LoadConfigException
from handlers import include_handlers


@dataclass
class Config:
    bot_token: str


def get_config() -> Config:
    load_dotenv(".env")

    bot_token = getenv("BOT_TOKEN")

    print(bot_token)

    if not bot_token:
        raise LoadConfigException("BOT_TOKEN config variable is required")

    return Config(bot_token=bot_token)


async def main() -> None:
    config = get_config()

    dispatcher = Dispatcher()

    include_handlers(dispatcher)

    bot = Bot(token=config.bot_token)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
