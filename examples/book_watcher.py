from ssc2ce.deribit.l2_book import L2Book


class BookWatcher:
    def __init__(self, parser):
        self.betters = {}
        parser.on_book_setup = self.handle_book_setup
        parser.on_book_update = self.handle_book_update

    async def handle_book_setup(self, book: L2Book):
        top = [book.bids[0][0], book.asks[0][0]]
        self.betters[book.instrument] = top
        print(f"{book.instrument} bid:{top[0]} ask:{top[1]}")

    async def handle_book_update(self, book: L2Book):
        top = self.betters[book.instrument]
        if top[1] != book.asks[0][0] or top[0] != book.bids[0][0]:
            top[1] = book.asks[0][0]
            top[0] = book.bids[0][0]
            print(f"{book.instrument} bid:{top[0]} ask:{top[1]}")
