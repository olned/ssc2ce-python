import asyncio
import json
import logging

import aiohttp

from ssc2ce.common.exceptions import Ssc2ceError
from ssc2ce.common.session import SessionWrapper
from ssc2ce.common.utils import resolve_route, IntId

from enum import IntEnum


class AuthType(IntEnum):
    NONE = 0
    PASSWORD = 1
    CREDENTIALS = 2
    SIGNATURE = 3


def hide_secret(request):
    data = request.copy()
    hidden_keys = ["password", "username", "client_id", "client_secret", "refresh_token", "access_token"]

    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = hide_secret(value)
        elif key in hidden_keys:
            data[key] = "***"

    return data


class Deribit(SessionWrapper):
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
    auth_params: dict = None

    def __init__(self,
                 client_id: str = None,
                 client_secret: str = None,
                 scope: str = "session",
                 testnet: bool = True,
                 auth_type: AuthType = AuthType.NONE,
                 get_id=IntId().get_id):

        if auth_type & (AuthType.CREDENTIALS | AuthType.SIGNATURE):
            if client_secret is None or client_id is None:
                raise Ssc2ceError(f" Authentication {str(auth_type)} need client_id and client_secret")

        if auth_type == AuthType.SIGNATURE:
            raise NotImplemented(f"Authentication {str(auth_type)} for Deribit is not implemented.")

        super().__init__()

        if auth_type != AuthType.NONE:
            self.on_connect_ws = self.auth_login

        self.on_authenticated = None
        self.on_token = None
        self.on_response_error = None
        self.on_handle_response = None

        self.requests = {}
        self.ws_api = f"wss://{'test' if testnet else 'www'}.deribit.com/ws/api/v2/"
        self.get_id = get_id
        self.logger = logging.getLogger(__name__)
        self.auth_type = auth_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope

        self.method_routes = [
            ("heartbeat", self.handle_heartbeat),
        ]
        self.response_routes = [
            ("public/auth", self.handle_auth),
            ("", self.empty_handler),
        ]

    def close(self):
        super()._close()

    async def stop(self):
        """
        Close connection and break the receiver loop
        :return:
        """
        await self.ws.close()

    async def send_public(self, request: dict, callback=None, logging_it: bool = True) -> int:
        """
        Send a public request

        :param request: Request without jsonrpc and id fields
        :param callback: The function that will be called after receiving the query result. Default is None
        :param logging_it:
        :return: Request Id
        """
        request_id = self.get_id()
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            **request
        }
        if logging_it:
            self.logger.info(f"sending:{repr(hide_secret(request))}")
        await self.ws.send_json(request)

        if callback:
            request["callback"] = callback

        self.requests[request_id] = request

        return request_id

    async def send_private(self, request: dict, callback=None) -> int:
        """
        Send a private request

        :param request: Request without jsonrpc and id fields
        :param callback: The function that will be called after receiving the query result. Default is None
        :return: Request Id
        """

        request_id = self.get_id()
        access_token = self.auth_params["access_token"]
        request["params"]["access_token"] = access_token

        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            **request
        }
        self.logger.info(f"sending:{repr(hide_secret(request))}")
        await self.ws.send_json(request)

        if callback:
            request["callback"] = callback

        self.requests[request_id] = request

        return request_id

    async def send(self, request: dict, callback=None) -> int:
        """
        A wrapper for send_private and send_public, defines the type of request by content.

        :param request: Request without jsonrpc and id fields
        :param callback: The function that will be called after receiving the query result. Default is None
        :return: Request Id
        """
        method = request["method"]
        if method.starts("public/"):
            request_id = await self.send_public(request, callback)
        else:
            request_id = await self.send_private(request, callback)

        return request_id

    async def auth_login(self) -> int:
        """
        Send an authentication request using parameters stored in the constructor

        :return: Reuest id
        """
        self.auth_type = AuthType.CREDENTIALS

        msg = {
            "method": "public/auth",
            "params": {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        }

        if self.scope:
            msg["scope"] = self.scope

        request_id = await self.send_public(msg)
        return request_id

    async def auth_client_credentials(self, client_id, client_secret, scope: str = None) -> int:
        """
        Send a credentials authentication request

        :param client_id: using the access key
        :param client_secret: and access secret that can be found on the API page on the website
        :param scope:
            connection, session, session:name,
            trade:[read, read_write, none],
            wallet:[read, read_write, none],
            account:[read, read_write, none]
        :return: Request Id
        """

        self.auth_type = AuthType.CREDENTIALS

        msg = {
            "method": "public/auth",
            "params": {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            }
        }

        if scope:
            self.scope = scope

        if self.scope:
            msg["scope"] = self.scope

        request_id = await self.send_public(msg)
        return request_id

    async def auth_password(self, username: str, password: str, scope: str = None) -> int:
        """
        Send a password authentication request

        :param username: User name
        :param password: Password
        :param scope:
            connection, session, session:name,
            trade:[read, read_write, none],
            wallet:[read, read_write, none],
            account:[read, read_write, none]
        :return: Request Id
        """

        self.auth_type = AuthType.PASSWORD
        msg = {
            "method": "public/auth",
            "params": {
                "grant_type": "password",
                "username": username,
                "password": password
            }
        }

        if scope:
            self.scope = scope

        if self.scope:
            msg["scope"] = scope

        request_id = await self.send_public(msg)
        return request_id

    async def auth_refresh_token(self) -> int:
        """
        Send a refresh token request

        :return: Request Id
        """
        msg = {
            "method": "public/auth",
            "params": {
                "grant_type": "refresh_token",
                "refresh_token": self.auth_params["refresh_token"]
            }
        }

        request_id = await self.send_public(msg)
        return request_id

    async def auth_logout(self) -> int:
        """
        Send a logout request

        :return: Request Id
        """
        msg = {
            "method": "private/logout",
            "params": {}
        }

        request_id = await self.send_private(msg)
        return request_id

    async def set_heartbeat(self, interval: int = 15) -> int:
        """

        :param interval:
        :return:
        """
        request_id = await self.send_public({"method": "public/set_heartbeat", "params": {"interval": interval}})
        return request_id

    async def disable_heartbeat(self) -> int:
        """

        :return:
        """
        request_id = await self.send_public({"method": "public/disable_heartbeat", "params": {}})
        return request_id

    async def get_currencies(self, callback=None):
        """
        Send a request for a list of cryptocurrencies supported by the API
        :param callback:
        :return: Request Id
        """
        return await self.send_public(request=dict(method="public/get_currencies", params={}), callback=callback)

    async def get_instruments(self, currency: str, kind: str = None, expired: bool = False, callback=None) -> int:
        """
        Send a request for a list available trading instruments
        :param currency: The currency symbol: BTC or ETH
        :param kind: Instrument kind: future or option, if not provided instruments of all kinds are considered
        :param expired:
        :param callback:
        :return: Request Id
        """
        request = {"method": "public/get_instruments",
                   "params": {
                       "currency": currency,
                       "expired": expired
                   }}
        if kind:
            request["params"]["kind"] = kind

        return await self.send_public(request=request, callback=callback)

    def handle_message(self, message: str) -> None:
        """

        :param message:
        :return:
        """
        data = json.loads(message)
        if "method" in data:
            self.handle_method_message(data)
        else:
            if "id" in data:
                if "error" in data:
                    self.handle_error(data)
                else:
                    request_id = data["id"]
                    if request_id:
                        self.handle_response(request_id, data)
            else:
                self.handle_method_message(data)

    def empty_handler(self, **kwargs) -> None:
        """
        A default handler
        :param kwargs:
        :return:
        """
        self.logger.debug(f"{repr(kwargs)}")

    def handle_response(self, request_id: int, response: dict) -> None:
        """

        :param request_id:
        :param response:
        :return:
        """

        request = self.requests.get(request_id)
        if request:
            if "callback" in request:
                callback = request["callback"]
                if asyncio.iscoroutinefunction(callback):
                    asyncio.ensure_future(callback(response))
                else:
                    callback(response)
            else:
                method = request["method"]
                handler = resolve_route(method, self.response_routes)
                if handler:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.ensure_future(handler(request=request, response=response))
                    else:
                        handler(request=request, response=response)
                else:
                    self.logger.warning(f"Unhandled method:{method} response:{repr(response)} "
                                        f"to request:{repr(request)}.")

            del self.requests[request_id]
        else:
            if self.on_handle_response:
                if asyncio.iscoroutinefunction(self.on_handle_response):
                    asyncio.ensure_future(self.on_handle_response(response))
                else:
                    self.on_handle_response(response)
                return
            else:
                self.logger.warning(
                    f"Unknown id:{request_id}, the on_handle_response event must be defined."
                    f" Unhandled message {response}")

    def handle_method_message(self, data) -> None:
        """

        :param data:
        :return:
        """
        method = data["method"]
        handler = resolve_route(method, self.method_routes)

        if handler:
            if asyncio.iscoroutinefunction(handler):
                asyncio.ensure_future(handler(data))
            else:
                handler(data)

        elif not self.on_before_handling:
            self.logger.warning(f"Unhandled message:{repr(data)}.")

    def handle_heartbeat(self, data):
        """

        :param data:
        :return:
        """
        if data["params"]["type"] == "test_request":
            asyncio.ensure_future(self.send_public({"method": "public/test", "params": {}}, logging_it=False))

    def handle_auth(self, request, response) -> None:
        """

        :param request:
        :param response:
        :return:
        """
        self.auth_params = response["result"]
        grant_type = request["params"]["grant_type"]
        if grant_type == "":
            if self.on_token:
                self.on_token(response["result"])
        elif grant_type in ("client_credentials", "password"):
            # TODO - Why we use two handlers?
            if self.on_authenticated:
                self.on_authenticated()
            if self.on_token:
                self.on_token(response["result"])
        elif grant_type == "client_signature":
            pass
        else:
            self.logger.error(f"Unknown grant_type {repr(hide_secret(request))} : {repr(hide_secret(response))}")

    def handle_error(self, message):
        if self.on_response_error:
            self.on_response_error(message)
        else:
            self.logger.error(message)
