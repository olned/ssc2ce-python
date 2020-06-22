import logging
import argparse
from time import time

from examples.common.book_watcher import BookWatcher

from ssc2ce import create_parser

logging.basicConfig(format='%(asctime)s %(name)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger("deribit-parser")


class FileReader:
    def __init__(self, exchange: str, is_cpp: bool):

        self.parser = create_parser(exchange, is_cpp)
        if self.parser is None:
            exit(1)

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

    def handle_message(self, _: str) -> None:
        self.counter += 1


def main():
    parser = argparse.ArgumentParser('ssc2ce parser example.')
    parser.add_argument('exchange',
                        type=str,
                        help='...')
    parser.add_argument('file',
                        type=str,
                        help='...')
    parser.add_argument('-c', '--cpp',
                        dest='is_cpp',
                        action='store_true',
                        default=False,
                        help='...')

    args = parser.parse_args()

    FileReader(args.exchange, args.is_cpp).run(args.file)


if __name__ == '__main__':
    main()
