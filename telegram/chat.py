from typing import Optional

from telethon import TelegramClient
from telethon.tl.types import Channel

from cache_helper import cache_exists, get_cache_data, write_data_to_cache
from constants import CHAT_ID
from log import logger


async def get_chat(client: TelegramClient, chat_name: str) -> Optional[Channel]:
    """Get last message from specified channels."""
    try:
        logger.info("Scanning for channels...")
        dialogs = await client.get_dialogs()

        for dialog in dialogs:
            if isinstance(dialog.entity, Channel):
                if chat_name in dialog.name:
                    return dialog.entity
    except Exception as e:
        logger.error("Failed to scan for channel", e)

    logger.warning("Channel not found")
    return None

async def get_cached_chat_id(client: TelegramClient, chat_name: str) -> Optional[int]:
    if cache_exists(CHAT_ID):
        chat_id = get_cache_data(CHAT_ID)
    else:
        chat = await get_chat(client, chat_name)
        if chat is None:
            return
        chat_id = chat.id
        write_data_to_cache(CHAT_ID, chat_id)
    return chat_id