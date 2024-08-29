import asyncio
from dataclasses import dataclass
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv


def hello(message: Message) -> None:
    return message.answer(f"Hi! Did you say: {message.text}")


@dataclass
class Config:
    bot_token: str


def get_config() -> Config:
    load_dotenv()

    return Config(bot_token=getenv("BOT_TOKEN"))


async def main() -> None:
    config = get_config()

    dispatcher = Dispatcher()

    dispatcher.message()(hello)

    bot = Bot(token=config.bot_token)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
