import json
import logging
from typing import Callable, Dict

from ssc2ce.common.abstract_parser import AbstractParser
from ssc2ce.cex.l2_book import CexL2Book
from ssc2ce.common.exceptions import BrokenOrderbook


class CexParser(AbstractParser):
    """

    """

    def __init__(self):
        AbstractParser.__init__(self)
        self._routes: Dict[str, Callable[[dict], None]] = None
        self._handler_broken_orderbook: Callable[[str, int, int], None] = None
        self._routes = {
            # 'auth', self.handle_auth,
            # 'balance', self.handle_balance,
            # 'disconnecting', self.handle_disconnecting,
            # 'get-balance', self.handle_get_balance,
            'md_update': self.handle_md_update,
            # 'obalance', self.handle_obalance,
            # 'open-orders', self.handle_open_orders,
            # 'order', self.handle_order,
            'order-book-subscribe': self.handle_order_book_subscribe,
            # 'order-book-unsubscribe': self.handle_order_book_unsubscribe,
            # 'ping': self.handle_ping,
            # 'tick': self.handle_tick,
            # 'tx', self.handle_tx,
        }
        self.logger = logging.getLogger(__name__)
        self.books = {}

    def parse(self, message: str) -> bool:
        data = json.loads(message)
        message_type = data.get('e')
        processed: bool = False

        if message_type:
            handler = self._routes.get(message_type)
            if handler:
                handler(data)
                processed = True
        else:
            self.logger.error(message)

        return processed

    def get_book(self, instrument: str) -> CexL2Book:
        book: CexL2Book = self.books.get(instrument)
        if book is None:
            book = CexL2Book(instrument)
            self.books[instrument] = book

        return book

    def handle_order_book_subscribe(self, message: dict) -> None:
        """

        :param message:
        :return:
        """
        ok = message.get('ok')
        if ok != 'ok':
            self.logger.error(message)
            return

        data = message["data"]
        book = self.get_book(data["pair"])
        book.clear()
        book.sequence = data["id"]
        book.time = data["timestamp"]

        for price, size in data['bids']:
            book.bids.add(price, size)

        for price, size in data['asks']:
            book.asks.add(price, size)

        if self._on_book_setup:
            self._on_book_setup(book)

    def handle_md_update(self, message: dict) -> None:
        """

        :param message:
        :return:
        """

        data = message["data"]
        book = self.get_book(data["pair"])
        book.sequence += 1
        if book.sequence != data["id"]:
            if self._handler_broken_orderbook:
                self._handler_broken_orderbook(data["pair"], book.sequence - 1, data["id"])
            else:
                raise BrokenOrderbook(data["pair"], book.sequence - 1, data["id"])

        book.time = data["time"]
        for price, size in data['bids']:
            book.bids.update(price, size)

        for price, size in data['asks']:
            book.bids.update(price, size)

        if self._on_book_update and book.valid():
            self._on_book_update(book)
