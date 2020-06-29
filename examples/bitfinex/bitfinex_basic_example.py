#!/usr/bin/env python
import asyncio
import logging
from datetime import datetime

from ssc2ce import Bitfinex
from ssc2ce.bitfinex.enums import ConfigFlag

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")

conn = Bitfinex(ConfigFlag.TIMESTAMP |
                ConfigFlag.SEQ_ALL)


def btc_usd_ticker(data):
    print('btc_usd_ticker', data)


def btc_usd_book(data):
    print('btc_usd_book', data)


def btc_usd_trades(data):
    print('btc_usd_trades', data)


def btc_usd_candles(data):
    print('btc_usd_trades', data)


def btc_usd_raw_book(data):
    print('btc_usd_trades', data)


def funding_usd_ticker(data):
    print('btc_usd_ticker', data)


def funding_usd_book(data):
    print('btc_usd_trades', data)


def funding_usd_rades(data):
    print('btc_usd_trades', data)


async def subscribe():
    await conn.subscribe_ticker("tBTCUSD", handler=btc_usd_ticker)
    await conn.subscribe_book("tBTCUSD", handler=btc_usd_book)
    await conn.subscribe_trades("tBTCUSD", handler=btc_usd_trades)
    await conn.subscribe_candles("tBTCUSD", handler=btc_usd_candles)
    await conn.subscribe_raw_book("tBTCUSD", handler=btc_usd_raw_book)
    await conn.subscribe_ticker("fUSD", handler=funding_usd_ticker)
    await conn.subscribe_book("fUSD", handler=funding_usd_book)
    await conn.subscribe_trades("fUSD", handler=funding_usd_rades)


start_at = "{0:%Y_%m_%d_%H_%M_%S}".format(datetime.utcnow())
f = open(f"../bitfinex_dump_flag_{conn.flags}-{start_at}.jsonl", "w")


def dump_it(message: str):
    f.write(message + '\n')


conn.on_connect_ws = subscribe
conn.on_before_handling = dump_it


def stop():
    asyncio.ensure_future(conn.stop())


loop = asyncio.get_event_loop()
loop.call_later(3600, stop)

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
