import asyncio
import logging

import aiohttp
from time import time

logger = logging.getLogger(__name__)


class SessionWrapper:
    """

    Handlers:
     - on_connect_ws - Called after the connection is established.
            If auth_type is not equivalent to AuthType.NONE,
            on_connect_ws will be set to self.auth_login;
     - on_close_ws - Called after disconnection, default value is None;
     - on_authenticated - Called after authentication is confirmed, default value is None;
     - on_message - Called when a message is received, default value is self.handle_message;
     - on_before_handling -
    """

    __internal_session: bool = True
    __is_session: bool = False
    __session: aiohttp.ClientSession = None
    _timeout: aiohttp.ClientTimeout = None
    ws: aiohttp.ClientWebSocketResponse = None

    def __init__(self, timeout: aiohttp.ClientTimeout = None, session: aiohttp.ClientSession = None):
        if session:
            self._session = session
            self.__internal_session = False

        if timeout:
            self._timeout = timeout
        else:
            self._timeout = aiohttp.ClientTimeout(total=20)

        self._on_message_is_routine = False
        self._on_message = None

        self._on_connect_ws_is_routine = None
        self._on_connect_ws = None
        self.on_close_ws = None
        self.on_before_handling = None

        self.ws_api = None
        self.logger = logging.getLogger(__name__)
        self.receipt_time = None
        self.last_message = None

    @property
    def _session(self):
        if not self.__is_session:
            self.__check_session()
        return self.__session

    @_session.setter
    def _session(self, value):
        self.__is_session = True
        self.__internal_session = False
        self.__session = value

    def __check_session(self):
        if not self.__is_session:
            self.__is_session = True
            self.__internal_session = True
            self.__session = aiohttp.ClientSession(timeout=self._timeout)

    def __del__(self):
        self._close()

    def __enter__(self):
        self.__check_session()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._close()

    def _close(self):
        if self.__internal_session and self.__session:
            asyncio.ensure_future(self.__session.close())
            self.__is_session = False

    @property
    def on_message(self):
        return self._on_message

    @on_message.setter
    def on_message(self, value):
        self._on_message_is_routine = asyncio.iscoroutinefunction(value)
        self._on_message = value

    @property
    def on_connect_ws(self):
        return self._on_connect_ws

    @on_connect_ws.setter
    def on_connect_ws(self, value):
        self._on_connect_ws_is_routine = asyncio.iscoroutinefunction(value)
        self._on_connect_ws = value

    async def run_receiver(self):
        """
        Establish a connection and start the receiver loop.
        :return:
        """
        self.ws = await self._session.ws_connect(self.ws_api)
        if self.on_connect_ws:
            if asyncio.iscoroutinefunction(self.on_connect_ws):
                await self.on_connect_ws()
            else:
                self.on_connect_ws()

        # A receiver loop
        while self.ws and not self.ws.closed:
            message = await self.ws.receive()
            self.receipt_time = time()
            self.last_message = message

            if message.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR):
                self.logger.warning(f"Connection close {repr(message)}")
                if self.on_close_ws:
                    await self.on_close_ws()

                continue
            if message.type == aiohttp.WSMsgType.CLOSING:
                self.logger.debug(f"Connection closing {repr(message)}")
                continue

            if message.type == aiohttp.WSMsgType.TEXT:
                if self.on_before_handling:
                    self.on_before_handling(message.data)

                processed = False
                if self._on_message:
                    if self._on_message_is_routine:
                        processed = await self._on_message(message.data)
                    else:
                        processed = self._on_message(message.data)

                if not processed:
                    self.handle_message(message.data)
            else:
                self.logger.warning(f"Unknown type of message {repr(message)}")

    def handle_message(self, message: str):
        pass
