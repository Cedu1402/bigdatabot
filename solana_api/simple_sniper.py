import asyncio

from anchorpy import Wallet
from solana.rpc.api import Client

from main import logger
from solana_api.data_parser import extract_data
from solana_api.wallet_data import get_wallet_balance


async def new_call_incoming(message, wallet: Wallet, client: Client):
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
    asyncio.create_task(trade_runner(ca, sol_amount_to_use, wallet, client))
    logger.info(f"Trade runner started for token: {ca} with amount: {sol_amount_to_use} lamports.")


def trade_runner(ca: str, amount: int, wallet: Wallet, client: Client):
    pass
