import asyncio
import datetime
import os

import base58
from dotenv import load_dotenv
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair

from log import logger
from solana_api.data_parser import extract_data
from solana_api.jupiter_api import buy_token, get_quote, sell_token
from solana_api.spl_token import get_token_balance, format_token_amount
from solana_api.wallet_data import get_wallet_balance

DUMP_WAIT_TIME = 43200

async def new_call_incoming(message, client: AsyncClient, wallet: Keypair):
    logger.info("Incoming message received for processing.")

    ca, mc = extract_data(message)
    if ca is None:
        logger.warning("No valid CA found in the message. Exiting.")
        return

    # Get wallet SOL balance
    sol_balance = await get_wallet_balance(client, wallet)
    logger.info(f"Wallet SOL balance retrieved: {sol_balance / 1e9} SOL")

    # Calculate 10% of SOL balance to use for buying
    sol_amount_to_use = int(sol_balance * 0.1)  # in lamports
    if sol_amount_to_use <= 50000000:
        logger.info("Insufficient SOL balance to buy token. Minimum required is 0.05 SOL.")
        return

    logger.info(f"Using {sol_amount_to_use / 1e9} SOL (10% of balance) to buy token: {ca}")

    # Start to buy, watch, and sell
    asyncio.create_task(trade_runner(client, wallet, ca, sol_amount_to_use))
    logger.info(f"Trade runner started for token: {ca} with amount: {sol_amount_to_use} lamports.")


async def trade_runner(client: AsyncClient, wallet: Keypair, token_ca: str, amount: int):
    try:
        logger.info("Starting trade runner for token %s with amount %d", token_ca, amount)

        # Step 1: Buy token
        buy_success = await buy_token(client, wallet, token_ca, amount)
        if not buy_success:
            logger.error("Failed to buy token %s.", token_ca)
            return

        await asyncio.sleep(2)

        # Step 2: Get bought token balance
        amount_bought = await get_token_balance(client, wallet, token_ca)
        if amount_bought == 0:
            logger.error("No tokens bought for %s.", token_ca)
            return
        logger.info("%s Tokens bought for %s", amount_bought, token_ca)

        bought_time = datetime.datetime.now()

        while True:
            await asyncio.sleep(10)
            logger.info("Fetching sell quote for %s.", token_ca)

            # Step 3: Get sell quote to convert the tokens back to SOL
            sell_quote = await get_quote(token_ca, amount_bought, False)
            if sell_quote is None or len(sell_quote.get('outAmount', [])) == 0:
                logger.error("Failed to get sell quote for token %s.", token_ca)
                return

            sell_amount = int(sell_quote['outAmount'])  # Amount received after selling tokens

            # Step 4: Calculate returns
            trade_return = sell_amount - amount  # Net profit or loss
            return_percentage = (trade_return / amount) * 100 if amount != 0 else 0

            logger.info("Current return percentage for %s: %.2f%%", token_ca, return_percentage)

            # Step 5: Check conditions for selling
            if return_percentage > 120 or return_percentage < -45 or (
                    datetime.datetime.now() - bought_time).total_seconds() > DUMP_WAIT_TIME:
                logger.info("Conditions met for selling %s. Selling...", token_ca)
                sell_success = await sell_token(client, wallet, token_ca, amount_bought)
                if sell_success:
                    logger.info("Successfully sold %s.", token_ca)
                else:
                    logger.error("Failed to sell token %s.", token_ca)
                return

    except Exception as e:
        logger.error("An unexpected error occurred in trade_runner: %s", str(e))


if __name__ == "__main__":
    load_dotenv()
    SOL_RPC = os.getenv('SOL_RPC')
    # Replace with your own RPC endpoint+
    sol_client = AsyncClient(SOL_RPC)
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')

    # Load your wallet using the private key (for testing only)
    private_key = base58.b58decode(PRIVATE_KEY)  # Replace with your base58 private key
    wallet = Keypair.from_bytes(private_key)

    asyncio.run(trade_runner(sol_client, wallet, "4AAmyhuio2bi7wGaPh1W47BD44o2YHrqr4WUSGpSpump", 1000000))
