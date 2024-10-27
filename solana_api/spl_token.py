import os

import base58
from dotenv import load_dotenv
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.token.associated import get_associated_token_address


async def get_token_balance(client: AsyncClient, wallet: Keypair, token_ca: str) -> int:
    token_mint_pubkey = Pubkey.from_string(token_ca)
    # Get associated token account for wallet and token mint
    token_account = get_associated_token_address(wallet.pubkey(), token_mint_pubkey)

    # Fetch the balance of the associated token account
    response = await client.get_token_account_balance(token_account, commitment=Confirmed)

    balance = int(response.value.amount)
    print(balance)
    return balance

def format_token_amount(amount: int, decimals: int) -> float:
    """Convert the raw token amount to a human-readable format."""
    return amount / (10 ** decimals)


if __name__ == "__main__":
    load_dotenv()
    SOL_RPC = os.getenv('SOL_RPC')
    # Replace with your own RPC endpoint+
    sol_client = Client(SOL_RPC)
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')

    # Load your wallet using the private key (for testing only)
    private_key = base58.b58decode(PRIVATE_KEY)  # Replace with your base58 private key
    wallet = Keypair.from_bytes(private_key)

    get_token_balance(sol_client, wallet, "4AAmyhuio2bi7wGaPh1W47BD44o2YHrqr4WUSGpSpump")
