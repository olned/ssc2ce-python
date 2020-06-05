import logging
from ssc2ce.common.abstract_l2_book import AbstractL2Book
from collections import deque

from ssc2ce.common.exceptions import BrokenOrderBook


class L2Book(AbstractL2Book):
    change_id = None
    timestamp = None
    logger = logging.getLogger(__name__)

    def __init__(self, instrument: str):
        """

        :param instrument:
        """
        AbstractL2Book.__init__(self, instrument)

    def handle_snapshot(self, message: dict) -> None:
        """

        :param message:
        :return:
        """
        self.asks.clear()
        self.bids.clear()

        self.change_id = message["change_id"]
        self.timestamp = message["timestamp"]
        for i in message['bids']:
            self.bids.add([i[1], i[2]])

        for i in message['asks']:
            self.asks.add([i[1], i[2]])

    def handle_update(self, message: dict) -> None:
        """

        :param message:
        :return:
        """
        prev_change_id = message["prev_change_id"]
        if prev_change_id != self.change_id:
            raise BrokenOrderBook(self.instrument, prev_change_id, self.change_id)

        self.change_id = message["change_id"]
        self.timestamp = message["timestamp"]
        for change in message['bids']:
            if change[0] == 'new':
                self._bids.add(change[1:])
            elif change[0] == 'delete':
                self._bids.delete(change[1])
            else:
                self._bids.update(price=change[1], size=change[2])

        for change in message['asks']:
            if change[0] == 'new':
                self._asks.add(change[1:])
            elif change[0] == 'delete':
                self._asks.delete(change[1])
            else:
                self._asks.update(price=change[1], size=change[2])


def create_l2_order_book(instrument: str) -> AbstractL2Book:
    return L2Book(instrument)
