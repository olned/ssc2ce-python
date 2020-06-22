#!/usr/bin/env python
import asyncio
import logging
import os

import aiohttp
from ssc2ce import Cex
from dotenv import load_dotenv

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

auth_param = dict(apiKey=os.environ.get('CEX_API_KEY'),
                  secret=os.environ.get('CEX_SECRET'),
                  uid=os.environ.get('CEX_UID'))

conn = Cex(auth_param)

archive_orders = []


async def get_archive_orders(symbol1, symbol2):
    global archive_orders
    res = await conn.private_get(f"archived_orders/{symbol1}/{symbol2}")
    archive_orders += res


async def start():
    request = {'e': "get-balance", 'oid': '1'}

    await conn.ws.send_json(request)

    my_balance = {}
    data = await conn.ws.receive()
    if data.type == aiohttp.WSMsgType.TEXT:
        data = data.json()
        if data.get('ok') == 'ok':
            balance = data['data']['balance']
            for key, value in balance.items():
                if float(value) != 0.00:
                    my_balance[key] = value

    print(my_balance)

    coroutines = []
    data = await conn.public_get("currency_limits")

    if data.get('ok') == 'ok':
        for pair in data['data']['pairs']:
            if pair['symbol1'] in my_balance and pair['symbol2'] in my_balance:
                print(pair)
                coroutines.append(get_archive_orders(pair['symbol1'], pair['symbol2']))
                break

        if coroutines:
            await asyncio.gather(*coroutines)
            for order in archive_orders:
                print(order)

    await conn.stop()


conn.on_connect_ws = start
loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    logger.info("Application closed by KeyboardInterrupt.")
