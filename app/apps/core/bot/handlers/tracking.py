import asyncio

from aiogram import Router, Bot
from aiogram.types import Message, ReplyKeyboardRemove

from app.config.bot import TG_TOKEN, ID_MESSAGES_CHANNEL, ID_GROUP
from app.apps.core.bot.keyboards.default.menu import MainMenuButtons
from app.apps.core.use_case import CORE_USE_CASE
from aiogram.fsm.context import FSMContext
from app.apps.core.bot.states.user import ActivityState

router = Router()
bot = Bot(TG_TOKEN, parse_mode="HTML")


async def reminder(user_id: int, activity_name: str, state: FSMContext):
    user = await CORE_USE_CASE.get_bot_user(user_id=user_id)
    if user.balance >= 100:
        await bot.send_message(user.id, "Там там там. Пришло время очередной активности\n"
                                        f"И это {activity_name}\n"
                                        f"У тебя есть целый час. Присылай кружочек в потдтверждении и я зачту его тебе",
                               reply_markup=ReplyKeyboardRemove())
        await state.set_state(ActivityState.waiting_video_activity)
        await state.update_data(activity_name=activity_name)
        await asyncio.sleep(3565)
        if await state.get_state() == ActivityState.waiting_video_activity and (await state.get_data()).get('activity_name') == activity_name:
            await bot.send_message(user.id, "Ну дружочек...не успел..или не захотел..или богатый слишком"
                                            f"Я снимаю у тебя 100 рублей и передаю другим участникам за пропуск"
                                            f"До встречи на следующей активности",
                                   reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                          add_change_activity=True,
                                                                          add_output_money=True
                                                                          )
                                   )
            await CORE_USE_CASE.penalty_user(user)
            await state.clear()
            if user.balance < 100:
                await bot.send_message(user.id, f"Ну вот и все..У тебя осталось всего{user.balance} руб. Ннаверно нужно положить еще",
                                       reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                              add_change_activity=True,
                                                                              add_output_money=True
                                                                              )
                                       )
                await state.clear()
            return


@router.message(ActivityState.waiting_video_activity)
async def waiting_period(message: Message, state: FSMContext) -> None:
    if message.video_note:
        await message.answer("Так уж и быть, зачтем на этот раз\n"
                             "Теперь с чистой совестью можно посмотреть на других на канале https://t.me/ecobalanc",
                             reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                    add_change_activity=True,
                                                                    add_output_money=True
                                                                    )
                             )
        activity = await state.get_data()
        activity_name = activity['activity_name']

        await bot.send_video_note(chat_id=ID_GROUP, video_note=message.video_note.file_id,
                                  reply_to_message_id=ID_MESSAGES_CHANNEL[activity_name])
        await state.clear()


async def finish_tracking(user_id):
    await CORE_USE_CASE.delete_activity(user_id)
    await bot.send_message(user_id, "Поздравляю! ты честно продержался все запланированные дни. теперь можешь выбрать сбе новые либо передохнуть",
                           reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                  add_change_activity=True,
                                                                  add_output_money=True
                                                                  ))

# async def tracking(user_id: int, state: FSMContext):
#     user = await CORE_USE_CASE.get_bot_user(user_id=user_id)
#     while user.balance > 0:
#         near_activity, activity_name = await CORE_USE_CASE.get_near_activity(user)
#         if near_activity:
#             now_time = (datetime.datetime.now() + datetime.timedelta(hours=3)).time()
#             wait_second = (near_activity.tracking_time.hour - now_time.hour) * 3600 + \
#                           (near_activity.tracking_time.minute - now_time.minute) * 60 + \
#                           near_activity.tracking_time.second - now_time.second
#         else:
#             wait_second = 3600
#             await asyncio.sleep(wait_second)
#             continue
#         await asyncio.sleep(wait_second)
#         await bot.send_message(user.id, "Там там там. Пришло время очередной активности\n"
#                                         f"И это {activity_name}\n"
#                                         f"У тебя есть целый час. Присылай кружочек в потдтверждении и я зачту его тебе",
#                                reply_markup=None)
#         await state.set_state(ActivityState.waiting_video_activity)
#         await state.update_data(activity_name=activity_name)
#
#         await asyncio.sleep(3600)
#         if await state.get_state() == ActivityState.waiting_video_activity:
#             await bot.send_message(user.id, "Ну дружочек...не успел..или не захотел..или богатый слишком"
#                                             f"Я снимаю у тебя 100 рублей и передаю другим участникам за пропуск"
#                                             f"До встречи на следующей активности",
#                                    reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
#                                                                           add_change_activity=True,
#                                                                           add_output_money=True
#                                                                           )
#                                    )
#             await CORE_USE_CASE.penalty_user(user)
#             await state.clear()
#     await bot.send_message(user.id, "Ну вот и все..деньги закончились..наверно нужно положить еще",
#                            reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
#                                                                   add_change_activity=True,
#                                                                   add_output_money=True
#                                                                   )
#                            )
#     await state.clear()
#     return
