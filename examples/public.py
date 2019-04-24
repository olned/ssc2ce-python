#!/usr/bin/env python

import asyncio
import logging
from pprint import pprint

from deribit import Deribit
from deribit.VERSION import __version__

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger("ons-derobit-ws-python-sample")

app = Deribit()


async def start_public():
    await app.send_public(request={
        "method": "public/hello",
        "params": {
            "client_name": "TCC Deribit Connector",
            "client_version": __version__
        }
    })
    await app.set_heartbeat(13)
    await app.send_public(request={
        "method": "public/subscribe",
        "params": {
            "channels": ["book.BTC-PERPETUAL.raw"]
        }
    })


async def printer(data):
    pprint(data)


app.on_connect_ws = start_public
app.on_message = app.handle_message

app.method_routes += [
    ("subscription", printer),
]

loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()


def disable_heartbeat():
    asyncio.ensure_future(app.disable_heartbeat())


def stop():
    asyncio.ensure_future(app.stop())


loop.call_later(60, stop)

try:
    loop.run_until_complete(app.run_receiver())
    logger.info("Application was stopped.")
except KeyboardInterrupt:
    logger.info("Application closed by KeyboardInterrupt.")

app.close()
