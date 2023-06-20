from typing import List

from aiogram import Router

from .basic import router as basic_router
from .admin import router as admin_router
from .pay import router as pay_router
from .user_active import router as user_active_router
from .user_not_active import router as user_not_active_router
from .tracking import router as tracking_router
from .group_chat import router as group_router


def prepare_router() -> List[Router]:
    return [group_router, admin_router, basic_router, pay_router, user_active_router, user_not_active_router, tracking_router,  ]
