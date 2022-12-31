import logging
from ssc2ce.common import L2Book


class BitfinexL2Book(L2Book):
    change_id = None
    timestamp = None
    logger = logging.getLogger(__name__)

    def __init__(self, instrument: str):
        """

        :param instrument:
        """
        L2Book.__init__(self, instrument)

    def handle_snapshot(self, message: dict) -> None:
        """

        :param message:
        :return:
        """
        self.clear()

        for item in message[1]:
            price = item[2]
            if price < 0:
                self.asks.add(item[0], -price)
            else:
                self.bids.add(item[0], price)

    def handle_update(self, message: dict) -> None:
        """

        :param message:
        :return:
        """
        price = message[1][0]
        size = message[1][2]
        count = message[1][1]
        if size < 0:
            if count == 0:
                self._asks.update(price, 0.)
            else:
                self._asks.update(price, -size)
        else:
            if count == 0:
                self._bids.update(price, 0.)
            else:
                self._bids.update(price, size)
