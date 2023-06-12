from typing import List

from aiogram import Router

from .user import router as user_router
from .main import router as main_router


def prepare_router() -> List[Router]:
    return [main_router, user_router]
