#!/usr/bin/env python
import asyncio
import json
from ssc2ce import Deribit

conn = Deribit()

pending = {}


async def handle_instruments(data: dict):
    del pending[data["id"]]
    print(json.dumps(data))
    if not pending:
        await subscribe()


async def handle_currencies(data: dict):
    for currency in data["result"]:
        symbol = currency["currency"]
        id = await conn.get_instruments(symbol, callback=handle_instruments)
        pending[id] = symbol


async def get_currencies():
    await conn.get_currencies(handle_currencies)


async def subscribe():
    await conn.send_public(request={
        "method": "public/subscribe",
        "params": {
            "channels": ["deribit_price_index.btc_usd"]
        }
    })


async def handle_subscription(data):
    method = data.get("method")
    if method and method == "subscription":
        if data["params"]["channel"].startswith("deribit_price_index"):
            index_name = data["params"]["data"]["index_name"]
            price = data["params"]["data"]["price"]
            print(f" Deribit Price Index {index_name.upper()}: {price}")


conn.on_connect_ws = get_currencies
conn.method_routes += [("subscription", handle_subscription)]

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
