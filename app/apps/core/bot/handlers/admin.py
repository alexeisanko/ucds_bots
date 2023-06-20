import datetime
import asyncio

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Bot

from app.config.bot import ID_CHANNEL, TG_TOKEN
from app.apps.core.use_case import CORE_USE_CASE
from app.apps.core.bot.filters import type_user

bot = Bot(TG_TOKEN, parse_mode="HTML")
router = Router()
router.message.filter(type_user.IsAdmin())


@router.message(Command(commands=['go']))
async def start_bot(message: Message):
    while True:
        activities = await CORE_USE_CASE.get_activities()
        for activity in activities:
            await bot.send_message(chat_id=ID_CHANNEL, text=f"{activity['text']} ({datetime.datetime.now().date()})",
                                   disable_notification=True)
            await asyncio.sleep(1)
        datetime_now = datetime.datetime.now()
        date = datetime.datetime(year=datetime_now.year, month=datetime_now.month, day=datetime_now.day)
        new_datetime = date + datetime.timedelta(days=1)
        wait_second = (new_datetime - datetime_now).total_seconds()
        await asyncio.sleep(wait_second + 5)
