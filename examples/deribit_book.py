#!/usr/bin/env python
import asyncio
import json
import logging

from examples.book_watcher import BookWatcher
from ssc2ce import Deribit

from ssc2ce.deribit.parser import DeribitParser

conn = Deribit()
parser = DeribitParser(conn)
conn.on_message = parser.parse
watcher = BookWatcher(parser)

pending = {}
instruments = []

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger("deribit-book")


async def handle_instruments(data: dict):
    request_id = data["id"]
    del pending[request_id]
    print(json.dumps(data))
    if not pending:
        await conn.send_public(request={
            "method": "public/subscribe",
            "params": {
                "channels": [f"book.{i}.raw" for i in instruments]
            }
        })


async def handle_currencies(data: dict):
    for currency in data["result"]:
        symbol = currency["currency"]
        instruments.append(symbol + "-PERPETUAL")
        request_id = await conn.get_instruments(symbol, kind="future", callback=handle_instruments)
        pending[request_id] = symbol


async def get_currencies():
    await conn.get_currencies(handle_currencies)


conn.on_connect_ws = get_currencies

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
