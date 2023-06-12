import asyncio

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.apps.core.use_case import CORE_USE_CASE
from app.apps.core.bot.keyboards.default.menu import MainMenuButtons
from app.apps.core.bot.keyboards.default.basic import BasicButtons
from app.apps.core.bot.keyboards.inline.callbacks import Action

from app.apps.core.bot.states.user import UserActivityState, PayState, ActivityState


router = Router()


@router.message(Text(text='Пополнить баланс'))
async def balance_replenishment(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    await message.answer("Введите сумму кратную 10", reply_markup=BasicButtons.cancel())
    await state.set_state(PayState.waiting_input)


@router.message(PayState.waiting_input)
async def waiting_input_pay(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    try:
        count = int(message.text) % 10
    except ValueError:
        await message.answer("Что то ты ввел какую то фигню, нужно число типо 10", reply_markup=BasicButtons.cancel())
        return
    if count % 10 == 0:
        # TODO сделать платеж. Пока заглушка
        await message.answer("Ссылка на оплату, типо действительно 1 мин. счет начислиться через 5 секунд")
        await asyncio.sleep(5)
        # проверка платежа
        is_paid = True
        user = await CORE_USE_CASE.get_bot_user(message.from_user.id)
        if is_paid:
            if user.is_active:
                user.balance = user.balance + int(message.text)
                await user.asave()
            else:
                user.is_active = True
                user.balance = user.balance + int(message.text)
                await user.asave()
                await message.answer("Поздравляю с регистрацией, теперь давай мы выберим активности которые будем соблюдать",
                                     reply_markup=Action.choice_activity())
                await state.set_state(ActivityState.change_activity)

        else:
            if user.is_active and user.balance:
                await message.answer("Время ссылки закончилось. Возврат в главное меню",
                                     reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                            add_change_activity=True,
                                                                            add_output_money=True))
                await state.set_state(UserActivityState.activity)
            else:
                await message.answer("Время ссылки закончилось. Возврат в главное меню",
                                     reply_markup=MainMenuButtons.add_balance())
                await state.clear()
    else:
        await message.answer("Что то ты ввел какую то фигню, нужно число типо 10", reply_markup=BasicButtons.cancel())


@router.message(Text(text='Изменить активности'), UserActivityState.activity)
async def change_activity(message: Message, state: FSMContext):
    await message.answer("Хорошенько подумай, какие ты возьмешь в этот раз", reply_markup=BasicButtons.confirmation(add_cancel=True))
    await message.answer("Вот такие есть активности",
                         reply_markup=Action.choice_activity())
    await state.set_state(ActivityState.change_activity)
