from typing import Optional, List, Dict, Set

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup

from app.apps.core.use_case import CORE_USE_CASE
from app.apps.core.models import Activity
from .consts import InlineConstructor


class Action(CallbackData, prefix="text"):
    action: str

    @staticmethod
    def choice_activity(btns: List[Dict[str, str]], select: Optional[Dict[str, bool]] = False) -> InlineKeyboardMarkup:
        schema = [1] * len(btns)
        print(btns)
        print(select)
        if select:
            for btn in btns:
                if select[btn['text']]:
                    # if btn['text'] in select:
                    btn['text'] = f"✅ {btn['text']}"
        return InlineConstructor._create_kb(btns, schema)
