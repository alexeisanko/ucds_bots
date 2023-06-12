from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.apps.core.use_case import CORE_USE_CASE
from app.apps.core.bot.keyboards.default.menu import MainMenuButtons
from app.apps.core.bot.states.user import UserActivityState

router = Router()


@router.message(Command(commands=["start"]))
async def handle_start_command_not_activity_user(message: Message, state: FSMContext) -> None:
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
        'Для регистрации тебе необходимо Пополнить баланс' \
        'Тыкай на кнопку олпачивай и начинай следовать своей мечте'
    if is_new or not user.is_active:
        await message.answer(welcome_message, reply_markup=MainMenuButtons.add_balance())
    else:
        if user.is_active and user.balance:
            await state.set_state(UserActivityState.activity)
            await message.answer(f'Привет {user.username} ты уже в секте, для получения информации введи /info',
                                 reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                        add_change_activity=True,
                                                                        add_output_money=True))
        else:
            await message.answer(f'Привет {user.username} ты уже в секте, но видимо кончились деньги,пополняй скорей!',
                                 reply_markup=MainMenuButtons.add_balance())


@router.message(Command(commands=["info"]))
async def handle_info_command(message: Message) -> None:
    if message.from_user is None:
        return
    await message.answer("Информационное сообщение, где расписывается о сервисе")


@router.message(Text(text='🚫 Отмена'))
async def handle_info_command(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    user = await CORE_USE_CASE.get_bot_user(message.from_user.id)
    if user.is_active and user.balance:
        await message.answer("Возврат в главное меню", reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                                              add_change_activity=True,
                                                                                              add_output_money=True))
        await state.set_state(UserActivityState.activity)
    else:
        await message.answer("Возврат в главное меню. Но денег все равно нет",
                             reply_markup=MainMenuButtons.add_balance())
        await state.clear()

# @router.message(Command(commands=["my_activity"]))
# async def handle_activity_user_command(message: Message) -> None:
#     if message.from_user is None:
#         return
#     select_activities, tracking_time = CORE_USE_CASE.get_activity_user(message.from_user.id)
#     await message.answer(
#         f"User Id: <b>{message.from_user.id}</b>\n" f"Chat Id: <b>{message.chat.id}</b>"
#     )
