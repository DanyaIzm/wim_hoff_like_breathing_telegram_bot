import asyncio
from dataclasses import dataclass
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv


async def count(message: Message) -> None:
    seconds_to_wait = 15

    await message.answer("Let the counter start!")

    message = await message.bot.send_message(
        message.from_user.id, f"Left: {seconds_to_wait}"
    )

    for current_second in range(0, seconds_to_wait, 5):
        await asyncio.sleep(5)

        seconds_left = seconds_to_wait - (current_second + 5)

        await message.edit_text(f"Left: {seconds_left}")

    await message.edit_text("Thank you!")


async def hello(message: Message) -> None:
    return await message.answer(f"Hi! Did you say: {message.text}")


@dataclass
class Config:
    bot_token: str


def get_config() -> Config:
    load_dotenv()

    return Config(bot_token=getenv("BOT_TOKEN"))


async def main() -> None:
    config = get_config()

    dispatcher = Dispatcher()

    dispatcher.message(Command("count"))(count)
    dispatcher.message()(hello)

    bot = Bot(token=config.bot_token)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
