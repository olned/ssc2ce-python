import asyncio
from datetime import datetime

from ssc2ce import Bitfinex

conn = Bitfinex()


def time_to_str(t: float) -> str:
    return datetime.utcfromtimestamp(t).isoformat()


def handle_book_btc_usd(data):
    print(time_to_str(conn.receipt_time), "book", data)
    pass


def handle_trades_btc_usd(data):
    print(time_to_str(conn.receipt_time), "trades", data)


async def subscribe():
    await conn.subscribe_book("tBTCUSD", handler=handle_book_btc_usd)
    await conn.subscribe_trades("tBTCUSD", handler=handle_trades_btc_usd)


conn.on_connect_ws = subscribe

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
