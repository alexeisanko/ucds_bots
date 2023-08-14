import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from app.apps.core.bot.handlers import prepare_router
from app.config.bot import RUNNING_MODE, TG_TOKEN, RunningMode
from app.apps.core.use_case import CORE_USE_CASE
from app.apps.core.bot.handlers.tracking import reminder, finish_tracking
from app.apps.core.bot.middleware import StructLoggingMiddleware
from app.apps.core.bot import utils

bot = Bot(TG_TOKEN, parse_mode="HTML")

dispatcher = Dispatcher()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def _register_routers() -> None:
    routers = prepare_router()
    for router in routers:
        dispatcher.include_router(router)


def _setup_logging() -> None:
    dispatcher["aiogram_logger"] = utils.logging.setup_logger().bind(type="aiogram")


def _setup_middlewares() -> None:
    dispatcher.update.outer_middleware(StructLoggingMiddleware(logger=dispatcher["aiogram_logger"]))


async def _set_bot_commands() -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="/start", description="Зарегистрироваться"),
            BotCommand(command="/info", description="Информация о боте"),
            # BotCommand(command="/cancel", description="Отмена"),
        ]
    )

@dispatcher.startup()
async def on_startup() -> None:
    # Register all routers
    _setup_logging()
    logger = dispatcher["aiogram_logger"]
    logger.debug("Configuring aiogram")
    _setup_middlewares()
    _register_routers()
    # Set default commands
    await _set_bot_commands()
    logger.info("Configured aiogram")
    await start_current_task()


async def start_current_task() -> None:
    scheduler = AsyncIOScheduler()
    activities, tracking = await CORE_USE_CASE.data_for_reload()
    for activity in activities:
        hours, minutes = activity[2].hour, activity[2].minute
        time_zone = timezone('Europe/Moscow')
        state_with: FSMContext = FSMContext(bot=bot,
                                            storage=dispatcher.storage,  # dp - экземпляр диспатчера
                                            key=StorageKey(
                                                chat_id=activity[0],  # если юзер в ЛС, то chat_id=user_id
                                                user_id=activity[0],
                                                bot_id=bot.id))
        days = '*' if activity[4] == 'Hard' else 'mon-fri'
        scheduler.add_job(reminder,
                          'cron',
                          args=(activity[0], activity[1], state_with),
                          day='*',
                          day_of_week=days,
                          hour=hours,
                          minute=minutes,
                          end_date=activity[3],
                          timezone=time_zone
                          )
    for track in tracking:
        scheduler.add_job(finish_tracking,
                          'date',
                          run_date=track[1],
                          args=(track[0],)
                          )
    scheduler.start()


def run_polling() -> None:
    dispatcher.run_polling(bot)


def run_webhook() -> None:
    raise NotImplementedError("Webhook mode is not implemented yet")


if __name__ == "__main__":
    if RUNNING_MODE == RunningMode.LONG_POLLING:
        run_polling()
    elif RUNNING_MODE == RunningMode.WEBHOOK:
        run_webhook()
    else:
        raise RuntimeError(f"Unknown running mode: {RUNNING_MODE}")
