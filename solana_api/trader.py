import logging
from asyncio import sleep
from datetime import datetime
from typing import Optional, Tuple

import base58
import redis.asyncio
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.signature import Signature

from constants import INVESTMENT_AMOUNT, SOL_RPC, PRIVATE_KEY
from data.data_format import get_sol_price
from data.redis_helper import get_async_redis
from env_data.get_env_value import get_env_value
from solana_api.jupiter_api import get_quote, get_token_price, swap_from_quote, get_price_in_usd_buy
from solana_api.solana_data import get_transaction
from solana_api.spl_token import get_token_balance

logger = logging.getLogger(__name__)


async def wait_for_tx_confirmed(client: AsyncClient, tx_id: str, max_wait_time: int) -> bool:
    start_time = datetime.now()

    while True:
        try:
            if (datetime.now() - start_time).total_seconds() > max_wait_time:
                logger.info("Transaction timed out.", extra={'tx_id': tx_id})
                return False

            tx = await get_transaction(client, Signature.from_string(tx_id))
            if tx is None:
                await sleep(5)
                continue

            if tx.transaction.meta.err is not None:
                logger.info("Transaction failed.", extra={'tx_id': tx_id})
                return False

            logger.info("Transaction confirmed.", extra={'tx_id': tx_id})
            return True

        except Exception:
            logger.exception("Wait for tx confirmation failed")
            await sleep(5)


def setup_buy() -> Tuple[AsyncClient, Keypair, redis.asyncio.Redis]:
    rpc = get_env_value(SOL_RPC)
    sol_client = AsyncClient(rpc)
    private_key = get_env_value(PRIVATE_KEY)
    private_key = base58.b58decode(private_key)
    wallet = Keypair.from_bytes(private_key)
    r = get_async_redis()

    return sol_client, wallet, r


async def execute_buy(start_time: datetime,
                      max_retry_time: int,
                      token: str,
                      sol_to_invest: float,
                      start_price_api: int,
                      sol_client: AsyncClient,
                      wallet: Keypair,
                      current_sol_price: float,
                      max_higher_price: int,
                      start_price: Optional[int],
                      real_money_mode: bool) -> Tuple[Optional[int], Optional[int]]:
    try:
        if (datetime.now() - start_time).seconds > max_retry_time:
            return -1, start_price

        logger.info("Fetching quote for token", extra={"token": token, "sol_to_invest": sol_to_invest})
        sol_to_invest_raw = int(sol_to_invest * (10 ** 9))
        quote_response = await get_quote(token, sol_to_invest_raw, True)
        if quote_response is None:
            logger.error("Failed to fetch quote", extra={'token': token})
            return None, start_price_api

        if start_price is None:
            start_price = get_price_in_usd_buy(quote_response, sol_to_invest_raw, current_sol_price)

        current_price = get_price_in_usd_buy(quote_response, sol_to_invest_raw, current_sol_price)
        if not real_money_mode:
            return int(quote_response.get('outAmount', 0)), current_price

        percentage_change = ((current_price - start_price) / start_price) * 100

        if percentage_change > max_higher_price:
            logger.error("Buy failed token price above limit", extra={'token': token})
            return -1, start_price

        # time to buy
        tx_id = await swap_from_quote(sol_client, wallet, quote_response)
        if tx_id is None:
            return None, start_price

        # check tx success
        tx_okay = await wait_for_tx_confirmed(sol_client, tx_id, 35)
        if not tx_okay:
            return None, start_price

        amount_bought = await get_token_balance(sol_client, wallet, token, 60, 10)
        if amount_bought == 0:
            logger.error("No balance found for token", extra={'token': token})
            return -1, start_price

        return int(amount_bought), start_price

    except Exception:
        logger.exception("Failed to execute buy.", extra={'token': token})
        return None, start_price


async def buy_token(token: str, max_retry_time: int, max_higher_price: int, real_money_mode: bool) -> Tuple[
    Optional[int], Optional[int]]:
    try:
        sol_client, wallet, r = setup_buy()
        start_time = datetime.now()

        current_sol_price = await get_sol_price(r)
        sol_to_invest = INVESTMENT_AMOUNT / current_sol_price

        logger.info("Calculated sol to invest", extra={"sol_to_invest": sol_to_invest})
        start_price_api = await get_token_price(token)
        start_price = None

        while True:
            buy_amount, start_price = await execute_buy(start_time, max_retry_time, token, sol_to_invest,
                                                        start_price_api * (10 ** 6), sol_client, wallet,
                                                        current_sol_price, max_higher_price, start_price,
                                                        real_money_mode)
            if buy_amount is None:
                await sleep(5)
                continue

            if buy_amount == -1:
                return None, None

            return buy_amount, start_price

    except Exception as e:
        logger.exception("Failed to buy token", extra={"token": token})
        return None, None


async def execute_sell(token: str, amount: int, sol_client: AsyncClient, wallet: Keypair,
                       quote_response: Optional[dict], slippage: Optional[int]) -> bool:
    try:
        if quote_response is None:
            quote_response = await get_quote(token, amount, False, slippage)
            if quote_response is None:
                logger.error("Failed to fetch quote", extra={'token': token})
                return False

        tx_id = await swap_from_quote(sol_client, wallet, quote_response)
        if tx_id is None:
            logger.error("Failed to send swap sell tx", extra={'token': token})
            return False

        tx_okay = await wait_for_tx_confirmed(sol_client, tx_id, 35)
        if not tx_okay:
            logger.error("Transaction failed or skipped", extra={'token': token, 'tx_id': tx_id})
            return False

        return True

    except Exception:
        logger.exception("Failed to execute sell.", extra={'token': token})
        return False


async def sell_token(token: str, amount: int, max_retry_time: int, quote: dict, is_profit: bool) -> bool:
    sol_client, wallet, _ = setup_buy()
    start_time = datetime.now()
    slippage = 1000
    while True:
        if (start_time - datetime.now()).total_seconds() > max_retry_time:
            logger.error("Failed to sell token in time", extra={'token': token, 'time': max_retry_time})
            return False

        sell_success = await execute_sell(token, amount, sol_client, wallet, quote, slippage)
        if not sell_success:
            logger.info("Failed to sell token", extra={'token': token})
            
            if is_profit:
                return False
            else:
                slippage = 1000 * 2 if slippage < 6000 else 6000  # higher slippage when selling to 60% avoiding issue when coin nukes hard to not be able to sell anymore.

            await sleep(5)
        else:
            logger.info("Sold token in time", extra={'token': token})
            return sell_success
