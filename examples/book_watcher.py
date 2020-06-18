from ssc2ce.common.abstract_parser import AbstractParser
from ssc2ce.deribit.l2_book import L2Book


class BookWatcher:
    def __init__(self, parser: AbstractParser, print_it: bool = True):
        self.betters = {}
        self.print_it = print_it
        parser.set_on_book_setup(self.handle_book_setup)
        parser.set_on_book_update(self.handle_book_update)

    def handle_book_setup(self, book: L2Book):
        top = [book.top_bid_price(), book.top_ask_price()]
        self.betters[book.instrument()] = top
        if self.print_it:
            print(f"{book.instrument()} bid:{top[0]} ask:{top[1]}")

    def handle_book_update(self, book: L2Book):
        top = self.betters[book.instrument()]
        if top[1] != book.top_ask_price() or top[0] != book.top_bid_price():
            top[1] = book.top_ask_price()
            top[0] = book.top_bid_price()
            if self.print_it:
                print(f"{book.instrument()} bid:{top[0]} ask:{top[1]}")
