import logging
from datetime import datetime
from typing import Optional, Tuple, List

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.rpc.responses import GetTransactionResp
from solders.transaction_status import EncodedTransactionWithStatusMeta

from constants import PUMP_DOT_FUN_ID
from solana_api.trade_model import Trade


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
    try:
        block = await client.get_block(slot, max_supported_transaction_version=0)
        return block.value.block_time, block.value.transactions
    except Exception as e:
        logging.error("Failed to load block", e)
        return 0, []


async def get_user_trades_in_block(user: Pubkey, slot: int, rpc: str) -> List[Trade]:
    trades = list()
    try:
        client = AsyncClient(rpc)
        block_time, tx_list = await get_block_transactions(client, slot)
        for tx in tx_list:
            trade = get_user_trade(user, tx, block_time)
            if trade is not None:
                trades.append(trade)
        return trades
    except Exception as e:
        logging.error("Failed to load trades", e)
        return trades


def get_user_trade(user: Pubkey, tx: EncodedTransactionWithStatusMeta, block_time: int) -> Optional[Trade]:
    try:
        if not is_user_trade(tx, user):
            return None

        if not (is_raydium_trade(tx) or is_raydium_trade(tx)):
            return None

        sol_amount = get_sol_change(tx, user)
        token, token_amount, token_holding_after = get_token_change(tx, user)

        return Trade(str(user), token, token_amount, sol_amount, sol_amount < 0, token_holding_after,
                     block_time_stamp_to_datetime(block_time))
    except Exception as e:
        logging.error("Failed to load trades", e)
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
        if balance.owner == user
    ]
    user_post_balances = [
        balance for balance in tx.meta.post_token_balances
        if balance.owner == user
    ]

    # more than one token involved.
    if len(user_pre_balances) > 1 or len(user_post_balances) > 1:
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
    for log in tx.meta.log_messages:
        if "SwapEvent { dex: RaydiumSwap" in log:
            return True

    return False
