#!/usr/bin/env python
import asyncio
import logging
from ssc2ce import Coinbase

conn = Coinbase(sandbox=False)

pending = {}

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("deribit-writer")


async def subscribe_books():
    await conn.ws.send_json({
        "type": "subscribe",
        "product_ids": ["BTC-EUR"],
        "channels": [
            "level2",
            "heartbeat"
        ]
    })


output = open("coinbase_dump.jsonl", "w")


def dump(msg: str):
    output.write(msg)
    output.write('\n')


def stop():
    asyncio.ensure_future(conn.ws.close())


conn.on_before_handling = dump
conn.on_connect_ws = subscribe_books

loop = asyncio.get_event_loop()
loop.call_later(3600, stop)

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
