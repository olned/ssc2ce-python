from ssc2ce.common.l2_book import L2Book


class DeribitL2Book(L2Book):
    def __init__(self, instrument: str):
        L2Book.__init__(self, instrument)
        self.change_id = None
        self.timestamp = None
