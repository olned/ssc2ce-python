import asyncio
import json
import logging

from examples.book_watcher import BookWatcher
from ssc2ce.deribit.icontroller import IDeribitController
from ssc2ce.deribit.parser import DeribitParser

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("deribit-parser")


class FileController(IDeribitController):
    def __init__(self):
        self.parser = DeribitParser(self)
        self.counter = 0
        self.watcher = BookWatcher(self.parser)

    async def run(self, filename: str):
        with open(filename) as f:
            for line in f:
                await self.parser.handle_message(line)

        logger.info(f"{self.counter}")

    async def handle_method_message(self, message: dict) -> None:

        self.counter += 1

    async def handle_error(self, message: dict) -> None:
        self.counter += 1
        logger.info(message)

    async def handle_response(self, request_id: int, data: dict):
        self.counter += 1
        # logger.info(json.dumps(data))


asyncio.run(FileController().run("dump.txt"))
