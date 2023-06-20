from enum import Enum

from app.config import env


class RunningMode(str, Enum):
    LONG_POLLING = "LONG_POLLING"
    WEBHOOK = "WEBHOOK"


TG_TOKEN = env("TG_TOKEN", cast=str)
ID_CHANNEL = env("ID_CHANEL", cast=int)
ID_GROUP = env("ID_GROUP", cast=int)
YOOMONEY_TOKEN = env("YOOMONEY_TOKEN", cast=str)
YOOMONEY_RECEIVER = env("YOOMONEY_RECEIVER", cast=int)
ID_MESSAGES_CHANNEL = {}

RUNNING_MODE = env("RUNNING_MODE", cast=RunningMode, default=RunningMode.LONG_POLLING)
WEBHOOK_URL = env("WEBHOOK_URL", cast=str, default="")
