#!/usr/bin/env python
import asyncio
import json
import logging
import sys

from examples.common.book_watcher import BookWatcher
from ssc2ce import Deribit, create_parser

conn = Deribit()
parser = create_parser(exchange="deribit", is_cpp=len(sys.argv) > 1 and "cpp" in sys.argv)
watcher = BookWatcher(parser)
conn.on_message = parser.parse

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
