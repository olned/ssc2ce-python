class Ssc2ceError(Exception):
    """Base class for errors."""


class BrokenOrderbook(Exception):
    def __init__(self, instrument, prev_change_id, change_id):
        self.instrument = instrument
        self.message = f"instrument:{self.instrument} expected:{change_id} != received:{prev_change_id}"
