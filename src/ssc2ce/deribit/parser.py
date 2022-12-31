import json
import logging
from typing import Callable, Dict, Optional

from ssc2ce.common.abstract_parser import AbstractParser
from ssc2ce.deribit.l2_book import DeribitL2Book
from ssc2ce.common.exceptions import BrokenOrderbook


class DeribitParser(AbstractParser):
    """

    """

    def __init__(self):
        AbstractParser.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.deprecated_already_warn = False
        self._handler_broken_orderbook: Optional[Callable[[str, int, int], None]] = None
        self._books: Dict[str, DeribitL2Book] = {}

    async def handle_message(self, message):
        if not self.deprecated_already_warn:
            self.deprecated_already_warn = True
            self.logger.warning("The handle_message method of DeribitParser is deprecated, please use parse instead")
        self.parse(message)

    def parse(self, message) -> bool:
        data = json.loads(message)

        return self.handle_method_message(data)

    def handle_method_message(self, data: dict) -> bool:
        method = data.get("method")
        processed = False
        if method and method == "subscription":
            params = data["params"]
            channel = params["channel"]
            if channel.startswith("book."):
                params_data = params["data"]
                instrument = params_data["instrument_name"]
                book = self.get_book(instrument)

                if "prev_change_id" in params_data:
                    self.handle_update(book, params_data)
                    if self._on_book_update:
                        self._on_book_update(book)
                else:
                    self.handle_snapshot(book, params_data)
                    if self._on_book_setup:
                        self._on_book_setup(book)

                processed = True

        return processed

    def get_book(self, instrument: str) -> DeribitL2Book:
        book = self._books.get(instrument)
        if book is None:
            book = DeribitL2Book(instrument)
            self._books[instrument] = book

        return book

    @staticmethod
    def handle_snapshot(book: DeribitL2Book, message: dict) -> None:
        """

        :param book:
        :param message:
        :return:
        """
        book.clear()

        book.change_id = message["change_id"]
        book.timestamp = message["timestamp"]
        for i in message['bids']:
            book.bids.add(i[1], i[2])

        for i in message['asks']:
            book.asks.add(i[1], i[2])

    def handle_update(self, book: DeribitL2Book, message: dict) -> None:
        """

        :param book:
        :param message:
        :return:
        """
        prev_change_id = message["prev_change_id"]
        if prev_change_id != book.change_id:
            if self._handler_broken_orderbook:
                self._handler_broken_orderbook(book.instrument(), prev_change_id, book.change_id)
            else:
                raise BrokenOrderbook(book.instrument(), prev_change_id, book.change_id)

        book.change_id = message["change_id"]
        book.timestamp = message["timestamp"]
        for change in message['bids']:
            if change[0] == 'new':
                book.bids.add(price=change[1], size=change[2])
            elif change[0] == 'delete':
                book.bids.delete(change[1])
            else:
                book.bids.update(price=change[1], size=change[2])

        for change in message['asks']:
            if change[0] == 'new':
                book.asks.add(price=change[1], size=change[2])
            elif change[0] == 'delete':
                book.asks.delete(change[1])
            else:
                book.asks.update(price=change[1], size=change[2])
