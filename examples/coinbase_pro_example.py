#!/usr/bin/env python
import asyncio
import logging

from examples.book_watcher import BookWatcher
from ssc2ce import Coinbase, CoinbaseParser

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")

conn = Coinbase()
parser = CoinbaseParser()
watcher = BookWatcher(parser)
conn.on_message = parser.parse


async def subscribe():
    await conn.ws.send_json({
        "type": "subscribe",
        "product_ids": [
            "BTC-USD",
            "ETH-BTC"
        ],
        "channels": [
            "level2",
            "heartbeat"
        ]
    })


def handle_subscriptions(data: dict) -> bool:
    print("subscriptions", data["channels"])
    return True


last_time: str = None


def handle_heartbeat(data: dict) -> bool:
    global last_time
    last_time = data["time"]
    return True


conn.on_connect_ws = subscribe
parser.set_on_heartbeat(handle_heartbeat)
parser.set_on_subscriptions(handle_subscriptions)


def stop():
    asyncio.ensure_future(conn.stop())


loop = asyncio.get_event_loop()
loop.call_later(3600, stop)

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")

print(last_time)
