from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.apps.core.use_case import CORE_USE_CASE


class IsGoodBalance(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user, is_new = await CORE_USE_CASE.register_bot_user(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username,
        )
        return True if (user.is_active and user.balance >= 100) else False


class IsNegativeBalance(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user, is_new = await CORE_USE_CASE.register_bot_user(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username,
        )
        return True if user.balance < 100 else False


class IsNotActive(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user, is_new = await CORE_USE_CASE.register_bot_user(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username,
        )
        return True if not user.is_active else False


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user, is_new = await CORE_USE_CASE.register_bot_user(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username,
        )
        return True if user.id == 1111355562 else False
