import asyncio
import logging
from time import time

from examples.book_watcher import BookWatcher
from ssc2ce.deribit.icontroller import IDeribitController

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


class FileController(IDeribitController):
    def __init__(self):
        self.parser = DeribitParser()
        self.counter = 0
        self.watcher = BookWatcher(self.parser, False)

    async def run(self, filename: str):
        start = time()
        with open(filename) as f:
            for line in f:
                self.parser.parse(line)

        logger.info(f"{self.counter} in {time()-start} sec.")

    async def handle_method_message(self, message: dict) -> None:
        self.counter += 1

    async def handle_error(self, message: dict) -> None:
        self.counter += 1
        logger.info(message)

    async def handle_response(self, request_id: int, data: dict):
        self.counter += 1
        # logger.info(json.dumps(data))


asyncio.run(FileController().run("dump.txt"))
