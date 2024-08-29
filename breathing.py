import asyncio

from aiogram import Bot


async def hold_breath(
    bot: Bot,
    chat_id: int,
    seconds_to_hold: int,
    hold_breath_message: str,
    seconds_left_message: str,
) -> None:
    seconds_left = seconds_to_hold

    await bot.send_message(chat_id, hold_breath_message)
    timer_message = await bot.send_message(
        chat_id, f"{seconds_left_message}: {seconds_left}"
    )

    while seconds_left > 0:
        await asyncio.sleep(1)
        seconds_left -= 1
        await timer_message.edit_text(f"{seconds_left_message}: {seconds_left}")

    await timer_message.delete()
