import logging
from typing import Optional, Tuple, List

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.rpc.responses import GetTransactionResp
from solders.transaction_status import EncodedTransactionWithStatusMeta

from constants import PUMP_DOT_FUN_ID
from solana_api.trade_model import Trade


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


async def get_block_transactions(client: AsyncClient, slot: int) -> Optional[list[EncodedTransactionWithStatusMeta]]:
    try:
        block = await client.get_block(slot, max_supported_transaction_version=0)
        return block.value.transactions
    except Exception as e:
        logging.error("Failed to load block", e)
        return []


def get_user_trades_in_block(client: AsyncClient, tx_list: List[str]) -> Optional[List[Trade]]:
    pass


async def get_user_trade(user: Pubkey, tx: EncodedTransactionWithStatusMeta) -> Optional[Trade]:
    if not is_user_trade(tx, user):
        return None

    if not (is_raydium_trade(tx) or is_raydium_trade(tx)):
        return None

    sol_amount = get_sol_change(tx, user)
    token, token_amount, token_holding_after = get_token_change(tx, user)

    return Trade(token, token_amount, sol_amount, sol_amount > 0, token_holding_after)


def get_index_of_account(account_keys: List[Pubkey], account: Pubkey) -> Optional[int]:
    items = [index for index, account_key in enumerate(account_keys) if account_key == account]
    if len(items) == 0:
        return None
    return items[0]


def get_sol_change(tx: EncodedTransactionWithStatusMeta, user: Pubkey) -> Optional[float]:
    index = get_index_of_account(tx.transaction.message.account_keys, user)
    pre_sol_balance = tx.meta.pre_balances[index]
    post_sol_balance = tx.meta.post_balances[index]

    change_sol = post_sol_balance - pre_sol_balance
    return change_sol


def get_token_change(tx: EncodedTransactionWithStatusMeta, user: Pubkey) -> Optional[Tuple[Pubkey, float, float]]:
    index = get_index_of_account(tx.transaction.message.account_keys, user)
    
    pass


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
