import asyncio
import logging
from time import time

from examples.book_watcher import BookWatcher

import sys

if len(sys.argv) > 1 and "cpp" in sys.argv:
    from importlib import util

    ssc2ce_cpp_spec = util.find_spec("ssc2ce_cpp")
    if ssc2ce_cpp_spec:
        from ssc2ce_cpp import DeribitParser
    else:
        print("You must install the ssc2ce_cpp module to use its features.\n pip install ssc2ce_cpp")
        exit(1)
else:
    from ssc2ce.deribit.parser import DeribitParser

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("deribit-parser")


class FileController:
    def __init__(self):
        self.parser = DeribitParser()
        self.counter = 0
        self.watcher = BookWatcher(self.parser, False)

    def run(self, filename: str):
        start = time()
        i = 0
        with open(filename) as f:
            for line in f:
                i += 1
                if not self.parser.parse(line):
                    self.handle_message(line)

        logger.info(f"{i} in {time() - start} sec. {self.counter}")

    def handle_message(self, message: str) -> None:
        self.counter += 1
        # logger.info(message[:-1])


FileController().run("dump.txt")
