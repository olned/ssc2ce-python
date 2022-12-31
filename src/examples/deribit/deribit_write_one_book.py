#!/usr/bin/env python
import asyncio
import logging
import os
from uuid import uuid4

from ssc2ce import Deribit, AuthType

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("deribit-writer")

client_id = os.environ.get('DERIBIT_CLIENT_ID')
client_secret = os.environ.get('DERIBIT_CLIENT_SECRET')

if client_id is None or client_secret is None:
    logger.error(
        "Please setup environment variables DERIBIT_CLIENT_ID and DERIBIT_CLIENT_SECRET")
    exit(0)

testnet = os.getenv("SANDBOX", 'True').lower() not in ('false', '0', 'f')

conn= Deribit(client_id=client_id,
            client_secret=client_secret,
            auth_type=AuthType.CREDENTIALS,
            scope=None,
            testnet=testnet,
            get_id=lambda: str(uuid4()))


async def subscribe_book():
    await conn.send_private(request={
        "method": "private/subscribe",
        "params": {
            "channels": [f"book.BTC-PERPETUAL.raw"]
        }
    })


os.makedirs("DATA", exist_ok=True) 
output = open(os.path.join("DATA", "deribit_dump_btc_perpetual.jsonl"), "w")


def dump(msg: str):
    output.write(msg)
    output.write('\n')


conn.on_connect_ws = subscribe_book
conn.on_before_handling = dump
loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
