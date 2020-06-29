#!/usr/bin/env python
import asyncio
import json
import logging
import sys
from datetime import datetime

from examples.common.book_watcher import BookWatcher
from ssc2ce import Deribit, create_parser

conn = Deribit()
parser = create_parser(exchange="deribit", is_cpp=len(sys.argv) > 1 and "cpp" in sys.argv)
watcher = BookWatcher(parser)
conn.on_message = parser.parse

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("deribit-book")

instrument = "BTC-PERPETUAL"


async def subscribe_book():
    await conn.send_public(request={
        "method": "public/subscribe",
        "params": {
            "channels": [f"book.{instrument}.raw"]
        }
    })


start_at = "{0:%Y_%m_%d_%H_%M_%S}".format(datetime.utcnow())
output = open(f"../deribit_dump-{instrument}-{start_at}.jsonl", "w")


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
