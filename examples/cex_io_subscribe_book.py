#!/usr/bin/env python
import asyncio
import json
import logging
import os

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

pending = {}


async def subscribe():
    for market in ["BTC-EUR", 'ETH-EUR', "ETH-BTC"]:
        pair = list(market.split('-'))
        request = {'e': "order-book-subscribe",
                   'oid': 'book-1',
                   'data': {'pair': [pair[0], pair[1]], 'subscribe': True, 'depth': 1}
                   }

        await conn.ws.send_json(request)


conn.on_connect_ws = subscribe
# conn.method_routes += [("subscription", handle_subscription)]

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
