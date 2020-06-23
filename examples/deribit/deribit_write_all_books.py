#!/usr/bin/env python
import asyncio
import json
import logging
from ssc2ce import Deribit

conn = Deribit()

pending = {}

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("deribit-writer")

instruments = []


async def handle_instruments(data: dict):
    global instruments
    request_id = data["id"]
    del pending[request_id]
    print(json.dumps(data))
    instruments += list(set(
        [x["instrument_name"][:11] if not x["instrument_name"].endswith("-PERPETUAL") else x["instrument_name"] for x in
         data["result"]]))

    if not pending:
        print(instruments)
        await subscribe_books()


async def handle_book_summary_by_currency(data: dict):
    request_id = data["id"]
    del pending[request_id]
    print(json.dumps(data))


async def handle_currencies(data: dict):
    for currency in data["result"]:
        symbol = currency["currency"]
        print(json.dumps(data))
        request_id = await conn.get_instruments(symbol, callback=handle_instruments)
        pending[request_id] = symbol
        request_id = await conn.send_public(
            request={"method": "public/get_book_summary_by_currency", "params": {"currency": symbol}},
            callback=handle_instruments)
        pending[request_id] = symbol


async def get_currencies():
    await conn.get_currencies(handle_currencies)


async def subscribe_books():
    global instruments
    await conn.send_public(request={
        "method": "public/subscribe",
        "params": {
            "channels": [f"book.{i}.raw" for i in instruments]
        }
    })

    await conn.send_public(request={
        "method": "public/set_heartbeat",
        "params": {
            "interval": 15
        }
    })


output = open("deribit_dump.jsonl", "w")


def dump(msg: str):
    output.write(msg)
    output.write('\n')


def stop():
    asyncio.ensure_future(conn.ws.close())


conn.on_before_handling = dump
conn.on_connect_ws = get_currencies

loop = asyncio.get_event_loop()
loop.call_later(3600, stop)

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
