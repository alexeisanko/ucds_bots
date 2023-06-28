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
    welcome_message = f"""Приветствую  "{user.username}".Здесь ты не просто так,наверника тебя уже ввели в курс дела.
Однако,если это не так, ты в любом случаи на верном пути.Меня зовут бот баланс - я твой трекер полезных привычек.
Мои разработчики старались сделать всё максимально просто и удобно.На данный момент ты можешь выбрать те привычки,которые ты готов 
соблюдать в определенное время - зарядка,завтра,обед,ужин.А моя задача проконтролировать их выполнение.
Мои разработчики придумали игровую форму отвественности за выполненные и невыполненные привычки в виде денежного пообщрения и наказания.
Правила простые:
1.Выбирай пункты по которым мы хотим себя контролировать и ставь срок для контроля (например 100 дней).Это можно сделать только 1 раз.
2.Вноси депозит от 500 рублей,чтобы вступить в игру.
3.При появление напоминания о зарядке,завтраке,обеде или ужине,тебе необходимо записать видеокружок в течении получаса для бота с целевым действием будь то,вкусная еда или
физическая активность.При несоблюдении этого правила,ты получаешь штраф в виде 100 рублей со своего счёта.Штраф распределяется равномерно между всеми участниками игры,которые 
выполнили в течении дня все точки контроля.Если ты всё соблюдаешь,как себе и пообещал-ты выигрываешь,полезные привычки закрепляются,баланс только пополняется.
4.Деньги со счета моэно вывести по окончанию срока контроля,который ты себе установил.
5.Также у нас есть паблик,в котором ты можешь посмотреть видеокружки других участников,а также пообщаться.
6.Администратор паблика вынужден удалять обнаженку,нецензурную брань или любое действие,которое может быть оскорбительным для большинства участников игры.
7.Мои разработчики будут дополнять и дополнять функции,если это будет необходимо.

Итак,ты готов начать солюдать полезные привычки и получать деньги за это?Если да,то следующим действием необходимо пополнить баланс от 500 до 1000 рублей,выбрать полезные привычки,время их ежедневного 
выполнения и срок этого челленджа.При отчёте в форме видеокружка деньги на счете,как минимум сохраняются,как максимум умножаются.При отсуствии отчёта в форме видеокружка,я вынужден списать 100 рублей
и раздать остальным участникам,которые выполнили отчёт.Да прибудет с нами баланс!
"""
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
    info_message = """Меня зовут бот баланс - я твой трекер полезных привычек.
Мои разработчики старались сделать всё максимально просто и удобно.На данный момент ты можешь выбрать те привычки,которые ты готов 
соблюдать в определенное время - зарядка,завтра,обед,ужин.А моя задача проконтролировать их выполнение.
Мои разработчики придумали игровую форму отвественности за выполненные и невыполненные привычки в виде денежного пообщрения и наказания.
Правила простые:
1.Выбирай пункты по которым мы хотим себя контролировать и ставь срок для контроля (например 100 дней).Это можно сделать только 1 раз.
2.Вноси депозит от 1000 рублей,чтобы вступить в игру.
3.При появление напоминания о зарядке,завтраке,обеде или ужине,тебе необходимо записать видеокружок в течении получаса для бота с целевым действием будь то,вкусная еда или
физическая активность.При несоблюдении этого правила,ты получаешь штраф в виде 100 рублей со своего счёта.Штраф распределяется равномерно между всеми участниками игры,которые 
выполнили в течении дня все точки контроля.Если ты всё соблюдаешь,как себе и пообещал-ты выигрываешь,полезные привычки закрепляются,баланс только пополняется.
4.Деньги со счета моэно вывести по окончанию срока контроля,который ты себе установил.
5.Также у нас есть паблик,в котором ты можешь посмотреть видеокружки других участников,а также пообщаться.
6.Администратор паблика вынужден удалять обнаженку,нецензурную брань или любое действие,которое может быть оскорбительным для большинства участников игры.
7.Мои разработчики будут дополнять и дополнять функции,если это будет необходимо."""
    await message.answer(info_message)


@router.message(Command(commands=["cansel"]))
@router.message(Text(text='🚫 Отмена'))
async def handle_info_command(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    await message.answer("Возврат в главное меню", reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                                          add_change_activity=True,
                                                                                          add_output_money=True))
    await state.clear()
