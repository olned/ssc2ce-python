from typing import Optional, Callable

from ssc2ce.bitfinex.enums import ConfigFlag
from ssc2ce.common import L2Book

__all__ = ['Channel',
           # 'TickerChannel',
           # 'FundingTickerChannel',
           # 'TradesChannel',
           # 'FundingTradesChannel',
           # 'CandlesChannel',
           'BookChannel',
           'FundingBookChannel',
           # 'RawBookChannel'
           ]


class Channel:
    def __init__(self, channel_id: int, params: dict, flags: ConfigFlag):
        self.set_flags(flags)
        self.channel_id = channel_id
        self.params = params
        self.on_received: Optional[Callable[[list], bool]] = None
        self.timestamp_present = False
        self.time_stamp_position = None
        self.exchange_ts = None

    def set_on_received(self, handler: Callable[[list], bool]):
        self.on_received = handler

    def handle_message(self, data: list):
        if self.timestamp_present:
            self.exchange_ts = data[self.time_stamp_position]
        if self.on_received:
            self.on_received(data)

    def set_flags(self, flags: ConfigFlag):
        self.timestamp_present = ConfigFlag.TIMESTAMP in flags
        self.time_stamp_position = 3 if ConfigFlag.SEQ_ALL in flags else 2

    def check_sum(self, data: list):
        if self.timestamp_present:
            self.exchange_ts = data[self.time_stamp_position + 1]
        pass

    def heartbeat(self, data: list):
        if self.timestamp_present:
            self.exchange_ts = data[self.time_stamp_position]
        pass

# class TickerChannel(Channel):
#     def __init__(self, channel_id: int, symbol: str, pair: str):
#         Channel.__init__(self, channel_id)
#         self.symbol = symbol
#         self.pair = pair
#
#
# class FundingTickerChannel(Channel):
#     def __init__(self, channel_id: int, symbol: str, currency: str):
#         Channel.__init__(self, channel_id)
#         self.symbol = symbol
#         self.currency = currency
#
#
# class TradesChannel(Channel):
#     def __init__(self, channel_id: int, symbol: str, currency: str):
#         Channel.__init__(self, channel_id)
#         self.symbol = symbol
#         self.currency = currency


# class FundingTradesChannel(Channel):
#     def __init__(self, channel_id: int, symbol: str, currency: str):
#         Channel.__init__(self, channel_id)
#         self.symbol = symbol
#         self.currency = currency
#
#
# class CandlesChannel(Channel):
#     def __init__(self, channel_id: int, key: str
#                  ):
#         Channel.__init__(self, channel_id)
#         self.key = key


class BookChannel(Channel):
    def __init__(self, channel_id: int, symbol: str, params: dict, book: L2Book, flags: ConfigFlag):
        Channel.__init__(self, channel_id, params, flags)
        self.symbol = symbol
        self.precision = params['prec']
        self.freq = params['freq']
        self.length = params['len']
        self.pair = params['pair']
        self.book = book

    def handle_snapshot(self, message: list) -> bool:
        """

        :param message:
        :return:
        """
        self.book.clear()

        for item in message[1]:
            count = item[1]
            size = item[2]
            if count:
                if size < 0:
                    self.book.asks.add(item[0], -size)
                else:
                    self.book.bids.add(item[0], size)

        if self.book.on_book_setup and self.book.valid():
            self.book.on_book_setup(self.book)

        if self.timestamp_present and self.exchange_ts:
            self.book.set_exchange_ts(self.exchange_ts)

        return True

    def handle_update(self, message: list) -> bool:
        """

        :param message:
        :return:
        """
        item = message[1]
        count = item[1]
        size = item[2]
        if count:
            if size < 0:
                self.book.asks.update(item[0], -size)
            else:
                self.book.bids.update(item[0], size)
        else:
            if size < 0:
                self.book.asks.update(item[0], 0.)
            else:
                self.book.bids.update(item[0], 0.)

        if self.book.on_book_update and self.book.valid():
            self.book.on_book_update(self.book)

        if self.timestamp_present and self.exchange_ts:
            self.book.set_exchange_ts(self.exchange_ts)

        return True

    def handle_message(self, message: list):
        data = message[1]
        if self.timestamp_present:
            self.exchange_ts = message[self.time_stamp_position]

        if isinstance(data, list):
            if isinstance(data[0], list):
                self.handle_snapshot(message)
            else:
                self.handle_update(message)

        if self.on_received:
            self.on_received(data)


class FundingBookChannel(Channel):
    def __init__(self, channel_id: int, symbol: str, params: dict, flags: ConfigFlag):
        Channel.__init__(self, channel_id, params, flags)
        self.symbol = symbol
        self.precision = params['prec']
        self.freq = params['freq']
        self.length = params['len']
        self.currency = params['currency']
        # self.book = book

    def handle_snapshot(self, message: list) -> bool:
        """

        :param message:
        :return:
        """
        return True

    def handle_update(self, message: list) -> bool:
        """

        :param message:
        :return:
        """

        return True

    def handle_message(self, message: list):
        Channel.handle_message(self, message)


# class RawBookChannel(Channel):
#     def __init__(self, channel_id: int, symbol: str, params: dict):
#         Channel.__init__(self, channel_id)
#         self.symbol = symbol
#         self.precision = params['prec']
#         self.freq = params['freq']
#         self.length = params['len']
#         self.pair = params['pair']
#         # self.book = book
#
#     def handle_snapshot(self, message: list) -> bool:
#         """
#
#         :param message:
#         :return:
#         """
#         return True
#
#     def handle_update(self, message: list) -> bool:
#         """
#
#         :param message:
#         :return:
#         """
#
#         return True
#
#     def handle_message(self, message: list):
#         Channel.handle_message(self, message)
