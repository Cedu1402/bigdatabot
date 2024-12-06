import asyncio
from base64 import b64decode
from typing import Optional, Any

import aiohttp
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.message import to_bytes_versioned
from solders.transaction import VersionedTransaction

from solana_api.http_helper import make_http_request_with_retry
from structure_log.logger_setup import logger

# Mint address for SOL token
SOL_MINT = 'So11111111111111111111111111111111111111112'
RETRY_HTTP = 5
RETRY_TX = 3
RETRY_DELAY = 1


async def get_token_price(token_address: str, show_extra_info: bool = False) -> float:
    url = f'https://api.jup.ag/price/v2'
    params = {
        'ids': token_address,
        'showExtraInfo': str(show_extra_info).lower()
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            response.raise_for_status()  # Ensure the request was successful
            data = await response.json()
            return float(data["data"][token_address]["price"])


async def buy_token(client: AsyncClient, wallet: Keypair, token: str, amount: int):
    """Swaps SOL for the specified token."""
    return await swap_tokens(client, wallet, token, amount, buy=True)


async def sell_token(client: AsyncClient, wallet: Keypair, token: str, amount: int):
    """Swaps the specified token for SOL."""
    return await swap_tokens(client, wallet, token, amount, buy=False)


async def get_quote(token: str, amount: int, buy: bool) -> Optional[Any]:
    url = 'https://quote-api.jup.ag/v6/quote'
    params = {
        'inputMint': SOL_MINT if buy else token,
        'outputMint': token if buy else SOL_MINT,
        'amount': amount,
        'slippageBps': 2000,
    }
    return await make_http_request_with_retry(RETRY_HTTP, RETRY_DELAY, "GET", url, params=params)


async def prepare_tx(quote_response, wallet: Keypair) -> Optional[Any]:
    swap_url = 'https://quote-api.jup.ag/v6/swap'
    params = {
        'quoteResponse': quote_response,
        'userPublicKey': str(wallet.pubkey()),
        'wrapAndUnwrapSol': True,
    }
    return await make_http_request_with_retry(RETRY_HTTP, RETRY_DELAY, "POST", swap_url, json=params)


async def send_transaction_with_retry(client: AsyncClient, signed_tx: VersionedTransaction,
                                      retries: int = 3, delay: float = 2.0) -> Optional[str]:
    """Retries sending a Solana transaction up to `retries` times with a delay on failure.
    Returns the transaction ID if confirmed, otherwise None."""
    for attempt in range(1, retries + 1):
        try:
            logger.info("Attempt %d of %d to send transaction", attempt, retries)
            txid = await client.send_transaction(signed_tx, opts=TxOpts(skip_preflight=True))
            logger.info("Transaction sent successfully on attempt %d: %s", attempt, txid)

            return txid.value.to_json()

        except Exception as e:
            logger.warning("Attempt %d failed with error: %s", attempt, str(e))
            if attempt < retries:
                logger.info("Retrying in %.2f seconds...", delay)
                await asyncio.sleep(delay)


async def swap_tokens(client: AsyncClient, wallet: Keypair, token: str, amount: int, buy: bool) -> bool:
    try:
        # Step 1: Fetch quote
        logger.info("Fetching quote for token %s with amount %d", token, amount)
        quote_response = await get_quote(token, amount, buy)
        if quote_response is None:
            logger.error("Failed to fetch quote.")
            return False

        # Step 2: Create swap transaction
        swap_data = await prepare_tx(quote_response, wallet)
        if swap_data is None:
            logger.error("Failed to get swap data")
            return False

        swap_transaction_b64 = swap_data.get('swapTransaction')
        if not swap_transaction_b64:
            logger.error("No transaction data in response.")
            return False

        # Step 3: Decode and deserialize the base64 transaction
        swap_transaction_buf = b64decode(swap_transaction_b64)
        raw_tx = VersionedTransaction.from_bytes(bytes(swap_transaction_buf))

        # Step 4: Sign the transaction
        signature = wallet.sign_message(to_bytes_versioned(raw_tx.message))
        signed_tx = VersionedTransaction.populate(raw_tx.message, [signature])

        # Step 5: Send the transaction
        logger.info("Sending transaction...")
        txid = await send_transaction_with_retry(client, signed_tx, RETRY_TX, RETRY_DELAY)
        logger.info("Transaction sent successfully: %s", txid)
        return True

    except Exception as e:
        logger.error("An error occurred during token swap: %s", str(e))
        return False


if __name__ == "__main__":
    pass
    #
    # swap_tokens()
