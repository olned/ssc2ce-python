import logging

import aiohttp

from .session import SessionWrapper
from .utils import resolve_route

from enum import IntEnum


class Bitfinex(SessionWrapper):
    class ConfigFlag(IntEnum):
        TIMESTAMP = 32768
        SEQ_ALL = 65536
        CHECKSUM = 131072

    class StatusFlag(IntEnum):
        MAINTENANCE = 0
        OPERATIVE = 1

    ws: aiohttp.ClientWebSocketResponse = None
    on_connect_ws = None
    on_close_ws = None
    on_maintenance = None
    on_conf = None

    ws_api = 'wss://api-pub.bitfinex.com/ws/2'

    last_message = None
    is_connected = False
    subscriptions = []
    channel_handlers = {}

    def __init__(self,
                 flags: ConfigFlag = ConfigFlag.TIMESTAMP | ConfigFlag.SEQ_ALL):
        super().__init__()

        self.flags = flags
        self.logger = logging.getLogger(__name__)

        self._timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=20)

        self.on_message = self.handle_message
        # self.on_connect = self.configure
        self.routes = [
            ("subscribed", self.handle_subscribed),
            ("info", self.handle_info),
            ("conf", self.handle_conf),
            # ("", self.warn_handler),
        ]

        # self.channel_route = []

    async def configure(self, flags: ConfigFlag = None):
        if flags is not None:
            self.flags = flags

        if self.flags is not None:
            request = dict(event="conf", flags=self.flags)
            await self.ws.send_json(request)

    async def subscribe(self, request, handler):
        self.subscriptions.append((request, handler))
        await self.ws.send_json({
            "event": "subscribe",
            **request
        })

    async def run_receiver(self):
        self.ws = await self._session.ws_connect(self.ws_api)

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

    async def handle_message(self, message: aiohttp.WSMessage):
        if message.type == aiohttp.WSMsgType.TEXT:
            data = message.json()

            if isinstance(data, list):
                channel_id = data[0]
                handler = self.channel_handlers.get(channel_id)
                if handler:
                    await handler(data)
                else:
                    self.logger.warning(f"Can't find handler for channel_id{channel_id}, {data}")
            elif isinstance(data, dict):
                if "event" in data:
                    await self.handle_event(data)
                else:
                    self.logger.warning(f"Unknown message {message.data}")
            else:
                self.logger.warning(f"Unknown message {message.data}")
        else:
            self.logger.warning(f"Unknown type of message {repr(message)}")

    async def empty_handler(self, data):
        pass

    async def handle_subscribed(self, message):
        self.logger.info(f"receive subscribed: {message}")
        idx = None
        for i, s in enumerate(self.subscriptions):
            if s[0].items() <= message.items():
                idx = i
                self.channel_handlers[message["chanId"]] = s[1]

        if idx:
            del self.subscriptions[idx]

    async def handle_conf(self, message):
        """{'event': 'conf', 'status': 'OK', 'flags': 98304}"""
        self.logger.info(f"{message}")
        if self.on_conf:
            await self.on_conf()

    async def handle_info(self, message):
        """
        Handle an info message that contains the actual version of the websocket stream, along with a platform status
        flag (1 for operative, 0 for maintenance
        :param message: Info messages {'event': 'info', 'version': 2, 'serverId': ..., 'platform': {'status': 1}}
          version: the actual version of the websocket stream must be 2
          status: a platform status flag (1 for operative, 0 for maintenance).
        :return:
        """
        self.logger.info(f"{message}")

        if message["version"] != 2:
            raise NotImplemented(f"Bitfinex connector support only version 2 but receive {message}")

        if message["platform"]["status"] == 1:
            if not self.is_connected:
                await self.configure()
                if self.on_connect_ws:
                    await self.on_connect_ws()
            else:
                if self.on_maintenance:
                    await self.on_maintenance(message)
        else:
            if self.on_maintenance:
                await self.on_maintenance(message)

    async def warn_handler(self, message):
        self.logger.warning(f"Unsupported message {message}")

    async def handle_event(self, message):
        event = message["event"]
        handler = resolve_route(event, self.routes)

        if handler:
            return await handler(message)

        self.logger.warning(f"Unhandled event:{event}, message:{repr(message)} .")
        return

    def close(self):
        super()._close()

    async def stop(self):
        await self.ws.close()
