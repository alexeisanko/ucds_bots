import asyncio
import time
from typing import Optional, List

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from yoomoney import Client
from yoomoney import Quickpay

from app.apps.core.use_case import CORE_USE_CASE
from app.apps.core.bot.keyboards.default.menu import MainMenuButtons
from app.apps.core.bot.keyboards.default.basic import BasicButtons
from app.apps.core.bot.keyboards.inline.callbacks import Action
from app.apps.core.bot.states.user import PayState, ActivityState
from app.apps.core.bot.handlers.user_active import CALLBACK_SELECT
from app.config.bot import YOOMONEY_TOKEN, YOOMONEY_RECEIVER

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
        count = int(message.text)
    except ValueError:
        await message.answer("Что то ты ввел какую то фигню, нужно число кратное 10 (например, 500)", reply_markup=BasicButtons.cancel())
        return
    if count % 10 == 0:
        yoomoney, label, payment_link = get_link(message, count)
        await message.answer(f"Ссылка на оплату действительна 1 минуту!\n"
                             f"Во время ожидания оплаты все функции недоступны\n{payment_link}")
        is_paid = payment_processing(yoomoney, label)
        user = await CORE_USE_CASE.get_bot_user(message.from_user.id)
        print(is_paid)
        if is_paid:
            if user.is_active:
                user.balance = user.balance + int(message.text)
                await user.asave()
                await message.answer("Оплата прошла. Урааа. Спасибо!",
                                     reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                            add_change_activity=True,
                                                                            add_output_money=True))
            else:
                user.is_active = True
                user.balance = user.balance + int(message.text)
                await user.asave()
                buttons = await CORE_USE_CASE.get_activities()
                CALLBACK_SELECT[message.from_user.id] = set()
                await message.answer("Поздравляю с регистрацией, теперь давай мы выберим активности которые будем соблюдать",
                                     reply_markup=BasicButtons.confirmation())
                await message.answer(
                    "Вот какие есть активности",
                    reply_markup=Action.choice_activity(buttons))
                await state.set_state(ActivityState.change_activity)
        else:
            if user.is_active and user.balance:
                await message.answer("Время ссылки закончилось. Возврат в главное меню",
                                     reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                            add_change_activity=True,
                                                                            add_output_money=True))
                await state.clear()
            else:
                await message.answer("Время ссылки закончилось. Возврат в главное меню",
                                     reply_markup=MainMenuButtons.add_balance())
                await state.clear()
    else:
        await message.answer("Что то ты ввел какую то фигню, нужно число типо 10", reply_markup=BasicButtons.cancel())


def get_link(message: Message, count: int) -> tuple:
    yoomoney = Client(YOOMONEY_TOKEN)
    label = f"{time.time()}{message.from_user.id}"
    payment_link = _create_pay(count, label)
    return yoomoney, label, payment_link


def payment_processing(yoomoney, label) -> bool:
    for i in range(60):
        is_success_pay = _check_pay(yoomoney, label)
        print(is_success_pay)
        if is_success_pay == 'success':
            return True
        time.sleep(1)
    return False


def _create_pay(summ, label):
    quickpay = Quickpay(
        receiver=YOOMONEY_RECEIVER,
        quickpay_form="shop",
        targets="ECOBALANCE super puper",
        paymentType="SB",
        sum=summ,
        label=label
    )
    return quickpay.redirected_url


def _check_pay(yoomoney: Client, pay_id: str) -> Optional[str]:
    history = yoomoney.operation_history(label=pay_id)
    for operation in history.operations:
        return operation.status
