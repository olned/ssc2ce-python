#!/usr/bin/env python
import asyncio
import logging
import os

from examples.common.book_watcher import BookWatcher
from ssc2ce import Cex, CexParser
from dotenv import load_dotenv

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

auth_param = dict(apiKey=os.environ.get('CEX_API_KEY'),
                  secret=os.environ.get('CEX_SECRET'),
                  uid=os.environ.get('CEX_UID'))

print(auth_param)

conn = Cex(auth_param)
parser = CexParser()
watcher = BookWatcher(parser)
conn.on_message = parser.parse


async def subscribe():
    for market in ["BTC-EUR", 'ETH-EUR', "ETH-BTC"]:
        pair = list(market.split('-'))
        request = {'e': "order-book-subscribe",
                   'oid': 'book-1',
                   'data': {'pair': [pair[0], pair[1]], 'subscribe': True, 'depth': 0}
                   }

        await conn.ws.send_json(request)


output = open("cex_dump_1h.jsonl", "w")


def dump(msg: str):
    output.write(msg)
    output.write('\n')


conn.on_connect_ws = subscribe
conn.on_before_handling = dump
loop = asyncio.get_event_loop()


def stop():
    asyncio.ensure_future(conn.ws.close())


loop.call_later(3600, stop)
try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
