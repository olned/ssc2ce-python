#!/usr/bin/env python
import asyncio
import logging

from ssc2ce import Cex

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("bitfinex-basic-example")

conn = Cex()


async def subscribe():
    data = await conn.public_get("currency_limits")
    if data.get('ok') == 'ok':
        for pair in data['data']['pairs']:
            if pair['symbol1'] == 'BTC' and pair['symbol2'] == 'EUR':
                print(pair)

    data = await conn.public_get("ticker/BTC/EUR")
    print(data)

    request = {'e': "subscribe", 'rooms': ["ticker"]}

    await conn.ws.send_json(request)


def print_ticker(msg):
    print(msg)
    return True


conn.on_connect_ws = subscribe
conn.on_message = print_ticker

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")
