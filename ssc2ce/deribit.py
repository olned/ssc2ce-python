import logging

import aiohttp

from .exceptions import Ssc2ceError
from .common import AuthType
from .session import SessionWrapper
from .utils import resolve_route, hide_secret, IntId


class Deribit(SessionWrapper):
    ws: aiohttp.ClientWebSocketResponse = None
    on_connect_ws = None
    on_close_ws = None
    on_message = None
    on_authenticated = None
    on_token = None
    on_subscription = None
    on_response_error = None
    on_handle_response = None

    requests = {}
    auth_params: dict = None

    last_message = None

    def __init__(self,
                 client_id: str = None,
                 client_secret: str = None,
                 scope: str = "session",
                 testnet: bool = True,
                 auth_type: AuthType = AuthType.NONE,
                 get_id=IntId().get_id):
        super().__init__()

        self.ws_api = f"wss://{'test' if testnet else 'www'}.deribit.com/ws/api/v2/"
        self.get_id = get_id
        self.logger = logging.getLogger(__name__)

        if auth_type & (AuthType.CREDENTIALS | AuthType.SIGNATURE):
            if client_secret is None or client_id is None:
                raise Ssc2ceError(f" Authentication {str(auth_type)} need client_id and client_secret")

        if auth_type == AuthType.SIGNATURE:
            raise NotImplemented(f"Authentication {str(auth_type)} for Deribit is not implemented.")

        self.auth_type = auth_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self._timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=20)

        self.on_message = self.handle_message
        self.method_routes = [
            ("heartbeat", self.handle_heartbeat),
        ]
        self.response_routes = [
            ("public/auth", self.handle_auth),
            ("", self.empty_handler),
        ]

    async def run_receiver(self):
        self.ws = await self._session.ws_connect(self.ws_api)
        if self.on_connect_ws:
            await self.on_connect_ws()

        while self.ws and not self.ws.closed:
            message = await self.ws.receive()
            self.last_message = message

            if message.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR):
                self.logger.warning(f"Connection close {repr(message)}")
                if self.on_close_ws:
                    await self.on_close_ws()

                continue
            if message.type == aiohttp.WSMsgType.CLOSING:
                self.logger.debug(f"Connection closing {repr(message)}")
                continue

            if self.on_message:
                await self.on_message(message)

    async def send_public(self, request):
        request_id = self.get_id()
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            **request
        }
        self.requests[request_id] = request
        self.logger.info(f"sending:{repr(hide_secret(request))}")
        await self.ws.send_json(request)
        return request_id

    async def send_private(self, request):
        request_id = self.get_id()
        access_token = self.auth_params["access_token"]
        request["params"]["access_token"] = access_token

        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            **request
        }
        self.requests[request_id] = request
        self.logger.info(f"sending:{repr(hide_secret(request))}")
        await self.ws.send_json(request)
        return request_id

    async def send(self, request):
        method = request["method"]
        if method.starts("public/"):
            request_id = await self.send_public(request)
        else:
            request_id = await self.send_private(request)

        return request_id

    async def auth_login(self):
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

    async def auth_client_credentials(self, client_id, client_secret, scope: str = None):
        """

        :param client_id: using the access key
        :param client_secret: and access secret that can be found on the API page on the website
        :param scope:
            connection, session, session:name,
            trade:[read, read_write, none],
            wallet:[read, read_write, none],
            account:[read, read_write, none]
        :return:
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

    async def auth_password(self, username, password, scope: str = None):
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

    async def auth_refresh_token(self):
        msg = {
            "method": "public/auth",
            "params": {
                "grant_type": "refresh_token",
                "refresh_token": self.auth_params["refresh_token"]
            }
        }

        request_id = await self.send_public(msg)
        return request_id

    async def auth_logout(self):
        msg = {
            "method": "private/logout",
            "params": {}
        }

        request_id = await self.send_private(msg)
        return request_id

    # async def auth_client_signature(self, client_id, client_secret, scope: str = None):
    #     msg = {
    #         "method": "public/auth",
    #         "params": {
    #             "grant_type": "password",
    #             "username": client_id,
    #             "password": client_secret
    #         }
    #     }
    #
    #     if scope:
    #         msg["scope"] = scope
    #
    #     await self.send_public(msg)
    #     return

    async def set_heartbeat(self, interval: int = 15):
        request_id = await self.send_public({"method": "public/set_heartbeat", "params": {"interval": interval}})
        return request_id

    async def disable_heartbeat(self):
        request_id = await self.send_public({"method": "public/disable_heartbeat", "params": {}})
        return request_id

    async def handle_message(self, message: aiohttp.WSMessage):
        if message.type == aiohttp.WSMsgType.TEXT:
            data = message.json()
            self.logger.debug(f"handling:{repr(hide_secret(data))}")

            if "method" in data:
                await self.handle_method_message(data)
            else:
                if "id" in data:
                    if "error" in data:
                        if self.on_response_error:
                            await self.on_response_error()
                        else:
                            self.logger.error(f"Receive error {repr(data)}")
                    else:
                        request_id = data["id"]
                        request = self.requests.get(request_id)
                        if request:
                            await self.handle_response(request=request, response=data)

                            del self.requests[request_id]
                        else:
                            if self.on_handle_response:
                                await self.on_handle_response(data)
                            else:
                                self.logger.warning(
                                    f"Unknown id:{request_id}, the on_handle_response event must be defined."
                                    f" Unhandled message {data}")

                else:
                    self.logger.warning(f"Unsupported message {message.data}")
        else:
            self.logger.warning(f"Unknown type of message {repr(message)}")

    async def empty_handler(self, **kwargs):
        self.logger.debug(f"{repr(kwargs)}")

    async def handle_response(self, request, response):
        method = request["method"]
        handler = resolve_route(method, self.response_routes)

        if handler:
            return await handler(request=request, response=response)

        self.logger.warning(f"Unhandled method:{method} response:{repr(response)} to request:{repr(request)}.")
        return

    async def handle_method_message(self, data):
        method = data["method"]
        handler = resolve_route(method, self.method_routes)

        if handler:
            return await handler(data)

        self.logger.warning(f"Unhandled message:{repr(data)}.")
        return

    async def handle_heartbeat(self, data):
        if data["params"]["type"] == "test_request":
            await self.send_public({"method": "public/test", "params": {}})

        return

    async def handle_auth(self, request, response):
        self.auth_params = response["result"]
        grant_type = request["params"]["grant_type"]
        if grant_type == "":
            if self.on_token:
                await self.on_token(response["result"])
        elif grant_type in ("client_credentials", "password"):
            if self.on_authenticated:
                await self.on_authenticated()
            if self.on_token:
                await self.on_token(response["result"])
        elif grant_type == "client_signature":
            pass
        else:
            self.logger.error(f"Unknown grant_type {repr(hide_secret(request))} : {repr(hide_secret(response))}")

    def close(self):
        super()._close()

    async def stop(self):
        if self.auth_params:
            await self.auth_logout()
        else:
            await self.ws.close()
