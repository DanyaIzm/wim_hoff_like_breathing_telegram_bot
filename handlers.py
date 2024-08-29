from typing import cast
from aiogram import F, Router
from aiogram.filters import CommandStart, and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from breathing import hold_breath
import keyboards
from states import BreathCycle

SECONDARY_BREATH_HOLDING_SECONDS = 15


_router = Router()


@_router.message(F.text == "Cancel")
async def handle_cancel(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Session cancelled.\n\nThank you for breathing!",
        reply_markup=keyboards.start_keyboard,
    )
    await state.clear()


@_router.message(F.text == "Begin session")
async def handle_session_begin(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Let the session begin!\n\nSelect amount of rounds you would like to breath.\nSend a number",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(BreathCycle.rounds_amount_selection)


@_router.message(BreathCycle.rounds_amount_selection)
async def handle_rounds_amount_selection(message: Message, state: FSMContext) -> None:
    try:
        rounds_amount = int(cast(str, message.text))

        if rounds_amount < 1:
            raise ValueError

        await state.update_data({"rounds_amount": rounds_amount})
        print(await state.get_data())

        await message.answer(
            f"You've selected {rounds_amount} rounds.\n\nNow select seconds to hold your breath before each breath.\nSend a number"
        )
        await state.set_state(BreathCycle.seconds_to_hold_amount_selection)
    except ValueError:
        await message.answer("Please send me a correct number")
        await state.set_state(BreathCycle.rounds_amount_selection)


@_router.message(BreathCycle.seconds_to_hold_amount_selection)
async def handle_seconds_to_hold_amount_selection(
    message: Message, state: FSMContext
) -> None:
    try:
        seconds_amount = int(cast(str, message.text))

        if seconds_amount <= 0:
            raise ValueError

        await state.update_data({"seconds_amount": seconds_amount})
        print(await state.get_data())

        await message.answer(
            f"You've selected {seconds_amount} seconds to hold your breath for each holding cycle."
        )

        await state.set_state(BreathCycle.pre_breathing)

        await message.bot.send_message(  # type: ignore[union-attr]
            message.from_user.id,  # type: ignore[union-attr]
            "Now please do 20 to 35 deep breaths and push a ready button below",
            reply_markup=keyboards.ready_keyboard,
        )
    except ValueError:
        await message.answer("Please send me a correct number")
        await state.set_state(BreathCycle.seconds_to_hold_amount_selection)


@_router.callback_query(and_f(F.data == "ready", BreathCycle.pre_breathing))
async def handle_prebreathing_ready(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    await callback_query.answer("Let the breath holding begin!")

    await state.set_state(BreathCycle.primary_breath_holding)

    state_data = await state.get_data()
    seconds_to_hold = state_data["seconds_amount"]

    bot = callback_query.bot
    chat_id = callback_query.from_user.id

    await hold_breath(bot, chat_id, seconds_to_hold)  # type: ignore[arg-type]

    await state.set_state(BreathCycle.deep_breath)

    await bot.send_message(  # type: ignore[union-attr]
        chat_id,
        "Now do one deep breath and push a ready button below",
        reply_markup=keyboards.ready_keyboard,
    )


@_router.callback_query(and_f(F.data == "ready", BreathCycle.deep_breath))
async def handle_deep_breath_ready(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    await callback_query.answer("Cool! Now hold your breath again for 15 seconds")

    await state.set_state(BreathCycle.secondary_breath_holding)

    seconds_to_hold = SECONDARY_BREATH_HOLDING_SECONDS

    bot = callback_query.bot
    chat_id = callback_query.from_user.id

    await hold_breath(bot, chat_id, seconds_to_hold)  # type: ignore[arg-type]

    await state.set_state(BreathCycle.round_end)

    await bot.send_message(  # type: ignore[union-attr]
        chat_id,
        "Nice! Push ready button when you're ready for the next round!",
        reply_markup=keyboards.ready_keyboard,
    )


@_router.callback_query(and_f(F.data == "ready", BreathCycle.round_end))
async def handle_round_end(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer("Round is over!")

    bot = callback_query.bot
    chat_id = callback_query.from_user.id

    state_data = await state.get_data()
    state_data["rounds_amount"] -= 1

    if state_data["rounds_amount"] == 0:
        await callback_query.answer("Session is over!")

        await bot.send_message(  # type: ignore[union-attr]
            chat_id,
            "Thank you for your session!",
            reply_markup=keyboards.start_keyboard,
        )

        await state.clear()

        return

    await state.update_data(state_data)

    await bot.send_message(  # type: ignore[union-attr]
        chat_id, "Select amount of seconds for the next round!\nSend a number"
    )

    await state.set_state(BreathCycle.seconds_to_hold_amount_selection)


@_router.message(CommandStart())
@_router.message()
async def handle_any_other_message(message: Message) -> None:
    await message.answer(
        "Hello and welcome to Wim Hof like breathing technique bot!\n\nPress the button below to start",
        reply_markup=keyboards.start_keyboard,
    )


def include_handlers(parent_router: Router) -> None:
    parent_router.include_router(_router)
