from solana.rpc.api import Client
from solders.keypair import Keypair


def get_wallet_balance(client: Client, wallet: Keypair):
    """Fetches the wallet balance in lamports (1 SOL = 1e9 lamports)."""
    balance = client.get_balance(wallet.pubkey())['result']['value']
    return balance

