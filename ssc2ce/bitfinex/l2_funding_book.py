from .l2_funding_book_side import L2FundingBookSide
from ..common.book_event_handler_holder import BookEventHandlerHolder


class L2FundingBook(BookEventHandlerHolder):
    """

    """

    def __init__(self, instrument: str):
        """

        :param instrument:
        """

        BookEventHandlerHolder.__init__(self)
        self._instrument = instrument
        # bids - what people are offering towards lending, so the lowest rate is in the beginning.
        self._bids = L2FundingBookSide(is_descending=False)
        # asks - what people want to borrow, so the highest rate is in the beginning.
        self._asks = L2FundingBookSide(is_descending=True)
        self.exchange_timestamp = None

    def instrument(self) -> str:
        return self._instrument

    @property
    def bids(self) -> L2FundingBookSide:
        return self._bids

    @property
    def asks(self) -> L2FundingBookSide:
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
