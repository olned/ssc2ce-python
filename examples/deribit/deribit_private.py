#!/usr/bin/env python

import asyncio
import logging
import os
import re
from uuid import uuid4
from typing import Pattern
from dotenv import load_dotenv
from ssc2ce import Deribit, AuthType


class MyApp:
    def __init__(self):
        logging.basicConfig(
            format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
        self.logger = logging.getLogger("deribit-private")
        self.direct_requests = {}

        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        client_id = os.environ.get('DERIBIT_CLIENT_ID')
        client_secret = os.environ.get('DERIBIT_CLIENT_SECRET')

        if client_id is None or client_secret is None:
            self.logger.error(
                "Please setup environment variables DERIBIT_CLIENT_ID and DERIBIT_CLIENT_SECRET")
            exit(0)

        self.deribit = Deribit(client_id=client_id,
                               client_secret=client_secret,
                               auth_type=AuthType.CREDENTIALS,
                               scope=None,
                               get_id=lambda: str(uuid4()))

        self.deribit.on_handle_response = self.on_handle_response
        self.deribit.on_authenticated = self.after_login
        self.deribit.on_token = self.on_token
        self.deribit.on_response_error = self.on_response_error

        self.deribit.method_routes += [
            ("subscription", self.handle_subscription),
        ]
        self.deribit.response_routes += [
            ("public/subscribe", self.printer),
            ("private/subscribe", self.printer),
            ("private/get_position", self.printer),
            ("private/enable_cancel_on_disconnect", self.printer),
            ("private/get_account_summary", self.printer),
        ]

        self.subscription_route = [
            (re.compile(r"book.(.*).raw"), self.handle_order_book_change),
            (re.compile(r"user.trades.(.*).raw"), self.handle_user_trades),
            (re.compile(r"user.orders.(.*).raw"), self.handle_user_orders),
            (re.compile(r"deribit_price_index.(.*)"), self.handle_price_index),
            (re.compile(r"trades.(.*).raw"), self.handle_trades),
            (re.compile(r"ticker.(.*).raw"), self.handle_ticker)
        ]

    async def do_something_after_login(self):
        await self.deribit.send_private(request={
            "method": "private/get_account_summary",
            "params": {
                "currency": "BTC",
                "extended": True
            }
        })

        await self.deribit.send_private(request={
            "method": "private/get_position",
            "params": {
                "instrument_name": "BTC-PERPETUAL"
            }
        })

        await self.deribit.send_public(request={
            "method": "private/subscribe",
            "params": {
                "channels": [
                    "deribit_price_index.btc_usd",
                    "book.BTC-PERPETUAL.raw",
                    "trades.BTC-PERPETUAL.raw",
                    "user.orders.BTC-PERPETUAL.raw",
                    "user.trades.BTC-PERPETUAL.raw"
                ]
            }
        })

        await self.deribit.send_public(request={
            "method": "public/set_heartbeat",
            "params": {
                "interval": 15
            }
        })

    async def printer(self, **kwargs):
        self.logger.info(f"{repr(kwargs)}")

    @ staticmethod
    def resolve_route(value, routes):
        key, handler = None, None
        for key, handler in routes:
            if key:
                if isinstance(key, str):
                    if key == value:
                        return handler
                elif isinstance(key, Pattern) and re.match(key, value):
                    return handler

        if key is not None and key == "" and handler:
            return handler

    def handle_subscription(self, data: dict):
        channel = data["params"]["channel"]
        handler = self.resolve_route(channel, self.subscription_route)
        if handler:
            return handler(data)

    def after_login(self):
        asyncio.ensure_future(self.do_something_after_login())

    async def setup_refresh(self, refresh_interval):
        await asyncio.sleep(refresh_interval)
        await self.deribit.auth_refresh_token()

    def on_token(self, params):
        refresh_interval = min(600, params["expires_in"])
        asyncio.ensure_future(self.setup_refresh(refresh_interval))

    def on_handle_response(self, data):
        request_id = data["id"]
        if request_id in self.direct_requests:
            self.logger.info(
                f"Caught response {repr(data)} to direct request {self.direct_requests[request_id]}")
        else:
            self.logger.error(
                f"Can't find request with id:{request_id} for response:{repr(data)}")

    def handle_order_book_change(self, message):
        data = message["params"]["data"]
        self.logger.debug(f"{repr(data)}")

    def handle_user_trades(self, message):
        data = message["params"]["data"]
        self.logger.info(f"{repr(data)}")

    def handle_user_orders(self, message):
        data = message["params"]["data"]
        self.logger.info(f"{repr(data)}")

    def handle_price_index(self, message):
        data = message["params"]["data"]
        index_name = data['index_name']
        self.logger.info(f"{index_name}: {repr(data)}")

    def handle_trades(self, message):
        data = message["params"]["data"]
        self.logger.debug(f"{repr(data)}")

    def handle_ticker(self, message):
        data = message["params"]["data"]
        instrument_name = data['instrument_name']
        self.logger.debug(f"{instrument_name}: {repr(data)}")

    def on_response_error(self, data):
        self.logger.error(f"Receive error {repr(data)}")
        asyncio.ensure_future(self.deribit.stop())

    def disable_heartbeat(self):
        asyncio.ensure_future(self.deribit.disable_heartbeat())

    def logout(self):
        asyncio.ensure_future(self.deribit.auth_logout())

    async def run(self):
        await self.deribit.run_receiver()

    async def stop(self):
        await self.deribit.stop()


if __name__ == '__main__':
    app = MyApp()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(app.run())
    except KeyboardInterrupt:
        loop.run_until_complete(app.stop())
    finally:
        app.logger.info('Program finished')
