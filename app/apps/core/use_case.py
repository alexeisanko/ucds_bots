from typing import Final
from asgiref.sync import sync_to_async
import datetime


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
    async def get_bot_user(user_id: int) -> TGUser:
        return await TGUser.objects.aget(id=user_id)

    @staticmethod
    async def get_activities() -> list[dict]:
        buttons_activity = []
        async for activity in Activity.objects.filter(is_active=True):
            name: str = activity.name
            buttons_activity.append({'text': name, 'callback_data': name})
        return buttons_activity

    @staticmethod
    async def save_activity_user(time: str, activity_name: str, user_id: int) -> None:
        user = await TGUser.objects.aget(id=user_id)
        activity = await Activity.objects.aget(name=activity_name)
        activity_user = TrackedActivity(user=user, activity=activity, tracking_time=time)
        await activity_user.asave()
        return

    @staticmethod
    async def save_period_activity_user(period_day: int, user_id: int) -> datetime.date:
        current_date = datetime.date.today()
        finish_tracking = current_date + datetime.timedelta(days=period_day)
        user = await TGUser.objects.aget(id=user_id)
        period_activity_user = TrackingTime(user=user, period=finish_tracking)
        await period_activity_user.asave()
        return finish_tracking

    @staticmethod
    @sync_to_async
    def get_near_activity(user) -> tuple[TrackedActivity, str]:
        time_now = (datetime.datetime.now() + datetime.timedelta(hours=3)).time()
        near_activities = TrackedActivity.objects.filter(user=user, tracking_time__gt=time_now).order_by('tracking_time')
        near_activity: TrackedActivity = near_activities.first()
        return near_activity, near_activity.activity.name

    @staticmethod
    @sync_to_async
    def penalty_user(guilty_user: TGUser) -> None:
        good_user = TGUser.objects.filter(is_active=True).exclude(id=guilty_user.id)
        add_money = 100 // len(good_user)
        for user in good_user:
            user.balance += add_money
            user.save()
        guilty_user.balance -= 100
        guilty_user.save()

    @staticmethod
    @sync_to_async
    def balance_user(user_id) -> int:
        return TGUser.objects.get(id=user_id).balance

    @staticmethod
    @sync_to_async
    def get_activities_user(user_id: int):
        user = TGUser.objects.get(id=user_id)
        activities_user = TrackedActivity.objects.filter(user=user)
        tracking_time = TrackingTime.objects.get(user=user)
        msg = 'Ваши выбранные активности\n'
        for activity in activities_user:
            msg += f"{activity.activity.name} - время отчета:{activity.tracking_time}\n"
        msg += f'Время до следующих изменений: {tracking_time.period}'
        return msg

    @staticmethod
    @sync_to_async
    def is_can_change_activity(user_id: int) -> tuple[bool, datetime.date]:
        user = TGUser.objects.get(id=user_id)
        try:
            period_activity = TrackingTime.objects.get(user=user).period
        except:
            return (True, "30")
        now_date = datetime.datetime.now().date()
        return (False, period_activity) if period_activity > now_date else (True, period_activity)

    @staticmethod
    @sync_to_async
    def delete_activity(user_id: int) -> None:
        user = TGUser.objects.get(id=user_id)
        TrackedActivity.objects.filter(user=user).delete()
        TrackingTime.objects.filter(user=user).delete()

    @staticmethod
    @sync_to_async
    def data_for_reload():
        data_activity = []
        activities_user = TrackedActivity.objects.all()
        for activity in activities_user:
            end_date = TrackingTime.objects.get(user=activity.user).period
            data_activity.append([activity.user.id, activity.activity.name, activity.tracking_time, end_date])
        data_tracking = []
        tracking_times = TrackingTime.objects.all()
        for time in tracking_times:
            data_tracking.append([time.user.id, time.period])
        return data_activity, data_tracking
    
    @staticmethod
    @sync_to_async
    def get_users_id_activity():
        users = TGUser.objects.filter(is_active=True).exclude(id=1)
        users_id = []
        for user in users:
            users_id.append(user.id)
        return users_id
# Alternative: use a DI middleware to inject the use case into the handler.
# To provide DI middleware, you need to use a third-party library.
# For example, https://github.com/MaximZayats/aiogram-di
CORE_USE_CASE: Final[CoreUseCase] = CoreUseCase()
