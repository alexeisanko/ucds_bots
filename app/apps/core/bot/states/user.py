from aiogram.fsm.state import State, StatesGroup


class UserActivityState(StatesGroup):
    not_active = State()
    insufficient_balance = State()
    activity = State()


class PayState(StatesGroup):
    waiting_input = State()
    waiting_pay = State()
    waiting_output = State()
    waiting_transfer = State()


class ActivityState(StatesGroup):
    waiting_video_activity = State()
    change_activity = State()
    waiting_time_activity = State()
    waiting_period_activity = State()
    
    
class AdminState(StatesGroup):
    waiting_message = State()
    waiting_user_for_reset_activity = State()
    waiting_user_for_change_balance = State()
    waiting_size_balance = State()
