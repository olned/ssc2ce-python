#!/usr/bin/env python
import asyncio
import logging

from ssc2ce import Bitfinex

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("ons-derobit-ws-python-sample")

conn = Bitfinex()


async def handle_subscription(data):
    print(data)


async def subscribe():
    await conn.subscribe({
        "channel": "ticker",
        "symbol": "tBTCUSD"
    }, handler=handle_subscription)


conn.on_connect_ws = subscribe

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
