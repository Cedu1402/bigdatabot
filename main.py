import asyncio
import os

import base58
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from telethon import TelegramClient, events

from constants import SESSION
from loguru import logger
from solana_api.simple_sniper import new_call_incoming
from telegram.chat import get_cached_chat_id
from telegram.sign_in import sign_in_to_telegram
from telegram.topic import get_cached_topic_id

# Load environment variables
load_dotenv()

# Telegram API credentials
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')

TOPIC_NAME = "SOL BOT [60-300K]"
CHAT_NAME = "meme.bot"

SOL_RPC = os.getenv('SOL_RPC')
# Replace with your own RPC endpoint+
sol_client = AsyncClient(SOL_RPC)
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

# Load your wallet using the private key (for testing only)
private_key = base58.b58decode(PRIVATE_KEY)  # Replace with your base58 private key
wallet = Keypair.from_bytes(private_key)


async def main():
    while True:
        try:
            async with TelegramClient(SESSION, API_ID, API_HASH) as client:
                if not await client.is_user_authorized():
                    await sign_in_to_telegram(client)

                chat_id = await get_cached_chat_id(client, CHAT_NAME)
                topic_id = await get_cached_topic_id(client, chat_id, TOPIC_NAME)

                # Start listening to new messages in the specified topic
                @client.on(events.NewMessage(chats=chat_id))
                async def message_listener(event):
                    if event.message.reply_to:
                        # Get the topic ID from reply_to.reply_to_top_id
                        message_topic_id = event.message.reply_to.reply_to_msg_id
                        if message_topic_id == topic_id:
                            print("Message is in the target topic")
                            await new_call_incoming(event.message.text, sol_client, wallet)

                await client.run_until_disconnected()
        except Exception as e:
            logger.error(e, "Watch ran into an error! Restarting now....")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
