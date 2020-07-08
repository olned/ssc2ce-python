#!/usr/bin/env python
import asyncio
import logging
from datetime import datetime

from ssc2ce import Bitfinex
from ssc2ce.bitfinex.enums import ConfigFlag

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")

conn = Bitfinex(ConfigFlag.TIMESTAMP | ConfigFlag.SEQ_ALL | ConfigFlag.OB_CHECKSUM)


# ConfigFlag.TIMESTAMP | ConfigFlag.SEQ_ALL

async def subscribe():
    # await conn.subscribe_ticker("tBTCUSD")
    await conn.subscribe_book("tBTCUSD")
    # await conn.subscribe_trades("tBTCUSD")
    # await conn.subscribe_candles("tBTCUSD")
    # await conn.subscribe_raw_book("tBTCUSD")
    # await conn.subscribe_ticker("fUSD")
    # await conn.subscribe_book("fUSD")
    # await conn.subscribe_trades("fUSD")


start_at = "{0:%Y_%m_%d_%H_%M_%S}".format(datetime.utcnow())
f = open(f"../bitfinex_dump_flag_{conn.flags}-{start_at}.jsonl", "w")


def dump_it(message: str):
    f.write(message + '\n')


conn.on_connect_ws = subscribe
conn.on_before_handling = dump_it


def stop():
    asyncio.ensure_future(conn.stop())


def reset_config():
    asyncio.ensure_future(conn.configure(ConfigFlag))


def set_config_1():
    asyncio.ensure_future(conn.configure(ConfigFlag.TIMESTAMP))


def set_config_2():
    asyncio.ensure_future(conn.configure(ConfigFlag.TIMESTAMP | ConfigFlag.OB_CHECKSUM))


def set_config_3():
    asyncio.ensure_future(conn.configure(ConfigFlag.TIMESTAMP | ConfigFlag.SEQ_ALL | ConfigFlag.OB_CHECKSUM))


loop = asyncio.get_event_loop()
# loop.call_later(30, reset_config)
# loop.call_later(60, set_config_1)
# loop.call_later(90, set_config_2)
# loop.call_later(120, set_config_3)
loop.call_later(3600, stop)

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
