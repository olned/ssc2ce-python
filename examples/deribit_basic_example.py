#!/usr/bin/env python
import asyncio
from ssc2ce import Deribit

conn = Deribit()


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


conn.on_connect_ws = subscribe
conn.method_routes += [("subscription", handle_subscription)]

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
