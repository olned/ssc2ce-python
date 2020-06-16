import asyncio
import json
import logging

from ssc2ce.deribit.l2_book import DeribitL2Book, L2Book
from ssc2ce.common.exceptions import BrokenOrderBook


class DeribitParser:
    """

    """

    def __init__(self):
        self._on_book_setup = None
        self._on_book_update = None
        self.logger = logging.getLogger(__name__)
        self.deprecated_already_warn = False
        self.books = {}

    def set_on_book_setup(self, handler) -> None:
        self._on_book_setup = handler

    def set_on_book_update(self, handler) -> None:
        self._on_book_update = handler

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

    def get_book(self, instrument: str) -> L2Book:
        book: L2Book = self.books.get(instrument)
        if book is None:
            book = L2Book(instrument)
            self.books[instrument] = book

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

    @staticmethod
    def handle_update(book: DeribitL2Book, message: dict) -> None:
        """

        :param book:
        :param message:
        :return:
        """
        prev_change_id = message["prev_change_id"]
        if prev_change_id != book.change_id:
            raise BrokenOrderBook(book.instrument, prev_change_id, book.change_id)

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
