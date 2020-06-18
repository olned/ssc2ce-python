import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Callable

from ssc2ce.deribit.l2_book import DeribitL2Book, L2Book
from ssc2ce.common.exceptions import BrokenOrderBook


class AbstractParser(ABC):
    """

    """
    _on_book_update: Callable[[L2Book], bool] = None
    _on_book_setup: Callable[[L2Book], bool] = None

    def __init__(self):
        pass

    def set_on_book_setup(self, handler) -> None:
        self._on_book_setup = handler

    def set_on_book_update(self, handler) -> None:
        self._on_book_update = handler

    @abstractmethod
    def parse(self, message: str) -> bool:
        return False
