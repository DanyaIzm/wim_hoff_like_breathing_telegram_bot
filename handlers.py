from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import keyboards


_router = Router()


@_router.message(F.text == "Begin session")
async def handle_session_begin(message: Message) -> None:
    await message.answer("Let the session begin!")


@_router.message(CommandStart())
@_router.message()
async def handle_any_other_message(message: Message) -> None:
    return await message.answer(
        "Hello and welcome to Wim Hof like breathing technique bot!\n\nPress the button below to start",
        reply_markup=keyboards.start_keyboard,
    )


def include_handlers(parent_router: Router) -> None:
    parent_router.include_router(_router)
