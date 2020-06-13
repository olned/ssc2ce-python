import json
import logging

from ssc2ce.common.utils import hide_secret
from ssc2ce.deribit.icontroller import IDeribitController
from ssc2ce.deribit.iparser import IDeribitParser
from ssc2ce.deribit.l2_book import L2Book


class DeribitParser(IDeribitParser):
    """

    """

    def __init__(self, controller: IDeribitController):
        self.on_book_setup = None
        self.on_book_update = None
        self.logger = logging.getLogger(__name__)
        self.controller = controller

        self.books = {}

    async def handle_message(self, message):
        data = json.loads(message)

        if "method" in data:
            await self.handle_method_message(data)
        else:
            if "id" in data:
                if "error" in data:
                    await self.controller.handle_error(data)
                else:
                    request_id = data["id"]
                    if request_id:
                        await self.controller.handle_response(request_id, data)
            elif self.controller.handle_method_message(data) is not None:
                self.logger.warning(f"Unsupported message {message}")

    async def handle_method_message(self, data: dict):
        method = data.get("method")
        if method is None:
            return

        if method == "subscription":
            params = data["params"]
            channel = params["channel"]
            if channel.startswith("book."):
                params_data = params["data"]
                instrument = params_data["instrument_name"]
                book = self.get_book(instrument)

                if "prev_change_id" in params_data:
                    book.handle_update(params_data)
                    if self.on_book_update:
                        await self.on_book_update(book)
                else:
                    book.handle_snapshot(params_data)
                    if self.on_book_setup:
                        await self.on_book_setup(book)
            else:
                await self.controller.handle_method_message(data)

        return

    def get_book(self, instrument: str) -> L2Book:
        book: L2Book = self.books.get(instrument)
        if book is None:
            book = L2Book(instrument)
            self.books[instrument] = book

        return book
