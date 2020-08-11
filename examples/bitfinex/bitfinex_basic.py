import asyncio
import logging
from datetime import datetime

from ssc2ce import Bitfinex

conn = Bitfinex()

logging.basicConfig(
    format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s',
    level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")


def time_to_str(t: float) -> str:
    return datetime.utcfromtimestamp(t).isoformat()


def handle_book_btc_usd(data):
    print(time_to_str(conn.receipt_time), "book", data)
    pass


def handle_trades_btc_usd(data):
    print(time_to_str(conn.receipt_time), "trades", data)
    pass

def handle_other(data):
    print("handle_other", time_to_str(conn.receipt_time), data)


async def subscribe():
    await conn.subscribe_book("tETHUSD", handler=handle_book_btc_usd)
    await conn.subscribe_trades("tETHUSD", handler=handle_trades_btc_usd)


conn.on_connect_ws = subscribe
conn.handle_message = handle_other

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
