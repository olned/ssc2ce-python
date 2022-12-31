import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Callable, Optional

from ssc2ce.deribit.l2_book import DeribitL2Book, L2Book
from ssc2ce.common.exceptions import BrokenOrderbook


class AbstractParser(ABC):
    """

    """

    def __init__(self):
        self._on_book_update: Optional[Callable[[L2Book], None]] = None
        self._on_book_setup: Optional[Callable[[L2Book], None]] = None

    def set_on_book_setup(self, handler) -> None:
        self._on_book_setup = handler

    def set_on_book_update(self, handler) -> None:
        self._on_book_update = handler

    @abstractmethod
    def parse(self, message: str) -> bool:
        return False
