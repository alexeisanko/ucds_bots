from typing import Dict, Any

from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject

from apscheduler.schedulers.asyncio import AsyncIOScheduler


from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class SomeMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        print("Before handler")
        result = await handler(event, data)
        print("After handler")
        return result

    async def pre_process(self, obj: TelegramObject, data: Dict[str, Any], *args: Any):
        data["scheduler"] = self._scheduler