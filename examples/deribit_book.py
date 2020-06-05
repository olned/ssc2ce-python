#!/usr/bin/env python
import asyncio
import json
import logging
from ssc2ce import Deribit
from ssc2ce.deribit.l2_book import L2Book

conn = Deribit()

pending = {}
books = {}

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("deribit-book")


async def handle_instruments(data: dict):
    request_id = data["id"]
    del pending[request_id]
    print(json.dumps(data))
    if not pending:
        await subscribe_books(list(books.keys()))


async def handle_currencies(data: dict):
    for currency in data["result"]:
        symbol = currency["currency"]
        instrument = symbol+"-PERPETUAL"
        book = L2Book(instrument)
        book.top_bid = [0., 0.]
        book.top_ask = [0., 0.]
        books[instrument] = book
        request_id = await conn.get_instruments(symbol, kind="future", callback=handle_instruments)
        pending[request_id] = symbol


async def get_currencies():
    await conn.get_currencies(handle_currencies)


async def subscribe_books(instruments: list):
    await conn.send_public(request={
        "method": "public/subscribe",
        "params": {
            "channels": [f"book.{i}.raw" for i in instruments]
        }
    })


async def handle_subscription(data):
    method = data.get("method")
    if method and method == "subscription":
        params = data["params"]
        channel = params["channel"]
        if channel.startswith("book."):
            params_data = params["data"]
            instrument = params_data["instrument_name"]
            book: L2Book = books[instrument]
            if "prev_change_id" in params_data:
                book.handle_update(params_data)
            else:
                book.handle_snapshot(params_data)

            if book.top_ask[0] != book.asks[0][0] or book.top_bid[0] != book.bids[0][0]:
                book.top_ask = book.asks[0].copy()
                book.top_bid = book.bids[0].copy()
                print(f"{instrument} bid:{book.top_bid[0]} ask:{book.top_ask[0]}")
        else:
            print("Unknown channel", json.dumps(data))


conn.on_connect_ws = get_currencies
conn.method_routes += [("subscription", handle_subscription)]

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
