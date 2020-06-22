#!/usr/bin/env python
import asyncio
import logging

from ssc2ce.bitfinex import Bitfinex, BitfinexL2Book

logging.basicConfig(
    format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s',
    level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")

conn = Bitfinex()


class BookMaintainer:
    def __init__(self, instrument):
        self.book = BitfinexL2Book(instrument)
        self.check_sum = None
        self.active = False
        self.top_bid = 0.
        self.top_ask = 0.

    def handle_book(self, message, _):
        if type(message[1]) is str:
            if message[1] == "cs":
                pass
        elif len(message[1]) == 3:
            self.book.handle_update(message)
            self.book.time = message[-1]
        else:
            self.book.handle_snapshot(message)
            self.book.time = message[-1]

        if self.top_ask != self.book.top_ask_price() or self.top_bid != self.book.top_bid_price():
            self.top_ask = self.book.top_ask_price()
            self.top_bid = self.book.top_bid_price()
            logger.info(
                f"{self.book.instrument()} bid:{self.top_bid} ask:{self.top_ask}")


btc = BookMaintainer("BTC-USD")
eth = BookMaintainer("ETH-USD")


async def subscribe():
    await conn.subscribe({'channel': "book", 'symbol': "tBTCUSD"}, handler=btc.handle_book)
    await conn.subscribe({'channel': "book", 'symbol': "tETHUSD"}, handler=eth.handle_book)


conn.on_connect_ws = subscribe

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    loop.run_until_complete(conn.stop())
finally:
    print("Application closed")
