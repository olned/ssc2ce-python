import json
import logging
from typing import Callable

from ssc2ce.coinbase_pro.l2_book import L2Book
from ssc2ce.common.abstract_parser import AbstractParser


class CoinbaseParser(AbstractParser):
    """

    """

    _on_subscriptions: Callable[[dict], bool] = None
    _on_heartbeat: Callable[[dict], bool] = None

    def __init__(self):
        AbstractParser.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.deprecated_already_warn = False
        self.books = {}
        self.routes = {
            "l2update": self.handle_update,
            "snapshot": self.handle_snapshot,
            "subscriptions": self.handle_subscriptions,
            "heartbeat": self.handle_heartbeat
        }

    def set_on_subscriptions(self, handler) -> None:
        self._on_subscriptions = handler

    def set_on_heartbeat(self, handler) -> None:
        self._on_heartbeat = handler

    def parse(self, message) -> bool:
        data = json.loads(message)

        if isinstance(data, dict):
            handler: Callable[[dict], bool] = self.routes.get(data.get('type'))
            if handler:
                return handler(data)

            return False

    def get_book(self, instrument: str) -> L2Book:
        book: L2Book = self.books.get(instrument)
        if book is None:
            book = L2Book(instrument)
            self.books[instrument] = book

        return book

    def handle_snapshot(self, message: dict) -> bool:
        """

        :param message:
        :return:
        """
        book = self.get_book(message["product_id"])
        book.clear()

        for i in message['bids']:
            book.bids.add(float(i[0]), float(i[1]))

        for i in message['asks']:
            book.asks.add(float(i[0]), float(i[1]))

        if self._on_book_setup:
            self._on_book_setup(book)

        return True

    def handle_update(self, message: dict) -> bool:
        """

        :param message:
        :return:
        """
        book = self.get_book(message["product_id"])
        book.time = message["time"]
        for change in message['changes']:
            if change[0] == 'sell':
                book.asks.update(price=float(change[1]), size=float(change[2]))
            else:
                book.bids.update(price=float(change[1]), size=float(change[2]))

        if self._on_book_update:
            self._on_book_update(book)
        return True

    def handle_subscriptions(self, data: dict) -> bool:
        if self._on_subscriptions:
            return self._on_subscriptions(data)

        return False

    def handle_heartbeat(self, data: dict) -> bool:
        if self._on_heartbeat:
            return self._on_heartbeat(data)

        return False
