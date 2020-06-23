#!/usr/bin/env python
import asyncio
import logging
from ssc2ce import Coinbase

conn = Coinbase(sandbox=False)

pending = {}

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("deribit-writer")

instruments = []


async def subscribe_books():
    await conn.ws.send_json({
        "type": "subscribe",
        "product_ids": instruments,
        "channels": [
            "level2",
            "heartbeat"
        ]
    })


output = open("coinbase_dump.jsonl", "w")


def dump(msg: str):
    output.write(msg)
    output.write('\n')


def stop():
    asyncio.ensure_future(conn.ws.close())


async def run():
    all_products = [x for x in await conn.get_products()]

    my_products = {x['id']: x for x in all_products if x['quote_currency'] == 'EUR'}
    base_currencies = [x['base_currency'] for x in my_products.values()]

    for product in all_products:
        if product["id"] in my_products:
            continue

        if product['quote_currency'] in base_currencies:
            my_products[product["id"]] = product

    global instruments
    instruments += list(my_products.keys())
    await conn.run_receiver()


conn.on_before_handling = dump
conn.on_connect_ws = subscribe_books

loop = asyncio.get_event_loop()
loop.call_later(3600, stop)

try:
    loop.run_until_complete(run())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
