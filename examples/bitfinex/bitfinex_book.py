#!/usr/bin/env python
import asyncio
import logging

from ssc2ce.bitfinex import Bitfinex
from examples.common.book_watcher import BookWatcher

logging.basicConfig(
    format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s',
    level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")

conn = Bitfinex()
watcher = BookWatcher(conn.parser)


async def subscribe():
    await conn.subscribe_book("tBTCUSD")
    await conn.subscribe_book("tETHUSD")


output = open("bitfinex_dump.cvs", "w")


def dump(msg: str):
    output.write(msg)
    output.write('\n')


def stop():
    asyncio.ensure_future(conn.ws.close())


conn.on_connect_ws = subscribe
conn.on_before_handling = dump
loop = asyncio.get_event_loop()

loop.call_later(3600, stop)

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    loop.run_until_complete(conn.stop())
finally:
    print("Application closed")
