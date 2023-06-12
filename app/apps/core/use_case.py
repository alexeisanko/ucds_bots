from typing import Final

from app.apps.core.models import TGUser, TrackedActivity, TrackingTime, Activity


# The `UseCase` classes are used to separate the business logic from the rest of the code.
# Also, because of this, we can easily use the same business logic in different places.
# For example, in the bot and in the web application.

# The main reason to use classes instead of functions is that
# the `UseCase` classes may depend on different services.


class CoreUseCase:
    @staticmethod
    async def register_bot_user(
            user_id: int,
            chat_id: int,
            username: str | None,
    ) -> tuple[TGUser, bool]:
        return await TGUser.objects.aget_or_create(
            id=user_id,
            chat_id=chat_id,
            username=username,
        )

    @staticmethod
    async def get_activities_user(user_id: int) -> tuple[TrackedActivity, TrackingTime]:
        user = TGUser.objects.aget(id=user_id)
        activities_user = await TrackedActivity.objects.filter(user=user)
        tracking_time = await TrackingTime.objects.aget(user=user)
        return activities_user, tracking_time

    @staticmethod
    async def get_bot_user(user_id: int) -> TGUser:
        return await TGUser.objects.aget(id=user_id)

    @staticmethod
    def get_activities() -> list[Activity]:
        return Activity.objects.filter(is_active=True)


# Alternative: use a DI middleware to inject the use case into the handler.
# To provide DI middleware, you need to use a third-party library.
# For example, https://github.com/MaximZayats/aiogram-di
CORE_USE_CASE: Final[CoreUseCase] = CoreUseCase()
