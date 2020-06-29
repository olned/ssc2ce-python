import asyncio
import logging
from typing import Optional, Callable, Any, Awaitable

from ssc2ce.bitfinex.enums import ConfigFlag
from ssc2ce.bitfinex.icontroller import IBitfinexController
from ssc2ce.bitfinex.parser import BitfinexParser
from ssc2ce.common.session import SessionWrapper


class Bitfinex(SessionWrapper, IBitfinexController):
    _user_on_connect: Optional[Callable[[], Any]] = None
    _user_async_on_connect: Optional[Callable[[], Awaitable[Any]]] = None

    on_conf = None
    receipt_time = None
    is_connected = False

    def __init__(self,
                 flags: ConfigFlag = ConfigFlag.TIMESTAMP | ConfigFlag.SEQ_ALL):
        """

        :param flags: a bitwise XOR of the different options:
            8 - enable all decimals as strings
            TIME_S - 32 - Enable all timestamps as strings
            TIMESTAMP - 32768 - Adds a Timestamp in milliseconds to each received event.
            SEQ_ALL - 65536 - Adds sequence numbers to each event.
            OB_CHECKSUM - 131072 - Enable checksum for every book iteration.
        """

        super().__init__()
        self.server_version = None
        self.on_check_version: Callable[[int], bool] = self.check_version
        self.on_maintenance = None
        self.ws_api = 'wss://api-pub.bitfinex.com/ws/2'
        self.flags = flags
        self.logger = logging.getLogger(__name__)
        self.parser = BitfinexParser()
        self.parser.set_controller(self)
        self.pong_cid = None
        self.pong_ts = None
        self.last_err_code = None
        self.on_message = self.parser.parse
        self.on_handle_version_info = self.handle_version_and_status

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

    def handle_message(self, message: str):
        self.logger.warning(f"Unhandled message {message}")

    def check_version(self, version: int) -> bool:
        """

        :param version:
        :return:
        """
        self.server_version = version
        if version != 2:
            self.logger.error(f"Bitfinex connector support only version 2 but receive {version}")
            return False
        else:
            return True

    def check_status(self, status: int):
        """

        :param status:
        :return:
        """
        if status == 1:
            if not self.is_connected:
                asyncio.ensure_future(self.configure())
                if self._user_async_on_connect:
                    asyncio.ensure_future(self._user_async_on_connect())
                elif self._user_on_connect:
                    self._user_on_connect()
            else:
                if self.on_maintenance:
                    asyncio.ensure_future(self.on_maintenance(status))
        else:
            if self.on_maintenance:
                asyncio.ensure_future(self.on_maintenance(status))

    def handle_version_and_status(self, version_no: int, status: int):
        if not self.check_version(version_no):
            asyncio.ensure_future(self.stop)
            return

        self.check_status(status=status)

    def handle_error(self, error_code: int):
        self.last_err_code = error_code
        self.logger.error(self.parser.last_message)

    def handle_pong(self, ts: int, cid: int):
        self.pong_ts = ts
        self.pong_cid = cid

    def handle_info(self, info_code: int):
        self.logger.warning("NOT IMPLEMENTED JET")
        if info_code == 20051:
            pass
        elif info_code == 20060:
            pass
        elif info_code == 20061:
            pass
        else:
            pass

    async def configure(self, flags: ConfigFlag = None):
        """

        :param flags:
        :return:
        """
        if flags is not None:
            self.flags = flags

        if self.flags is not None:
            request = dict(event="conf", flags=self.flags)
            await self.ws.send_json(request)

    async def request_ping(self):
        """
        Send ping request

        :return:
        """

        await self.ws.send_json({
            "event": "ping"
        })

    async def subscribe(self,
                        request,
                        handler: Optional[Callable[[list], None]] = None):
        """

        :param request:
        :param handler:
        :return:
        """
        self.parser.subscriptions.append((request, handler))
        self.logger.info(f"subscribe {request}")
        await self.ws.send_json({
            "event": "subscribe",
            **request
        })

    async def subscribe_ticker(self, symbol: str,
                               handler: Optional[Callable[[list], None]] = None):
        """
        Subscribe to ticker

        :param symbol: 	Trading pair or funding currency
        :param handler:
        :return:
        """

        await self.subscribe({
            "event": "subscribe",
            "channel": "ticker",
            "symbol": symbol
        }, handler)

    async def subscribe_trades(self, symbol: str,
                               handler: Optional[Callable[[list], None]] = None):
        """
        Subscribe to trades channel

        :param symbol: Trading pair or funding currency
        :param handler:
        :return:
        """

        await self.subscribe({
            "event": "subscribe",
            "channel": "trades",
            "symbol": symbol
        }, handler)

    async def subscribe_book(self,
                             symbol: str,
                             precision: int = 0,
                             frequency: int = 0,
                             length: int = 25,
                             handler: Optional[Callable[[list], None]] = None):
        """

        :param symbol: Trading pair or funding currency
        :param precision: Level of price aggregation: 0, 1, 2, 3, 4
        :param frequency: Frequency of updates: 0 - realtime, 1 - 2sec
        :param length: Number of price points: 25, 100
        :param handler:
        :return:
        """

        await self.subscribe({
            "event": "subscribe",
            "channel": "book",
            "symbol": symbol,
            "prec": f"P{precision}",
            "freq": f"F{frequency}",
            "len": length
        }, handler)

    async def subscribe_raw_book(self,
                                 pair: str,
                                 length: int = 25,
                                 handler: Optional[Callable[[list], None]] = None):
        """

        :param pair: Trading pair or funding currency
        :param length: Number of price points: 1, 25, 100
        :param handler:
        :return:
        """

        await self.subscribe({
            "event": "subscribe",
            "channel": "book",
            "pair": pair,
            "prec": "R0",
            "len": length
        }, handler)

    async def subscribe_candles(self, symbol: str, time_frame: str = "1m",
                                handler: Optional[Callable[[list], None]] = None):
        """

        :param symbol: Trading pair or funding currency
        :param time_frame: 1m, 5m, 15m, 30m, 1h, 3h, 6h, 12h, 1D, 7D, 14D, 1M
        :param handler:
        :return:
        """

        await self.subscribe({
            "event": "subscribe",
            "channel": "candles",
            "key": f"trade:{time_frame}:{symbol}"
        }, handler)
