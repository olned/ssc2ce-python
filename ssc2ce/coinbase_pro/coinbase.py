import asyncio
import json
import logging

from time import time

import aiohttp

from ssc2ce.common.exceptions import Ssc2ceError
from ssc2ce.common import AuthType
from ssc2ce.common.session import SessionWrapper
from aiohttp import ClientResponseError


class Coinbase(SessionWrapper):
    """
    Handlers:
     - on_connect_ws - Called after the connection is established.
            If auth_type is not equivalent to AuthType.NONE,
            on_connect_ws will be set to self.auth_login;
     - on_close_ws - Called after disconnection, default value is None;
     - on_authenticated - Called after authentication is confirmed, default value is None;
     - on_token - Called after receiving a response to an authentication request, default value is None;
     - on_message - Called when a message is received, default value is self.handle_message;
     - on_handle_response - Called when the message from the exchange does not contain the request id;
     - on_response_error - Called when the response contains an error message.
    """

    def __init__(self,
                 sandbox: bool = True,
                 auth_param: dict = None):

        super().__init__()

        self.ws_api = "wss://ws-feed-public.sandbox.pro.coinbase.com" if sandbox \
            else "wss://ws-feed.pro.coinbase.com"

        self.rest_api = "https://api-public.sandbox.pro.coinbase.com" if sandbox \
            else "https://api.pro.coinbase.com"
        self.sandbox = sandbox

    async def public_get(self, request_path, params=None):
        async with self._session.get(url=self.rest_api + request_path,
                                     params=params,
                                     headers=None) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()

    async def get_currencies(self):
        try:
            return await self.public_get("/currencies")
        except ClientResponseError as e:
            self.logger.error(e.message)
            return []

    async def get_products(self):
        try:
            return await self.public_get("/products")
        except ClientResponseError as e:
            self.logger.error(e.message)
            return []
