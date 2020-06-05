from sortedcontainers import SortedKeyList
from abc import abstractmethod, ABC
from .l2_book_side import L2BookSide, SortedKeyList


class AbstractL2Book(ABC):
    """

    """

    def __init__(self, instrument: str):
        """

        :param instrument:
        """
        self.instrument = instrument
        self._bids = L2BookSide(is_bids=True)
        self._asks = L2BookSide(is_bids=False)

    @abstractmethod
    def handle_snapshot(self, message: dict) -> None:
        """

        :param message:
        :return:
        """
        pass

    @abstractmethod
    def handle_update(self, message: dict) -> None:
        """

        :param message:
        :return:
        """
        pass

    @property
    def bids(self):
        return self._bids.data

    @property
    def asks(self):
        return self._asks.data
