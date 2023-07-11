import re
from typing import Dict, Union, List

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from app.apps.core.use_case import CORE_USE_CASE
from app.apps.core.bot.filters import type_user
from app.apps.core.bot.keyboards.default.menu import MainMenuButtons
from app.apps.core.bot.keyboards.default.basic import BasicButtons
from app.apps.core.bot.keyboards.inline.callbacks import Action
from app.apps.core.bot.handlers.tracking import reminder, finish_tracking
from app.apps.core.bot.states.user import UserActivityState, ActivityState, PayState

router = Router()
router.message.filter(type_user.IsGoodBalance())
CALLBACK_SELECT: Dict[int, Union[Dict[str, bool]] | List] = {}
SELECT_MODE: Dict[int, str]


@router.message(Text(text='Ваш баланс'))
async def user_balance(message: Message) -> None:
    if message.from_user is None:
        return
    balance = await CORE_USE_CASE.balance_user(message.from_user.id)
    await message.answer(f"Ваш баланс {balance} руб.")


@router.message(Text(text='Выбранные активности'))
async def user_activities(message: Message) -> None:
    if message.from_user is None:
        return
    msg = await CORE_USE_CASE.get_activities_user(message.from_user.id)
    await message.answer(msg)


@router.message(Text(text='Изменить активности'))
async def change_activity(message: Message, state: FSMContext):
    is_can_change, period = await  CORE_USE_CASE.is_can_change_activity(message.from_user.id)
    if is_can_change:
        buttons = await CORE_USE_CASE.get_activities()
        CALLBACK_SELECT[message.from_user.id] = {x['text']: False for x in buttons}
        await message.answer("Хорошенько подумай, какие ты возьмешь в этот раз",
                             reply_markup=BasicButtons.confirmation(add_cancel=True))
        await message.answer("Вот такие есть активности",
                             reply_markup=Action.choice_activity(buttons))
        await state.set_state(ActivityState.change_activity)
    else:
        await message.answer(f"Еще рано, ты же обешал все выполнять до {period}")


@router.callback_query(ActivityState.change_activity)
async def switch_choice_activity(callback: CallbackQuery):
    CALLBACK_SELECT[callback.from_user.id][callback.data] = False if CALLBACK_SELECT[callback.from_user.id][
        callback.data] else True
    buttons = await CORE_USE_CASE.get_activities()
    await callback.message.edit_reply_markup(
        reply_markup=Action.choice_activity(buttons, CALLBACK_SELECT[callback.from_user.id]))


@router.message(Text(text='✅Подтвердить'), ActivityState.change_activity)
async def confirm_activity(message: Message, state: FSMContext):
    if not CALLBACK_SELECT[message.from_user.id]:
        await message.answer("Ты не выбрал ни одной активности, ну ка выбери хоть одну")
        return
    CALLBACK_SELECT[message.from_user.id] = [[x, 0] for x, y in CALLBACK_SELECT[message.from_user.id].items() if y]
    await message.answer(
        "С активностями определились. Теперь напиши время когда ты будешь присылать мне выбранные активности \n\n "
        "Формат: 15:30.\n"
        f'Начнем с активности "{CALLBACK_SELECT[message.from_user.id][0][0]}"\n', reply_markup=None)
    await state.set_state(ActivityState.waiting_time_activity)


@router.message(ActivityState.waiting_time_activity)
async def waiting_time(message: Message, state: FSMContext):
    select_time = re.findall(r"\d?\d:\d\d", message.text)
    if len(select_time) == 1:
        select_time = select_time[0]
        for i in range(len(CALLBACK_SELECT[message.from_user.id])):
            if not CALLBACK_SELECT[message.from_user.id][i][1]:
                select_time = '0' + select_time if len(select_time) == 4 else select_time
                CALLBACK_SELECT[message.from_user.id][i][1] = select_time
                print(select_time)
                if not CALLBACK_SELECT[message.from_user.id][-1][1]:
                    await message.answer(
                        f'Принято. теперь напиши время для активности под названием "{CALLBACK_SELECT[message.from_user.id][i + 1][0]}"')
                    return
                else:
                    select_activities = CALLBACK_SELECT[message.from_user.id]
                    for activity, time in select_activities:
                        await CORE_USE_CASE.save_activity_user(time=time, activity_name=activity,
                                                               user_id=message.from_user.id)
                    buttons = [{'text': 'Hard', 'callback_data': 'Hard'}, {'text': 'Lite', 'callback_data': 'Lite'}]
                    SELECT_MODE[message.from_user.id] = 'Hard'
                    await message.answer(
                        "Финишная прямая! Выбери режим которому ты будешь следовать \n"
                        "Lite - Выходные это отдых. \n"
                        "Hard - Буду следить каждый божий день.\n"
                        "Как определишься, указывай период в днях сколько ты будешь придерживаться,тех полезных привычек,которые ты выбрал (например 90) и начнем веселье",
                        reply_markup=Action.choice_mode(buttons, SELECT_MODE[message.from_user.id]))
                    await state.set_state(ActivityState.waiting_period_activity)
    else:
        await message.answer("Не корректный формат. Введите время в следующем формате: 15:47")
        return


@router.callback_query(ActivityState.waiting_period_activity)
async def switch_choice_activity(callback: CallbackQuery):
    buttons = [{'text': 'Hard', 'callback_data': 'Hard'}, {'text': 'Lite', 'callback_data': 'Lite'}]
    SELECT_MODE[callback.from_user.id] = callback.data
    await callback.message.edit_reply_markup(
        reply_markup=Action.choice_mode(buttons, callback.data))


@router.message(ActivityState.waiting_period_activity)
async def waiting_period(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        end_date = await CORE_USE_CASE.save_period_activity_user(period_day=int(message.text),
                                                                 user_id=message.from_user.id,
                                                                 mode=SELECT_MODE[message.from_user.id])
        await message.answer("Ура, у тебя получилось!!! теперь я буду следить за тобой в оба глаза \n"
                             f"Через {message.text} день/дней/дня ты сможешь поменять свои активности \n"
                             "А еще ты можешь смотреть как справляются остальные на канале https://t.me/ecobalanc",
                             reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                    add_change_activity=True,
                                                                    add_output_money=True
                                                                    )
                             )
        await state.set_state(UserActivityState.activity)

        scheduler = AsyncIOScheduler()
        select_activities = CALLBACK_SELECT[message.from_user.id]
        days = '*' if SELECT_MODE[message.from_user.id] == 'Hard' else 'mon-fri'
        for activity, time in select_activities:
            hours, minutes = time.split(':')
            time_zone = timezone('Europe/Moscow')
            scheduler.add_job(reminder,
                              'cron',
                              args=(message.from_user.id, activity, state),
                              day=days,
                              hour=hours,
                              minute=minutes,
                              end_date=end_date,
                              timezone=time_zone
                              )
        scheduler.add_job(finish_tracking,
                          'date',
                          run_date=end_date,
                          args=(message.from_user.id,)
                          )
        scheduler.start()
    else:
        await message.answer('Для особо одаренных... Просто введи число... 1 или 30 или 100')


@router.message(Text(text='Вывести деньги'))
async def output_money(message: Message, state: FSMContext):
    is_can_output, period = await CORE_USE_CASE.is_can_change_activity(message.from_user.id)
    if is_can_output:
        await message.answer("Введи сумму кратную 100 которую ты хочешь вывести",
                             reply_markup=BasicButtons.cancel())
        await state.set_state(PayState.waiting_output)
    else:
        await message.answer(
            f"Можно вывести деньги только после окончания заявленного тобой срока активностей (после {period})")
