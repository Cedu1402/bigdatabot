from base64 import b64decode

import requests
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.message import to_bytes_versioned
from solders.transaction import VersionedTransaction

# Mint address for SOL token
SOL_MINT = 'So11111111111111111111111111111111111111112'


def buy_token(client: Client, wallet: Keypair,token: str, amount: int):
    """Swaps SOL for the specified token."""
    return swap_tokens(client, wallet, token, amount, buy=True)


def sell_token(client: Client, wallet: Keypair,token: str, amount: int):
    """Swaps the specified token for SOL."""
    return swap_tokens(client, wallet, token, amount, buy=False)


def get_quote(token: str, amount: int, buy: bool):
    url = 'https://quote-api.jup.ag/v6/quote'
    params = {
        'inputMint': SOL_MINT if buy else token,
        'outputMint': token if buy else SOL_MINT,
        'amount': amount,  # Amount in lamports (0.1 SOL)
        'slippageBps': 100,  # Slippage in basis points (0.5%)
    }

    response = requests.get(url, params=params)
    return response.json()


def swap_tokens(client: Client, wallet: Keypair, token: str, amount: int, buy: bool) -> object:
    quote_response = get_quote(token, amount, buy)

    # Create swap transaction
    swap_url = 'https://quote-api.jup.ag/v6/swap'
    swap_response = requests.post(swap_url, json={
        'quoteResponse': quote_response,
        'userPublicKey': str(wallet.pubkey()),
        'wrapAndUnwrapSol': True,
    })

    swap_data = swap_response.json()

    # Step 3: Decode and deserialize the base64 transaction
    swap_transaction_b64 = swap_data.get('swapTransaction')

    # Decode from base64
    swap_transaction_buf = b64decode(swap_transaction_b64)

    # Deserialize into a Transaction object
    raw_tx = VersionedTransaction.from_bytes(bytes(swap_transaction_buf))
    signature = wallet.sign_message(to_bytes_versioned(raw_tx.message))
    signed_tx = VersionedTransaction.populate(raw_tx.message, [signature])

    # Step 5: Send the transaction
    txid = client.send_transaction(signed_tx, opts=TxOpts(skip_preflight=True))
    print(f'Transaction sent: {txid}')
    return True


if __name__ == "__main__":
    pass
    #
    # swap_tokens()
