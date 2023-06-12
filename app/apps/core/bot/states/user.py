from aiogram.fsm.state import State, StatesGroup


class UserActivityState(StatesGroup):
    not_active = State()
    insufficient_balance = State()
    activity = State()


class PayState(StatesGroup):
    waiting_input = State()
    waiting_pay = State()
    waiting_output = State()


class ActivityState(StatesGroup):
    waiting_video_activity = State()
    change_activity = State()