import asyncio

from aiogram import Bot


async def hold_breath(bot: Bot, chat_id: int, seconds_to_hold: int) -> None:
    seconds_left = seconds_to_hold

    await bot.send_message(chat_id, "Now hold your breath!")
    timer_message = await bot.send_message(chat_id, f"Seconds left: {seconds_left}")

    while seconds_left > 0:
        await asyncio.sleep(1)
        seconds_left -= 1
        await timer_message.edit_text(f"Seconds left: {seconds_left}")

    await timer_message.delete()
