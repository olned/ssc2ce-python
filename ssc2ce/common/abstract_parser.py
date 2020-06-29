from abc import ABC, abstractmethod

from .book_event_handler_holder import BookEventHandlerHolder


class AbstractParser(ABC, BookEventHandlerHolder):
    """

    """

    def __init__(self):
        BookEventHandlerHolder.__init__(self)

    @abstractmethod
    def parse(self, message: str) -> bool:
        return False
