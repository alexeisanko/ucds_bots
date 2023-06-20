from aiogram import Router
from aiogram.types import Message


from app.apps.core.bot.filters import type_channel
from app.config.bot import ID_MESSAGES_CHANNEL


router = Router()
router.message.filter(
    type_channel.ChatTypeFilter(chat_type=["group", "supergroup"])
)


@router.message()
async def save_message_id(message: Message) -> None:
    activity_name = message.text.split()[0]
    ID_MESSAGES_CHANNEL[activity_name] = message.message_id
    print('сообщение', ID_MESSAGES_CHANNEL)
