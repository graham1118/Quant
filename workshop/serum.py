import asyncio
from pyserum.async_connection import async_conn
from pyserum.market import AsyncMarket


async def main():
    market_address = "5LgJphS6D5zXwUVPU7eCryDBkyta3AidrJ5vjNU6BcGW"  # Address for BTC/USDC
    async with async_conn("https://solana-api.projectserum.com") as cc:
        # Load the given market
        market = await AsyncMarket.load(cc, market_address)
        asks = await market.load_asks()
        # Show all current ask order
        print("Ask Orders:")
        for ask in asks:
            print(f"Order id: {ask.order_id}, price: {ask.info.price}, size: {ask.info.size}.")
        print("\n")
        # Show all current bid order
        print("Bid Orders:")
        bids = await market.load_bids()
        for bid in bids:
            print(f"Order id: {bid.order_id}, price: {bid.info.price}, size: {bid.info.size}.")


asyncio.run(main())