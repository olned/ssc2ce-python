# ssc2ce
A Set of Simple Connectors for access To Cryptocurrency Exchanges via websocket based on
 [aiohttp](https://aiohttp.readthedocs.io) .

## Installation
Install ssc2ce with:
```bash
$ pip install ssc2ce
```

## Bitfinex
### Description
API description look at [Websocket API v2](https://docs.bitfinex.com/v2/docs/ws-general)
### Basic example
```python
import asyncio

from ssc2ce import Bitfinex

conn = Bitfinex()


async def handle_subscription(data):
    print(data)

async def subscribe():
    await conn.subscribe({
        "channel": "ticker",
        "symbol": "tBTCUSD"
    }, handler=handle_subscription)


conn.on_connect_ws = subscribe

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")

```

## Deribit 
### Description

API description look at [Deribit API v2 websocket](https://docs.deribit.com/v2/?python#json-rpc)

### Basic example
```python
import asyncio
from ssc2ce import Deribit

conn = Deribit()


async def subscribe():
    await conn.send_public(request={
        "method": "public/subscribe",
        "params": {
            "channels": ["deribit_price_index.btc_usd"]
        }
    })


async def handle_subscription(data):
    method = data.get("method")
    if method and method == "subscription":
        if data["params"]["channel"].startswith("deribit_price_index"):
            index_name = data["params"]["data"]["index_name"]
            price = data["params"]["data"]["price"]
            print(f" Deribit Price Index {index_name.upper()}: {price}")


conn.on_connect_ws = subscribe
conn.method_routes += [("subscription", handle_subscription)]

loop = asyncio.get_event_loop()


try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")

```
## Run examples from a clone

If you clone repository you can run examples from the root directory.
```bash
$ PYTHONPATH=.:$PYTHONPATH python examples/basic_example.py
```

The deribit_private.py example uses [python-dotenv](https://github.com/theskumar/python-dotenv), you must either install it if you want the example to work right out of the box,
```bash
$ pip install python-dotenv
```
or make the corresponding changes, removed followed code.
```python
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
```
To run the private.py example, you must either fill in the .env file or set the environment variables DERIBIT_CLIENT_ID and DERIBIT_CLIENT_SECRET. Look at .env_default. 
```bash
$ PYTHONPATH=.:$PYTHONPATH DERIBIT_CLIENT_ID=YOU_ACCESS_KEY DERIBIT_CLIENT_SECRET=YOU_ACCESS_SECRET python examples/private.py
```
