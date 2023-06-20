import re
from typing import Dict, Set, Optional, List

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.apps.core.use_case import CORE_USE_CASE
from app.apps.core.bot.filters import type_user
from app.apps.core.bot.keyboards.default.menu import MainMenuButtons
from app.apps.core.bot.keyboards.default.basic import BasicButtons
from app.apps.core.bot.keyboards.inline.callbacks import Action
from app.apps.core.bot.handlers.tracking import tracking
from app.apps.core.bot.states.user import UserActivityState, ActivityState

router = Router()
router.message.filter(type_user.IsGoodBalance())
CALLBACK_SELECT: Dict[int, Optional[Set[str]] | List[str]] = {}


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
    is_can_change, period = await CORE_USE_CASE.is_can_change_activity(message.from_user.id)
    if is_can_change:
        CALLBACK_SELECT[message.from_user.id] = set()
        buttons = await CORE_USE_CASE.get_activities()
        await message.answer("Хорошенько подумай, какие ты возьмешь в этот раз",
                             reply_markup=BasicButtons.confirmation(add_cancel=True))
        await message.answer("Вот такие есть активности",
                             reply_markup=Action.choice_activity(buttons))
        await state.set_state(ActivityState.change_activity)
    else:
        await message.answer(f"Еще рано, ты же обешал все выполнять до {period}")


@router.callback_query(ActivityState.change_activity)
async def switch_choice_activity(callback: CallbackQuery):
    if callback.data in CALLBACK_SELECT.get(callback.from_user.id, set()):
        CALLBACK_SELECT[callback.from_user.id].remove(callback.data)
    else:
        CALLBACK_SELECT[callback.from_user.id].add(callback.data)
    buttons = await CORE_USE_CASE.get_activities()
    await callback.message.edit_reply_markup(
        reply_markup=Action.choice_activity(buttons, CALLBACK_SELECT[callback.from_user.id]))


@router.message(Text(text='✅Подтвердить'), ActivityState.change_activity)
async def waiting_time(message: Message, state: FSMContext):
    if not CALLBACK_SELECT[message.from_user.id]:
        await message.answer("Ты не выбрал ни одной активности, ну ка выбери хоть одну")
        return
    CALLBACK_SELECT[message.from_user.id] = list(CALLBACK_SELECT[message.from_user.id])
    activities = ', '.join(CALLBACK_SELECT[message.from_user.id])
    await message.answer("Супер. Теперь напиши время когда ты будешь присылать мне выбранные активности \n\n "
                         "Формат: 15:30 Время активностей разделять пробелом. Указывать в следующем порядке \n"
                         f"{activities}\n"
                         "Обрати внимание на последовательность! (проверка на дурака)", reply_markup=None)
    await state.set_state(ActivityState.waiting_time_activity)


@router.message(ActivityState.waiting_time_activity)
async def waiting_time(message: Message, state: FSMContext):
    select_time = re.findall(r"\d\d:\d\d", message.text)
    select_activities = CALLBACK_SELECT[message.from_user.id]
    if len(select_time) == len(select_activities):
        for activity, time in zip(select_activities, select_time):
            await CORE_USE_CASE.save_activity_user(time=time, activity_name=activity, user_id=message.from_user.id)
        await message.answer(
            "Финишная прямая перед твоими приключениями!\n укажи период в днях сколько ты будешь придерживаться привычки")
        await state.set_state(ActivityState.waiting_period_activity)
    else:
        activities = ', '.join(CALLBACK_SELECT[message.from_user.id])
        await message.answer("Не соответствует количество активностей и количеству времени. А может не правильно ввел время \n"
                             "Ты ведь не такой дурак, попробуй еще раз \n"
                             "Формат: 15:30 Время активностей разделять пробелом. Указывать в следующем порядке \n"
                             f"{activities}")
        return


@router.message(ActivityState.waiting_period_activity)
async def waiting_period(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        await CORE_USE_CASE.save_period_activity_user(period_day=int(message.text), user_id=message.from_user.id)
        await message.answer("Ура, у тебя получилось!!! теперь я буду следить за тобой в оба глаза \n"
                             f"Через {message.text} день/дней/дня ты сможешь поменять свои активности \n"
                             f"(до тех пор пока не поменяешь, будут оставаться старые)",
                             reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                    add_change_activity=True,
                                                                    add_output_money=True
                                                                    )
                             )
        await state.set_state(UserActivityState.activity)
        await tracking(message.from_user.id, state)

    else:
        await message.answer('Для особо одаренных... Просто введи число... 1 или 30 или 100')

