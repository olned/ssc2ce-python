#!/usr/bin/env python

import asyncio
import logging

from deribit import Deribit
from deribit.VERSION import __version__

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.WARNING)
logger = logging.getLogger("ons-derobit-ws-python-sample")

conn = Deribit()


async def hello():
    await conn.send_public(request={
        "method": "public/hello",
        "params": {
            "client_name": "ONS Deribit",
            "client_version": __version__
        }
    })

    await conn.send_public(request={
        "method": "public/subscribe",
        "params": {
            "channels": ["deribit_price_index.btc_usd"]
        }
    })


async def printer(data):
    method = data.get("method")
    if method and method == "subscription":
        if data["params"]["channel"].startswith("deribit_price_index"):
            index_name = data["params"]["data"]["index_name"]
            price = data["params"]["data"]["price"]
            print(f" Deribit Price Index {index_name.upper()}: {price}")

conn.on_connect_ws = hello
conn.on_message = conn.handle_message

conn.method_routes += [
    ("subscription", printer),
]

loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()


try:
    loop.run_until_complete(conn.run_receiver())
    logger.info("Application was stopped.")
except KeyboardInterrupt:
    logger.info("Application closed by KeyboardInterrupt.")

conn.close()
