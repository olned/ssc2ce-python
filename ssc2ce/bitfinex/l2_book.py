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

