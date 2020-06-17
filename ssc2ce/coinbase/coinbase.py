import asyncio
import json
import logging

from time import time

import aiohttp

from ssc2ce.common.exceptions import Ssc2ceError
from ssc2ce.common import AuthType
from ssc2ce.common.session import SessionWrapper
from ssc2ce.common.utils import resolve_route, hide_secret, IntId


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

