import aiogram.types

from .consts import DefaultConstructor


class MainMenuButtons(DefaultConstructor):
    @staticmethod
    def main_menu(
            add_select_activity: bool = False,
            add_change_activity: bool = False,
            add_output_money: bool = False
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = []
        btns = []
        schema.append(1)
        btns.append('Ваш баланс')
        schema.append(1)
        btns.append('Пополнить баланс')
        if add_select_activity:
            schema.append(1)
            btns.append('Выбранные активности')
        if add_change_activity:
            schema.append(1)
            btns.append('Изменить активности')
        if add_output_money:
            schema.append(1)
            btns.append('Вывести деньги')
        return MainMenuButtons._create_kb(btns, schema)

    @staticmethod
    def add_balance() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ['Пополнить баланс']
        return MainMenuButtons._create_kb(btns, schema)
