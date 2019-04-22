#!/usr/bin/env python

import asyncio
import logging

from deribit.deribit import Deribit

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger("ons-derobit-ws-python-sample")

app = Deribit()


async def start_public():
    await app.send_public(request={
        "method": "public/hello",
        "params": {
            "client_name": "TCC Public Example",
            "client_version": "0.1.0"
        }
    })
    await app.set_heartbeat(13)


app.on_connect_ws = start_public
app.on_message = app.handle_message
# app.on_close_ws = app.close

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
