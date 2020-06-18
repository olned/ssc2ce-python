import asyncio
import json
import logging
from time import time

import aiohttp

from ssc2ce.common.session import SessionWrapper
from ssc2ce.common.utils import resolve_route

from enum import IntEnum


class Bitfinex(SessionWrapper):
    _on_received_info: None

    class ConfigFlag(IntEnum):
        TIMESTAMP = 32768
        SEQ_ALL = 65536
        CHECKSUM = 131072

    class StatusFlag(IntEnum):
        MAINTENANCE = 0
        OPERATIVE = 1

    on_maintenance = None
    on_conf = None
    receipt_time = None
    is_connected = False
    subscriptions = []
    channel_handlers = {}

    def __init__(self,
                 flags: ConfigFlag = ConfigFlag.TIMESTAMP | ConfigFlag.SEQ_ALL):
        super().__init__()

        self.ws_api = 'wss://api-pub.bitfinex.com/ws/2'
        self.flags = flags
        self.logger = logging.getLogger(__name__)
        self._timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=20)
        self.routes = [
            ("subscribed", self.handle_subscribed),
            ("info", self.handle_info),
            ("conf", self.handle_conf),
            # ("", self.warn_handler),
        ]

    async def configure(self, flags: ConfigFlag = None):
        if flags is not None:
            self.flags = flags

        if self.flags is not None:
            request = dict(event="conf", flags=self.flags)
            await self.ws.send_json(request)

    async def subscribe(self, request, handler):
        self.subscriptions.append((request, handler))
        self.logger.info(f"subscribe {request}")
        await self.ws.send_json({
            "event": "subscribe",
            **request
        })

    @property
    def on_connect_ws(self):
        return None

    @on_connect_ws.setter
    def on_connect_ws(self, value):
        self._on_connect_ws_is_routine = asyncio.iscoroutinefunction(value)
        self._on_received_info = value

    def handle_message(self, message: str):
        data = json.loads(message)

        if isinstance(data, list):
            channel_id = data[0]
            handler = self.channel_handlers.get(channel_id)
            if handler:
                handler(data, self)
            else:
                self.logger.warning(f"Can't find handler for channel_id{channel_id}, {message}")
        elif isinstance(data, dict):
            if "event" in data:
                if asyncio.iscoroutinefunction(self.handle_event):
                    asyncio.ensure_future(self.handle_event(data))
                else:
                    self.handle_event(data)
            else:
                self.logger.warning(f"Unknown message {message}")
        else:
            self.logger.warning(f"Unknown message {message}")

    async def empty_handler(self, data):
        pass

    def handle_subscribed(self, message):
        self.logger.info(f"receive subscribed: {message}")
        idx = None
        for i, s in enumerate(self.subscriptions):
            if s[0].items() <= message.items():
                idx = i
                self.channel_handlers[message["chanId"]] = s[1]

        if idx:
            del self.subscriptions[idx]

    def handle_conf(self, message):
        """{'event': 'conf', 'status': 'OK', 'flags': 98304}"""
        self.logger.info(f"{message}")
        if self.on_conf:
            self.on_conf()

    def handle_info(self, message):
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
                asyncio.ensure_future(self.configure())
                if self._on_received_info:
                    if self._on_connect_ws_is_routine:
                        asyncio.ensure_future(self._on_received_info())
                    else:
                        self._on_received_info()
            else:
                if self.on_maintenance:
                    asyncio.ensure_future(self.on_maintenance(message))
        else:
            if self.on_maintenance:
                asyncio.ensure_future(self.on_maintenance(message))

    def warn_handler(self, message):
        self.logger.warning(f"Unsupported message {message}")

    def handle_event(self, message):
        event = message["event"]
        handler = resolve_route(event, self.routes)

        if handler:
            handler(message)
        else:
            self.logger.warning(f"Unhandled event:{event}, message:{repr(message)} .")
        return

    def close(self):
        super()._close()

    async def stop(self):
        await self.ws.close()
        self.close()
