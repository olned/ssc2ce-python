#!/usr/bin/env python

import asyncio
import logging
import os
from pprint import pprint

from dotenv import load_dotenv
from deribit.deribit import Deribit, AuthType

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.WARNING)
logger = logging.getLogger("ons-derobit-ws-python-sample")

client_id = os.environ.get('DERIBIT_CLIENT_ID')
client_secret = os.environ.get('DERIBIT_CLIENT_SECRET')

if client_id is None or client_secret is None:
    logger.error("Please setup environment variables DERIBIT_CLIENT_ID and DERIBIT_CLIENT_SECRET")
    exit(0)

app = Deribit(client_id=client_id, client_secret=client_secret, auth_type=AuthType.CREDENTIALS)


async def start_credential():
    await app.auth_login()
    # await app.set_heartbeat(15)


async def do_something_after_login():
    await app.send_private(request={
        "method": "private/get_account_summary",
        "params": {
            "currency": "BTC",
            "extended": True
        }
    })

    await app.send_private(request={
        "method": "private/get_position",
        "params": {
            "instrument_name": "BTC-PERPETUAL"
        }
    })

    await app.send_private(request={
        "method": "private/enable_cancel_on_disconnect",
        "params": {}
    })

    await app.send_private(request={
        "method": "public/subscribe",
        "params": {
            "channels": [
                "book.BTC-PERPETUAL.raw"
            ]
        }
    })


"subscription"


async def printer(**kwargs):
    pprint(kwargs)


async def handle_subscription(data: dict):
    if data["params"]["channel"] == 'book.BTC-PERPETUAL.raw':
        return

    print(repr(data))


async def after_login():
    asyncio.ensure_future(do_something_after_login())


async def setup_refresh(refresh_interval):
    await asyncio.sleep(refresh_interval)
    await app.auth_refresh_token()


async def on_token(params):
    refresh_interval = min(600, params["expires_in"])
    asyncio.ensure_future(setup_refresh(refresh_interval))


app.on_connect_ws = start_credential
app.on_message = app.handle_message
app.on_authenticated = after_login
app.on_token = on_token
app.method_routes += [
    ("subscription", handle_subscription),
]
app.response_routes += [
    ("public/subscribe", printer),
    ("private/get_position", printer),
    ("private/enable_cancel_on_disconnect", printer),
    ("private/get_account_summary", printer),
]

loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()


def disable_heartbeat():
    asyncio.ensure_future(app.disable_heartbeat())


def logout():
    asyncio.ensure_future(app.auth_logout())


def stop():
    asyncio.ensure_future(app.stop())


# loop.call_later(60, stop)

try:
    loop.run_until_complete(app.run_receiver())
    logger.info("Application was stopped.")
except KeyboardInterrupt:
    logger.info("Application closed by KeyboardInterrupt.")

app.close()
