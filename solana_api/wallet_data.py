from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair


async def get_wallet_balance(client: AsyncClient, wallet: Keypair):
    """Fetches the wallet balance in lamports (1 SOL = 1e9 lamports)."""
    balance_result = await client.get_balance(wallet.pubkey())
    balance = balance_result['result']['value']
    return balance

