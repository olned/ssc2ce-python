# ssc2ce
A set of simple connectors for access to few cryptocurrency Exchanges via websocket based on
 [aiohttp](https://aiohttp.readthedocs.io).

Supported Exchanges:
- Bitfinex - only public API,
- CEX.io,
- Coinbase Pro
- Deribit
    
This is more of a pilot project, if you have any wishes for adding exchanges or expanding functionality, please register issues.

## Installation
Install ssc2ce with:
```bash
$ pip install ssc2ce
```

You can run some examples with  
## Bitfinex
### Description
API description look at [Websocket API v2](https://docs.bitfinex.com/v2/docs/ws-general)
### Basic example
```python
import asyncio

from ssc2ce import Bitfinex

conn = Bitfinex()


def handle_subscription(data, connector: Bitfinex):
    print(data, f"received:{connector.receipt_time}")


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


def handle_subscription(data):
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
PYTHONPATH=.:$PYTHONPATH python examples/bitfinex/bitfinex_basic_example.py
```

To run some examples, you may need additional modules, you can install them from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

To run the private.py example, you must either fill in the .env file, look at .env.example, or set the environment variables DERIBIT_CLIENT_ID and DERIBIT_CLIENT_SECRET. 

```bash
PYTHONPATH=.:$PYTHONPATH DERIBIT_CLIENT_ID=YOU_ACCESS_KEY DERIBIT_CLIENT_SECRET=YOU_ACCESS_SECRET python examples/deribit/deribit_private.py
```
