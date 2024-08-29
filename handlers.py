from typing import cast
from aiogram import F, Router
from aiogram.filters import CommandStart, and_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from fluentogram import TranslatorRunner

from breathing import hold_breath
import keyboards
from states import BreathCycle

SECONDARY_BREATH_HOLDING_SECONDS = 15


_router = Router()


@_router.message(or_f(F.text == "Cancel", F.text == "Отменить"))
async def handle_cancel(
    message: Message, state: FSMContext, i18n: TranslatorRunner
) -> None:
    await message.answer(
        i18n.session_canceled(),
        reply_markup=keyboards.start_keyboard,
    )
    await state.clear()


@_router.message(or_f(F.text == "Begin session", F.text == "Начать сессию"))
async def handle_session_begin(
    message: Message, state: FSMContext, i18n: TranslatorRunner
) -> None:
    await message.answer(
        i18n.select_rounds_amount(),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(BreathCycle.rounds_amount_selection)


@_router.message(BreathCycle.rounds_amount_selection)
async def handle_rounds_amount_selection(
    message: Message, state: FSMContext, i18n: TranslatorRunner
) -> None:
    try:
        rounds_amount = int(cast(str, message.text))

        if rounds_amount < 1:
            raise ValueError

        await state.update_data({"rounds_amount": rounds_amount})

        await message.answer(
            i18n.rounds_selected(rounds_amount=rounds_amount)
            + "\n\n"
            + i18n.select_seconds_amount()
        )
        await state.set_state(BreathCycle.seconds_to_hold_amount_selection)
    except ValueError:
        await message.answer(i18n.number_incorrect())
        await state.set_state(BreathCycle.rounds_amount_selection)


@_router.message(BreathCycle.seconds_to_hold_amount_selection)
async def handle_seconds_to_hold_amount_selection(
    message: Message, state: FSMContext, i18n: TranslatorRunner
) -> None:
    try:
        seconds_amount = int(cast(str, message.text))

        if seconds_amount <= 0:
            raise ValueError

        await state.update_data({"seconds_amount": seconds_amount})
        print(await state.get_data())

        await message.answer(
            i18n.selected_seconds_amount(seconds_amount=seconds_amount)
        )

        await state.set_state(BreathCycle.pre_breathing)

        await message.bot.send_message(  # type: ignore[union-attr]
            message.from_user.id,  # type: ignore[union-attr]
            i18n.pre_breath(),
            reply_markup=keyboards.ready_keyboard,
        )
    except ValueError:
        await message.answer(i18n.number_incorrect())
        await state.set_state(BreathCycle.seconds_to_hold_amount_selection)


@_router.callback_query(and_f(F.data == "ready", BreathCycle.pre_breathing))
async def handle_prebreathing_ready(
    callback_query: CallbackQuery, state: FSMContext, i18n: TranslatorRunner
) -> None:
    await callback_query.answer(i18n.breath_holding_begin())

    await state.set_state(BreathCycle.primary_breath_holding)

    state_data = await state.get_data()
    seconds_to_hold = state_data["seconds_amount"]

    bot = callback_query.bot
    chat_id = callback_query.from_user.id

    hold_breath_message = i18n.hold_breath()
    seconds_left_message = i18n.seconds_left()

    await hold_breath(
        bot,  # type: ignore[arg-type]
        chat_id,
        seconds_to_hold,
        hold_breath_message,
        seconds_left_message,
    )

    await state.set_state(BreathCycle.deep_breath)

    await bot.send_message(  # type: ignore[union-attr]
        chat_id,
        i18n.deep_breath(),
        reply_markup=keyboards.ready_keyboard,
    )


@_router.callback_query(and_f(F.data == "ready", BreathCycle.deep_breath))
async def handle_deep_breath_ready(
    callback_query: CallbackQuery, state: FSMContext, i18n: TranslatorRunner
) -> None:
    await callback_query.answer(i18n.secondary_breath_holding())

    await state.set_state(BreathCycle.secondary_breath_holding)

    seconds_to_hold = SECONDARY_BREATH_HOLDING_SECONDS

    bot = callback_query.bot
    chat_id = callback_query.from_user.id

    hold_breath_message = i18n.hold_breath()
    seconds_left_message = i18n.seconds_left()

    await hold_breath(
        bot,  # type: ignore[arg-type]
        chat_id,
        seconds_to_hold,
        hold_breath_message,
        seconds_left_message,
    )

    await state.set_state(BreathCycle.round_end)

    await bot.send_message(  # type: ignore[union-attr]
        chat_id,
        i18n.next_round(),
        reply_markup=keyboards.ready_keyboard,
    )


@_router.callback_query(and_f(F.data == "ready", BreathCycle.round_end))
async def handle_round_end(
    callback_query: CallbackQuery, state: FSMContext, i18n: TranslatorRunner
) -> None:
    await callback_query.answer(i18n.round_is_over())

    bot = callback_query.bot
    chat_id = callback_query.from_user.id

    state_data = await state.get_data()
    state_data["rounds_amount"] -= 1

    if state_data["rounds_amount"] == 0:
        await callback_query.answer(i18n.session_is_over())

        await bot.send_message(  # type: ignore[union-attr]
            chat_id,
            i18n.thanks_for_session(),
            reply_markup=keyboards.start_keyboard,
        )

        await state.clear()

        return

    await state.update_data(state_data)

    await bot.send_message(  # type: ignore[union-attr]
        chat_id, i18n.select_seconds_amount()
    )

    await state.set_state(BreathCycle.seconds_to_hold_amount_selection)


@_router.message(CommandStart())
@_router.message()
async def handle_any_other_message(message: Message, i18n: TranslatorRunner) -> None:
    await message.answer(
        i18n.hello(),
        reply_markup=keyboards.start_keyboard,
    )


def include_handlers(parent_router: Router) -> None:
    parent_router.include_router(_router)
