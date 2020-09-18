import asyncio
import json
from ssc2ce import Deribit

conn = Deribit()

loop = asyncio.get_event_loop()

i = 0
def check():
    global i
    i += 1
    print("Check connection  ", conn.is_connected())
    loop.call_later(1, close, i < 2)

def run():
    print("Is connected before run_receiver() ", conn.is_connected())
    asyncio.ensure_future(conn.run_receiver())
    loop.call_later(1, check)

def close(restart: bool = True):
    print("Is connection before closing", conn.is_connected())
    asyncio.ensure_future(conn.stop())
    if restart:
        loop.call_later(2, run)

def stop():
    loop.call_later(1, loop.stop)

loop.call_later(10, stop)
loop.call_soon(run)

try:
    loop.run_forever()
except KeyboardInterrupt:
    print("Application closed by KeyboardInterrupt.")


print("Is connected before exit", conn.is_connected())
