#!/usr/bin/env python
import asyncio
import logging
import os

from ssc2ce import Coinbase

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")


auth_param = dict(api_key=os.environ.get('COINBASE_PRO_KEY'),
                  secret_key=os.environ.get('COINBASE_PRO_SECRET'),
                  passphrase=os.environ.get('COINBASE_PRO_PASSPHRASE'))


def handle_message(message: str):
    logger.info(message)

sandbox=os.getenv("SANDBOX", 'True').lower() not in ('false', '0', 'f')
logger.info('sandbox:%s', str(sandbox))

conn = Coinbase(auth_param=auth_param, sandbox=sandbox)
conn.on_message = handle_message


async def start():
    res = await conn.private_get('/accounts')
    print(res)
    await conn.stop()
    # await conn.ws.send_json({
    #     "type": "subscribe",
    #     "product_ids": [
    #         "BTC-USD",
    #         "ETH-BTC"
    #     ],
    #     "channels": [
    #         "level2",
    #         "heartbeat"
    #     ]
    # })


def handle_heartbeat(data: dict) -> bool:
    logger.info(f"{repr(data)}")
    return True


conn.on_connect_ws = start


def stop():
    asyncio.ensure_future(conn.stop())


loop = asyncio.get_event_loop()
loop.call_later(3600, stop)

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    logger.info("Application closed by KeyboardInterrupt.")
