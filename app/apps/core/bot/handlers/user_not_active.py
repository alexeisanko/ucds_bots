from aiogram import Router
from aiogram.types import Message

from app.apps.core.bot.filters import type_user
from app.apps.core.bot.keyboards.default.menu import MainMenuButtons

router = Router()
router.message.filter(type_user.IsNegativeBalance())


@router.message()
async def negative_message(message: Message):
    await message.answer('Ничего тебе не скажу, вначале деньги, потом разговор',
                         reply_markup=MainMenuButtons.main_menu(add_select_activity=True,
                                                                add_change_activity=True,
                                                                add_output_money=True))
