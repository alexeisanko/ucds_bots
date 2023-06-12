from asgiref.sync import sync_to_async, async_to_sync

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup

from app.apps.core.use_case import CORE_USE_CASE
from app.apps.core.models import Activity
from .consts import InlineConstructor


class Action(CallbackData, prefix="text"):
    action: str

    @staticmethod
    def choice_activity() -> InlineKeyboardMarkup:
        schema = [1, 1, 1, 1]
        activities: list[Activity] = CORE_USE_CASE.get_activities()
        btns = sync_to_async([{'text': activity.name, 'callback_data': activity.name} for activity in activities if activity.is_active])
        # btns = [{'text': 'Завтрак', 'callback_data': 'breakfast'},
        #         {'text': 'Обед', 'callback_data': 'lunch'},
        #         {'text': 'Ужин', 'callback_data': 'dinner'},
        #         {'text': 'Бег', 'callback_data': 'run'}]
        return InlineConstructor._create_kb(btns, schema)

