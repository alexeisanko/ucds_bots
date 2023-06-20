from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.apps.core.use_case import CORE_USE_CASE
from app.apps.core.bot.keyboards.default.menu import MainMenuButtons
from app.apps.core.bot.filters import type_user

router = Router()


@router.message(Command(commands=["start"]), type_user.IsNotActive())
async def first_start(message: Message) -> None:
    if message.from_user is None:
        return
    user, is_new = await CORE_USE_CASE.register_bot_user(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        username=message.from_user.username,
    )
    welcome_message = \
        f'Приветствую в {user.username} в семье "ECO Balance"\n' \
        'Это как трекер привычек, но с определенной ответственностью' \
        'текст бла бла вот все правила,в общем пополни свой баланс 😘 \n\n' \
        'Для регистрации тебе необходимо Пополнить баланс. ' \
        'Тыкай на кнопку олпачивай и начинай следовать своей мечте'
    await message.answer(welcome_message, reply_markup=MainMenuButtons.add_balance())


@router.message(Command(commands=["start"]), type_user.IsGoodBalance())
async def good_start(message: Message) -> None:
    if message.from_user is None:
        return
    user = await CORE_USE_CASE.get_bot_user(message.from_user.id)
    await message.answer(f'Привет {user.username} ты уже в секте, для получения информации введи /info',
                         reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                add_change_activity=True,
                                                                add_output_money=True))


@router.message(Command(commands=["start"]), type_user.IsNegativeBalance())
async def bad_start(message: Message) -> None:
    if message.from_user is None:
        return
    user = await CORE_USE_CASE.get_bot_user(message.from_user.id)
    await message.answer(f'Привет {user.username} ты уже в секте, но видимо кончились деньги,пополняй скорей!',
                         reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                add_change_activity=True,
                                                                add_output_money=True))


@router.message(Command(commands=["info"]))
async def handle_info_command(message: Message) -> None:
    if message.from_user is None:
        return
    await message.answer("Информационное сообщение, где расписывается о сервисе")


@router.message(Command(commands=["cansel"]))
@router.message(Text(text='🚫 Отмена'))
async def handle_info_command(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    await message.answer("Возврат в главное меню", reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                                          add_change_activity=True,
                                                                                          add_output_money=True))
    await state.clear()
