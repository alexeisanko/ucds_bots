import datetime
import asyncio

from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from app.config.bot import ID_CHANNEL, TG_TOKEN
from app.apps.core.use_case import CORE_USE_CASE
from app.apps.core.bot.filters import type_user
from app.apps.core.bot.states.user import AdminState
from app.apps.core.bot.handlers.tracking import reminder, finish_tracking
from app.apps.core.bot.keyboards.default.basic import BasicButtons

bot = Bot(TG_TOKEN, parse_mode="HTML")
router = Router()
router.message.filter(type_user.IsAdmin())


# @router.message(Command(commands=['go']))
# async def start_bot(message: Message, state: FSMContext):
#     scheduler = AsyncIOScheduler()
#     activities, tracking = await CORE_USE_CASE.data_for_reload()
#     for activity in activities:
#         hours, minutes = activity[2].hour, activity[2].minute
#         time_zone = timezone('Europe/Moscow')
#         state_with: FSMContext = FSMContext(bot=bot,
#                                             storage=dp.storage, # dp - экземпляр диспатчера 
#                                             key=StorageKey(
#                                                 chat_id=activity[0], # если юзер в ЛС, то chat_id=user_id
#                                                 user_id=activity[0],  
#                                                 bot_id=bot.id)))
#         scheduler.add_job(reminder,
#                           'cron',
#                           args=(activity[0], activity[1], state_with),
#                           day='*',
#                           hour=hours,
#                           minute=minutes,
#                           end_date=activity[3],
#                           timezone=time_zone
#                           )
#     for track in tracking:
#         scheduler.add_job(finish_tracking,
#                           'date',
#                           run_date=track[1],
#                           args=(track[0],)
#                           )
#     scheduler.start()
#     while True:
#         activities = await CORE_USE_CASE.get_activities()
#         for activity in activities:
#             await bot.send_message(chat_id=ID_CHANNEL, text=f"{activity['text']} ({datetime.datetime.now().date()})",
#                                   disable_notification=True)
#             await asyncio.sleep(1)
#         datetime_now = datetime.datetime.now()
#         date = datetime.datetime(year=datetime_now.year, month=datetime_now.month, day=datetime_now.day)
#         new_datetime = date + datetime.timedelta(days=1)
#         wait_second = (new_datetime - datetime_now).total_seconds()
#         await asyncio.sleep(wait_second + 5)
        
        
@router.message(Command(commands=['message']))
async def waiting_message(message: Message, state: FSMContext):
    await message.answer('Напиши сообщение', reply_markup=BasicButtons.cancel())
    await state.set_state(AdminState.waiting_message)
    

@router.message(AdminState.waiting_message)
async def send_message(message: Message, state: FSMContext) -> None:
    users_id = await CORE_USE_CASE.get_users_id_activity()
    for user_id in users_id:
        try:
            await bot.send_message(user_id, message.text)
        except:
            continue  
    await state.clear()
    
    
