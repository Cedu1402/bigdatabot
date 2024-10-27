import asyncio
import os

from dotenv import load_dotenv
from solana_api.rpc.async_api import AsyncClient
from solana_api.rpc.commitment import Confirmed


async def test_rpc_connection(rpc_url):
    async with AsyncClient(rpc_url, commitment=Confirmed) as client:
        try:
            # Attempt to get the latest block
            response = await client.get_block_height(Confirmed)
            print("Connected to RPC server. Latest block:", response)
        except Exception as e:
            print(f"Failed to connect to RPC server: {e}")

if __name__ == "__main__":
    load_dotenv()
    rpc = os.getenv('SOL_RPC')
    asyncio.run(test_rpc_connection(rpc))