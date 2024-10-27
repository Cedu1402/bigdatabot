from anchorpy import Wallet
from solana.rpc.api import Client


def get_wallet_balance(client: Client, wallet: Wallet):
    """Fetches the wallet balance in lamports (1 SOL = 1e9 lamports)."""
    balance = client.get_balance(wallet.public_key)['result']['value']
    return balance

