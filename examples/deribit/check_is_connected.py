import asyncio
import json
from ssc2ce import Deribit

conn = Deribit()

print("Is connected after init", conn.is_connected())


def close():
    print("Check connection  before closing", conn.is_connected())
    asyncio.ensure_future(conn.stop())


loop = asyncio.get_event_loop()


loop.call_later(1, close)

try:
    loop.run_until_complete(conn.run_receiver())
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")


print("Is connected before exit", conn.is_connected())
