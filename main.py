import asyncio
import logging
import os

import base58
from dotenv import load_dotenv
from solana.rpc.api import Client
from solders.keypair import Keypair
from telethon import TelegramClient, events

from cache_helper import cache_exists, get_cache_data, write_data_to_cache
from solana_api.simple_sniper import new_call_incoming
from telegram.chat import get_chat, get_cached_chat_id
from telegram.sign_in import sign_in_to_telegram
from telegram.topic import get_cached_topic_id

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Telegram API credentials
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION = "mysession"
CHAT_ID = "chat_id"
TOPIC_ID = "topic_id"

SOL_RPC = os.getenv('SOL_RPC')
# Replace with your own RPC endpoint+
client = Client(SOL_RPC)
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

# Load your wallet using the private key (for testing only)
private_key = base58.b58decode(PRIVATE_KEY)  # Replace with your base58 private key
wallet = Keypair.from_bytes(private_key)


async def main():
    async with TelegramClient(SESSION, API_ID, API_HASH) as client:
        if not await client.is_user_authorized():
            await sign_in_to_telegram(client)

        chat_name = "meme.bot"
        chat_id = await get_cached_chat_id(client, chat_name)
        topic_name = "SOL BOT [60-300K]"
        topic_id= await get_cached_topic_id(client, chat_id, topic_name)

        # Start listening to new messages in the specified topic
        @client.on(events.NewMessage(chats=chat_id, func=lambda e: e.peer_id.channel_id == topic_id))
        async def message_listener(event):
            await new_call_incoming(event)


if __name__ == "__main__":
    asyncio.run(main())
