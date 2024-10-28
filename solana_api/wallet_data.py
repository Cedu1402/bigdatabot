import asyncio
import os

import base58
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair

from log import logger


async def get_wallet_balance(client: AsyncClient, wallet: Keypair):
    """Fetches the wallet balance in lamports (1 SOL = 1e9 lamports)."""
    try:
        balance_result = await client.get_balance(wallet.pubkey())
        balance = balance_result.value
        logger.info("Current balance %s", balance)
        return balance
    except Exception as e:
        logger.error("Failed to get balance", str(e))
        return 0


if __name__ == '__main__':
    load_dotenv()
    SOL_RPC = os.getenv('SOL_RPC')
    # Replace with your own RPC endpoint+
    sol_client = AsyncClient(SOL_RPC)
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')

    # Load your wallet using the private key (for testing only)
    private_key = base58.b58decode(PRIVATE_KEY)  # Replace with your base58 private key
    wallet = Keypair.from_bytes(private_key)

    asyncio.run(get_wallet_balance(sol_client, wallet))
