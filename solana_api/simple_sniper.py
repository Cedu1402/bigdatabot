import asyncio
import os

import base58
from dotenv import load_dotenv
from solana.rpc.api import Client
from solders.keypair import Keypair

from log import logger
from solana_api.data_parser import extract_data
from solana_api.jupiter_api import buy_token, get_quote, sell_token
from solana_api.spl_token import get_token_balance
from solana_api.wallet_data import get_wallet_balance


async def new_call_incoming(message, client: Client, wallet: Keypair):
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


async def trade_runner(client: Client, wallet: Keypair, token_ca: str, amount: int):
    buy_success = buy_token(client, wallet, token_ca, amount)
    if not buy_success:
        return

    amount_bought = get_token_balance(client, wallet, token_ca)
    if amount_bought == 0:
        return

    while True:
        await asyncio.sleep(10)
        sell_quote = get_quote(token_ca, amount_bought, False)

        # Step 3: Get sell quote to convert the tokens back to SOL
        if sell_quote is None or len(sell_quote['outAmount']) == 0:
            print("Error: Failed to get sell quote.")
            return

        sell_amount = int(sell_quote['outAmount'])  # Amount received after selling tokens

        trade_return = sell_amount - amount  # Net profit or loss
        return_percentage = (trade_return / amount) * 100 if amount != 0 else 0

        if return_percentage > 120  or return_percentage < -45:
            sell_token(client, wallet, token_ca, amount_bought)
            return


if __name__ == "__main__":
    load_dotenv()
    SOL_RPC = os.getenv('SOL_RPC')
    # Replace with your own RPC endpoint+
    sol_client = Client(SOL_RPC)
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')

    # Load your wallet using the private key (for testing only)
    private_key = base58.b58decode(PRIVATE_KEY)  # Replace with your base58 private key
    wallet = Keypair.from_bytes(private_key)

    asyncio.run(trade_runner(sol_client, wallet, "4AAmyhuio2bi7wGaPh1W47BD44o2YHrqr4WUSGpSpump", 1000000))
