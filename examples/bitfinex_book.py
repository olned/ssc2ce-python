#!/usr/bin/env python
import asyncio
import logging

from ssc2ce.bitfinex import Bitfinex, L2Book

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")

conn = Bitfinex()


class BookMaintainer:
    def __init__(self, instrument):
        self.book = L2Book(instrument)
        self.check_sum = None
        self.active = False
        self.top_bid = [0, 0]
        self.top_ask = [0, 0]

    async def handle_book(self, message, connector):
        if type(message[1]) is str:
            if message[1] == "cs":
                pass
        elif len(message[1]) == 3:
            self.book.handle_update(message)
            self.book.time = message[-1]
        else:
            self.book.handle_snapshot(message)
            self.book.time = message[-1]

        if self.top_ask[0] != self.book.asks[0][0] or self.top_ask[0] != self.book.asks[0][0]:
            self.top_ask = self.book.asks[0].copy()
            self.top_bid = self.book.bids[0].copy()
            print(f"{self.book.instrument} bid:{self.top_bid[0]} ask:{self.top_ask[0]}")


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
