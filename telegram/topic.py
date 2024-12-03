from telethon import TelegramClient
from telethon.tl.functions.channels import GetForumTopicsRequest

from cache_helper import get_cache_data, cache_exists, write_data_to_cache
from constants import TOPIC_ID
from structure_log.logger_setup import logger


async def get_last_message_in_topic(client, chat_id, topic_id):
    async with client:
        messages = await client.get_messages(
            chat_id,
            limit=1,  # Get only the last message
            reply_to=topic_id  # This filters for messages in the specific topic
        )

        if len(messages) > 0:
            last_message = messages[0]
            logger.info(f"Last message ID: {last_message.id}, Text: {last_message.message}")
            return last_message.message
        else:
            logger.warning("No messages found in this topic.")


async def get_topic_id(client, chat_id, topic_name):
    async with client:
        result = await client(GetForumTopicsRequest(
            channel=chat_id,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=10  # Set to the number of topics you want to retrieve
        ))

        for topic in result.topics:
            if topic_name in topic.title:
                return topic.id
    return None

async def get_cached_topic_id(client: TelegramClient, chat_id, topic_name):
    if cache_exists(TOPIC_ID):
        topic_id = get_cache_data(TOPIC_ID)
    else:
        topic_id = await get_topic_id(client, chat_id, topic_name)
        if topic_id is None:
            return
        write_data_to_cache(TOPIC_ID, topic_id)

    return topic_id