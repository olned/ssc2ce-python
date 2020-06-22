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

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger("deribit-book")


async def subscribe_book():
    await conn.send_public(request={
        "method": "public/subscribe",
        "params": {
            "channels": [f"book.BTC-PERPETUAL.raw"]
        }
    })


output = open("../../ssc2ce/tests/deribit_dump_test.txt", "w")


def dump(msg: str):
    output.write(msg)
    output.write('\n')


conn.on_connect_ws = subscribe_book
conn.on_before_handling = dump
loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
