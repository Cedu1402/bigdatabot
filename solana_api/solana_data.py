import logging
from asyncio import sleep
from datetime import datetime
from typing import Optional, Tuple, List

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Finalized
from solders.pubkey import Pubkey
from solders.rpc.responses import GetTransactionResp, RpcConfirmedTransactionStatusWithSignature
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, EncodedConfirmedTransactionWithStatusMeta

from constants import PUMP_DOT_FUN_ID
from database.event_table import signature_exists
from dto.trade_model import Trade

logger = logging.getLogger(__name__)


async def get_recent_signature(client: AsyncClient, account: Pubkey) -> RpcConfirmedTransactionStatusWithSignature:
    try:
        response = await client.get_signatures_for_address(account, limit=1, commitment=Finalized)
        return response.value[0]
    except Exception as e:
        logger.exception("Failed to get recent signature", extra={"trader": str(account)})


async def get_transaction(client: AsyncClient,
                          signature: Signature) -> EncodedConfirmedTransactionWithStatusMeta:
    try:
        response = await client.get_transaction(signature,
                                                max_supported_transaction_version=0,
                                                commitment=Finalized)
        return response.value
    except Exception as e:
        logger.exception("Failed to get recent signature", extra={"signature": str(signature)})


def block_time_stamp_to_datetime(timestamp: int) -> datetime:
    return datetime.utcfromtimestamp(timestamp)


def transform_to_encoded_transaction_with_status_meta(tx: GetTransactionResp):
    # Extract the fields
    transaction_data = tx.value.transaction.transaction
    meta_data = tx.value.transaction.meta

    # Construct EncodedTransactionWithStatusMeta
    encoded_tx_with_meta = EncodedTransactionWithStatusMeta(
        transaction=transaction_data,  # Base64 encoded transaction
        meta=meta_data,  # Metadata (status, fee, etc.),
        version=tx.value.transaction.version
    )

    return encoded_tx_with_meta


async def get_block_transactions(client: AsyncClient, slot: int) -> Optional[
    Tuple[int, List[EncodedTransactionWithStatusMeta]]]:
    retries = 0
    max_retries = 10
    while retries < max_retries:
        try:
            block = await client.get_block(slot, max_supported_transaction_version=0)
            return block.value.block_time, block.value.transactions
        except Exception as e:
            logger.exception("Failed to load block", extra={"slot": slot})
            retries += 1
            await sleep(20)

    return 0, []


async def get_latest_user_trade(user: Pubkey, rpc: str) -> Optional[Trade]:
    try:
        async with AsyncClient(rpc) as client:
            latest_signature = await get_recent_signature(client, user)
            logger.info("Check latest signature of trader", extra={"trader": str(user),
                                                                   "signature": str(latest_signature.signature)})
            if latest_signature.err is not None:
                logger.info("Skip failed transaction", extra={"trader": str(user),
                                                              "signature": str(latest_signature.signature)})
                return None

            already_done = signature_exists(str(latest_signature.signature))
            if already_done == str(latest_signature.signature):
                logger.info("Latest signature already checked", extra={"trader": str(user),
                                                                       "signature": str(latest_signature.signature)})
                return None

            logger.info("Get tx for signature", extra={"signature": str(latest_signature.signature)})
            tx = await get_transaction(client, latest_signature.signature)
            if tx is None:
                logger.warning("Failed to load tx data", extra={"signature": str(latest_signature.signature)})

            logger.info("Check tx for trades", extra={"signature": str(latest_signature.signature)})
            trade = get_user_trade(user, tx.transaction, tx.block_time)

            return trade
    except Exception as e:
        logger.exception("Failed to load latest user trade")


async def get_user_trades_in_block(user: Pubkey, slot: int, rpc: str) -> List[Trade]:
    trades = list()
    try:
        async with AsyncClient(rpc) as client:
            block_time, tx_list = await get_block_transactions(client, slot)
            logger.info("Loaded block details", extra={"slot": slot})
            for tx in tx_list:
                trade = get_user_trade(user, tx, block_time)
                if trade is not None:
                    trades.append(trade)
                    logger.info("found trades in block", extra={"slot": slot})
            return trades
    except Exception as e:
        logger.exception("Failed to load trades", extra={"trader": str(user)})
        return trades


def get_user_trade(user: Pubkey, tx: EncodedTransactionWithStatusMeta, block_time: int) -> Optional[Trade]:
    try:
        if not is_user_trade(tx, user):
            return None

        if not (is_pump_fun_trade(tx) or is_raydium_trade(tx)):
            return None

        sol_amount = get_sol_change(tx, user)
        token_data = get_token_change(tx, user)
        if token_data is None:
            return None

        token, token_amount, token_holding_after = token_data

        return Trade(str(user), str(token), token_amount, sol_amount, sol_amount < 0, token_holding_after,
                     block_time_stamp_to_datetime(block_time).isoformat(), str(tx.transaction.signatures[0]))
    except Exception as e:
        logger.exception("Failed to load trades", extra={"trader": str(user)})
        return None


def get_index_of_account(account_keys: List[Pubkey], account: Pubkey) -> Optional[int]:
    items = [index for index, account_key in enumerate(account_keys) if account_key == account]
    if len(items) == 0:
        return None
    return items[0]


def get_sol_change(tx: EncodedTransactionWithStatusMeta, user: Pubkey) -> Optional[int]:
    index = get_index_of_account(tx.transaction.message.account_keys, user)
    pre_sol_balance = tx.meta.pre_balances[index]
    post_sol_balance = tx.meta.post_balances[index]

    change_sol = int(post_sol_balance) - int(pre_sol_balance)
    return change_sol


def get_token_change(tx: EncodedTransactionWithStatusMeta, user: Pubkey) -> Optional[Tuple[Pubkey, int, int]]:
    user_pre_balances = [
        balance for balance in tx.meta.pre_token_balances
        if balance.owner == user and str(balance.mint) != 'So11111111111111111111111111111111111111112'
    ]
    user_post_balances = [
        balance for balance in tx.meta.post_token_balances
        if balance.owner == user and str(balance.mint) != 'So11111111111111111111111111111111111111112'
    ]

    # more than one token involved.
    if len(user_pre_balances) > 1 or len(user_post_balances) > 1:
        logger.info(f"Multihop token swap skipped", extra={"tx": str(tx.transaction.signatures[0])})
        return None

    if len(user_post_balances) == 0 and len(user_pre_balances) == 0:
        logger.info(f"No tokens found", extra={"tx": str(tx.transaction.signatures[0])})
        return None

    post_balance = user_post_balances[0].ui_token_amount.amount if len(user_post_balances) == 1 else 0
    pre_balance = user_pre_balances[0].ui_token_amount.amount if len(user_pre_balances) == 1 else 0
    change = int(post_balance) - int(pre_balance)
    token = user_post_balances[0].mint if len(user_post_balances) == 1 else user_pre_balances[0].mint

    return token, change, int(post_balance)


def is_user_trade(tx: EncodedTransactionWithStatusMeta, user: Pubkey) -> bool:
    return len([0 for item in tx.transaction.message.account_keys if
                item == user]) > 0


def is_pump_fun_trade(tx: EncodedTransactionWithStatusMeta) -> bool:
    if len([0 for item in tx.transaction.message.account_keys if
            item == Pubkey.from_string(PUMP_DOT_FUN_ID)]) == 0:
        return False

    for index, log in enumerate(tx.meta.log_messages):
        if "Instruction: Buy" in log and PUMP_DOT_FUN_ID in tx.meta.log_messages[index - 1]:
            return True
        if "Instruction: Sell" in log and PUMP_DOT_FUN_ID in tx.meta.log_messages[index - 1]:
            return True

    return False


def is_raydium_trade(tx: EncodedTransactionWithStatusMeta) -> bool:
    if (Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8") in tx.transaction.message.account_keys or
            Pubkey.from_string(
                "5qucFmuXKGX1SLwNT5YXrFUnhAicELNkfup9dCFu4Xe") in tx.transaction.message.account_keys):
        return True

    for log in tx.meta.log_messages:
        if ("SwapEvent { dex: RaydiumSwap" in log or "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8" in log or
                "5qucFmuXKGX1SLwNT5YXrFUnhAicELNkfup9dCFu4Xe" in log):
            return True

    return False
