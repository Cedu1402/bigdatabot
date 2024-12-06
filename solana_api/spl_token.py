import asyncio
import os

import base58
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.token.associated import get_associated_token_address

from structure_log.logger_setup import logger


async def get_token_balance(client: AsyncClient, wallet: Keypair, token_ca: str, retries: int = 5,
                            delay: int = 1) -> int:

    for attempt in range(retries):
        balance = 0
        try:
            token_mint_pubkey = Pubkey.from_string(token_ca)
            token_account = get_associated_token_address(wallet.pubkey(), token_mint_pubkey)

            response = await client.get_token_account_balance(token_account, commitment=Confirmed)
            if hasattr(response, "value"):
                balance = int(response.value.amount)

            if balance > 0:
                logger.info("Balance retrieved: %d", balance)
                return balance

            logger.info("Attempt %d: Balance is 0, retrying in %d seconds...", attempt + 1, delay)
        except Exception as e:
            logger.exception("Failed to get token balance")
        finally:
            await asyncio.sleep(delay)

    print("Max retries reached. Balance remains 0.")
    return 0


def format_token_amount(amount: int, decimals: int) -> float:
    """Convert the raw token amount to a human-readable format."""
    return amount / (10 ** decimals)


if __name__ == "__main__":
    load_dotenv()
    SOL_RPC = os.getenv('SOL_RPC')
    # Replace with your own RPC endpoint+
    sol_client = AsyncClient(SOL_RPC)
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')

    # Load your wallet using the private key (for testing only)
    private_key = base58.b58decode(PRIVATE_KEY)  # Replace with your base58 private key
    wallet = Keypair.from_bytes(private_key)

    asyncio.run(get_token_balance(sol_client, wallet, "7XJ8YSjjaVL6fgLQDzSTErLPV8YP5MZ7Z2EVFLfdpump"))
