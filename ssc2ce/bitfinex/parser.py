import json
from typing import Callable, Optional, Dict

from ssc2ce.bitfinex.icontroller import IBitfinexController
from ssc2ce.common.abstract_parser import AbstractParser
from .channel import *
from .enums import ConfigFlag
from ..common import L2Book


class BrokenSessionError(Exception):
    pass


class BitfinexParser(AbstractParser):
    """

    """

    def __init__(self):
        AbstractParser.__init__(self)
        self.controller: Optional[IBitfinexController] = None
        self.on_handle_version_info: Optional[Callable[[int, int], None]] = None
        self.on_conf: Optional[Callable[[str, int], None]] = None
        self.on_pong: Optional[Callable[[int, int], None]] = None
        self.on_error: Optional[Callable[[int], None]] = None
        self.on_info: Optional[Callable[[int], None]] = None
        self.subscriptions = []
        self.channel_handlers: Dict[int, Callable[[list], None]] = {}
        self.books = {}
        self.last_message = None

        self.flags = ConfigFlag
        self.timestamp_present = False
        self.time_stamp_position = None
        self.sequence_present = False
        self.current_sequence = 0

        self.handlers: Dict[str: Callable[[dict], bool]] = {
            "subscribed": self.handle_subscribed,
            "info": self.handle_info,
            "pong": self.handle_pong,
            "conf": self.handle_conf,
            "unsubscribed": self.handle_unsubscribed,
        }

        self.subscription_handlers: Dict[str: Callable[[dict], Channel]] = {
            "book": self.handle_book_subscribed,
            "trades": self.handle_trades_subscribed,
            "ticker": self.handle_ticker_subscribed,
            "candles": self.handle_candles_subscribed,
        }

        self.channels: Dict[int: Channel] = {}

    def set_controller(self, controller: IBitfinexController):
        self.controller = controller
        self.on_pong = controller.handle_pong
        self.on_handle_version_info = controller.handle_version_and_status
        self.on_error = controller.handle_error

    def parse(self, message) -> bool:
        self.last_message = message
        data = json.loads(message)

        if isinstance(data, list):
            if self.sequence_present:
                self.current_sequence += 1
                """
                Oleg Nedbaylo: It would be more ease to get sequence from the end of list but Bitfinex writes:
                    "!Array Length. Message (JSON array) lengths should never be hardcoded. New fields may be appended 
                                    at the end of a message without changing version."
                """
                seq_pos = 2 if not isinstance(data[1], str) or data[1] == 'hb' else 3
                new_seq = data[seq_pos]
                if self.current_sequence != new_seq:
                    raise BrokenSessionError(f"expected {self.current_sequence} received {new_seq} "
                                             f"in message {self.last_message}")

            if isinstance(data[1], str):
                if data[1] == 'cs':
                    self.channels[data[0]].check_sum(data)
                elif data[1] == 'hb':
                    self.channels[data[0]].heartbeat(data)
                else:
                    raise Exception(f"Unknown type of message {message}")
            else:
                self.channels[data[0]].handle_message(data)
            return True
        elif isinstance(data, dict):
            if "error" in data:
                if self.on_error:
                    self.on_error(data["error_code"])
                    return True
            else:
                event_mane = data.get("event")
                if event_mane:
                    handler: Optional[Callable[[dict], bool]] = self.handlers.get(event_mane)
                    if handler:
                        ok = handler(data)
                        return ok

        return False

    def set_on_book_setup(self, handler) -> None:
        self.on_book_setup = handler

        for book in self.books.values():
            book.set_on_book_setup(handler)

    def set_on_book_update(self, handler) -> None:
        self.on_book_update = handler

        for book in self.books.values():
            book.set_on_book_update(handler)

    def get_book(self, instrument: str) -> L2Book:
        book: L2Book = self.books.get(instrument)
        if book is None:
            book = L2Book(instrument)

            if self.on_book_setup:
                book.set_on_book_setup(self.on_book_setup)

            if self.on_book_update:
                book.set_on_book_update(self.on_book_update)

            self.books[instrument] = book

        return book

    def handle_info(self, message: dict) -> bool:
        if "version" in message:
            """
            {
               "event": "info",
               "version":  VERSION,
               "platform": {
                  "status": 1
               }
            }
            """
            if self.on_handle_version_info:
                self.on_handle_version_info(message["version"], message["platform"]["status"])
            return True

        """
        {
           "event":"info",
           "code": CODE,
           "msg": MSG
        }
        """

        if self.on_info:
            self.on_info(message["code"])
            return True

    def handle_conf(self, message: dict) -> bool:
        """{'event': 'conf', 'status': 'OK', 'flags': 98304}"""
        status = message["status"]
        self.flags = ConfigFlag(message.get("flags", 0))
        self.timestamp_present = self.flags & ConfigFlag.TIMESTAMP
        self.sequence_present = self.flags & ConfigFlag.SEQ_ALL

        if self.flags:
            self.time_stamp_position = 3 if self.sequence_present else 2

        for channel in self.channels.values():
            channel.set_flags(self.flags)

        if self.on_conf:
            self.on_conf(status, self.flags)
        return True

    def handle_pong(self, message: dict) -> bool:
        if self.on_pong:
            self.controller.handle_pong(message["ts"], message["cid"])
        return True

    def handle_subscribed(self, message: dict) -> bool:
        channel_name = message.get('channel')
        handler: Optional[Callable[[dict], Channel]] = self.subscription_handlers.get(channel_name)
        if handler:
            channel = handler(message)

            idx = None
            y = [(i[0], i[1] if isinstance(i[1], str) else str(i[1])) for i in message.items()]

            for i, s in enumerate(self.subscriptions):
                ok = True
                z = [(i[0], i[1] if isinstance(i[1], str) else str(i[1])) for i in s[0].items()]
                for x in z:
                    if x not in y:
                        ok = False
                        break

                if ok:
                    idx = i
                    if s[1]:
                        channel.set_on_received(s[1])
                    break

            if idx is not None:
                del self.subscriptions[idx]

            return True

        return False

    def handle_book_subscribed(self, message: dict) -> Channel:
        channel_id = message['chanId']
        symbol = message['symbol']
        book = self.get_book(symbol)
        precision = message['prec']
        if precision == 'R0':
            channel = Channel(channel_id, message)
        elif symbol[0] == 't':
            channel = BookChannel(channel_id, symbol, message, book, self.flags)
        else:
            channel = FundingBookChannel(channel_id, symbol, message, self.flags)

        self.channels[channel_id] = channel
        return channel

    def handle_trades_subscribed(self, message: dict) -> Channel:
        channel_id = message['chanId']
        symbol = message['symbol']
        if symbol[0] == 't':
            channel = Channel(channel_id, message, self.flags)
        else:
            channel = Channel(channel_id, message, self.flags)

        self.channels[channel_id] = channel
        return channel

    def handle_ticker_subscribed(self, message: dict) -> Channel:
        channel_id = message['chanId']
        symbol = message['symbol']
        if symbol[0] == 't':
            channel = Channel(channel_id, message, self.flags)
        else:
            channel = Channel(channel_id, message, self.flags)
        self.channels[channel_id] = channel
        return channel

    def handle_candles_subscribed(self, message: dict) -> Channel:
        channel_id = message['chanId']
        channel = Channel(channel_id, message, self.flags)

        self.channels[channel_id] = channel
        return channel

    def handle_unsubscribed(self, message: dict) -> bool:
        self.last_message = message
        return False
