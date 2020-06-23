#!/usr/bin/env python
import asyncio
import logging

from ssc2ce import Bitfinex

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")

conn = Bitfinex()


def handle_subscription(data, self):
    print(data, self.receipt_time * 1000 - data[-1])


async def subscribe():
    await conn.subscribe({
        "channel": "ticker",
        "symbol": "tBTCUSD"
    }, handler=handle_subscription)


conn.on_connect_ws = subscribe


def stop():
    asyncio.ensure_future(conn.stop())


loop = asyncio.get_event_loop()
loop.call_later(3600, stop)

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
