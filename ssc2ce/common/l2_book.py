from .book_event_handler_holder import BookEventHandlerHolder
from .l2_book_side import L2BookSide


class L2Book(BookEventHandlerHolder):
    """

    """

    def __init__(self, instrument: str):
        """

        :param instrument:
        """

        BookEventHandlerHolder.__init__(self)
        self._instrument = instrument
        self._bids = L2BookSide(is_descending=True)
        self._asks = L2BookSide(is_descending=False)
        self.exchange_timestamp = None

    def instrument(self) -> str:
        return self._instrument

    @property
    def bids(self) -> L2BookSide:
        return self._bids

    @property
    def asks(self) -> L2BookSide:
        return self._asks

    def clear(self):
        self._bids.data.clear()
        self._asks.data.clear()

    def top_ask_price(self):
        return self._asks.data[0][0]

    def top_bid_price(self):
        return self._bids.data[0][0]

    def valid(self) -> bool:
        return len(self._asks.data) != 0 and len(self._bids.data) != 0

    def set_exchange_ts(self, exchange_ts):
        self.exchange_timestamp = exchange_ts
