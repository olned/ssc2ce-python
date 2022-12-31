#!/usr/bin/env python
import asyncio
import logging

from ssc2ce import Coinbase

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")


def handle_message(message: str):
    logger.info(message)


conn = Coinbase()
conn.on_message = handle_message


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


def handle_heartbeat(data: dict) -> bool:
    logger.info(f"{repr(data)}")
    return True


conn.on_connect_ws = subscribe


def stop():
    asyncio.ensure_future(conn.stop())


loop = asyncio.get_event_loop()
loop.call_later(3600, stop)

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    logger.info("Application closed by KeyboardInterrupt.")
