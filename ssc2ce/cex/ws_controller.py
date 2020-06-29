import asyncio
import json
import logging
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Optional, Callable, Any, Awaitable

import aiohttp
from aiohttp import ClientResponseError
from ssc2ce.common.session import SessionWrapper


class WrongMessage(Exception):
    def __init__(self, msg: aiohttp.WSMessage):
        self.msg = msg


def convert_message(msg: aiohttp.WSMessage):
    if msg.type == aiohttp.WSMsgType.TEXT:
        message = msg.data
        return json.loads(message)
    else:
        raise WrongMessage(msg)


def hide_secret(request: dict):
    data = request.copy()
    hidden_keys = ["key", "signature"]

    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = hide_secret(value)
        elif key in hidden_keys:
            data[key] = "***"

    return data


class Cex(SessionWrapper):
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

    _user_on_connect: Optional[Callable[[], Any]] = None
    _user_async_on_connect: Optional[Callable[[], Awaitable[Any]]] = None

    def __init__(self, auth_param: dict = None):

        super().__init__()

        self.ws_api = 'wss://ws.cex.io/ws/'
        self.rest_api = 'https://cex.io/api/'
        self.logger = logging.getLogger(__name__)
        self.auth_param = auth_param.copy() if auth_param else auth_param
        self._async_on_connect = self.handle_connected

    def rest_signature(self):
        """
        Create signature for REST request

        Look at https://cex.io/rest-api#/definitions/signature
        An HMAC-SHA256 encoded message containing - a nonce, user ID and API key. The HMAC-SHA256 code must be
        enerated using a secret key that was generated with your API key. This code must be converted to
        its hexadecimal representation (64 uppercase characters).

        :return:
        """

        unix_ts = int(datetime.now().timestamp())  # UNIX timestamp in seconds
        string = "{}{}{}".format(unix_ts, self.auth_param["uid"], self.auth_param['apiKey'])
        signature = hmac.new(self.auth_param['secret'].encode(), string.encode(), hashlib.sha256).hexdigest().upper()
        return {'key': self.auth_param['apiKey'],
                'signature': signature,
                'nonce': unix_ts, }

    async def authorize(self):
        """

        :return:
        """

        unix_ts = int(datetime.now().timestamp())  # UNIX timestamp in seconds
        string = "{}{}".format(unix_ts, self.auth_param['apiKey'])
        signature = hmac.new(self.auth_param['secret'].encode(), string.encode(), hashlib.sha256).hexdigest()
        request = {'e': 'auth',
                   'auth': {'key': self.auth_param["apiKey"],
                            'signature': signature,
                            'timestamp': unix_ts},
                   'oid': 'auth', }

        try:
            self.logger.info(f"Auth{hide_secret(request)} is been sending")
            await self.ws.send_json(request)
        except Exception as e:
            logging.error("{}.authorize, {}({})".format(self.__class__.__name__, e.__class__.__name__, e))
            raise

        msg = await self.ws.receive()
        msg = convert_message(msg)
        if msg.get('e') == 'auth' and msg.get('ok') == 'ok' and msg["data"].get('ok') == 'ok':
            conf_ts = msg["timestamp"]
            conf_ts = datetime.fromtimestamp(conf_ts, tz=timezone.utc).isoformat()
            self.logger.info("Successful authorization. " + conf_ts)
        else:
            self.logger.error("Unsuccessful authorization:" + json.dumps(msg))
            await self.ws.close()

    @property
    def on_connect_ws(self):
        if self._async_on_connect:
            return self._user_async_on_connect
        else:
            return self._user_on_connect

    @on_connect_ws.setter
    def on_connect_ws(self, handler):
        if handler is None:
            self._user_async_on_connect = None
            self._user_on_connect = None
        else:
            if asyncio.iscoroutinefunction(handler):
                self._user_async_on_connect = handler
                self._user_on_connect = None
            else:
                self._user_async_on_connect = None
                self._user_on_connect = handler

    async def handle_connected(self):
        msg = await self.ws.receive()
        msg = convert_message(msg)
        if msg.get('e') == 'connected':
            if self.auth_param:
                await self.authorize()

            if self._user_async_on_connect:
                await self._user_async_on_connect()
            elif self._user_on_connect:
                self._user_on_connect()
        else:
            self.logger.error(f"Wrong protocol. Expected 'connected' received:{json.dumps(msg)}")
            await self.ws.close()

    async def ping(self):
        request = '{"e": "pong"}'
        await self.ws.send_str(request)
        self.logger.debug("ping - " + json.dumps(request))

    def handle_message(self, message: str):
        data = json.loads(message)

        msg_type = data.get('e')
        if msg_type == 'ping':
            asyncio.ensure_future(self.ping())
        else:
            self.logger.info(message)

    async def get_currency_limits(self):
        try:
            result = await self.public_get("currency_limits")
            return result
        except ClientResponseError as e:
            self.logger.error(e.message)
            return {}

    async def private_get(self, request_path, params: dict = None):
        if params is None:
            params = self.rest_signature()
        else:
            params.update(self.rest_signature())

        print(params)
        # body = json.dumps(params)

        async with self._session.get(self.rest_api + request_path, data=params) as response:
            if response.status == 200:
                data = await response.read()
                data = json.loads(data)
                return data
            else:
                self.logger.error(self.rest_api + request_path)
                response.raise_for_status()
