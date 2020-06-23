import os

from unittest import TestCase

from ssc2ce import CexParser, BrokenOrderbook
from .cex_expected_result import results

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, "cex_dump.jsonl")
with open(path) as f:
    lines = f.readlines()


class TestCexParser(TestCase):
    broken = False

    def test_one(self):
        parser = CexParser()
        book = parser.get_book("BTC:EUR")
        for i, line in enumerate(lines):
            # print(results[i])
            if results[i][0] == 1:
                parser.parse(line)
                self.assertTrue(book.valid())
                self.assertEqual(book.top_bid_price(), results[i][1])
                self.assertEqual(book.top_ask_price(), results[i][2])
            elif results[i][0] == 0:
                parser.parse(line)
                self.assertFalse(book.valid())
            else:
                self.assertRaises(BrokenOrderbook, parser.parse, line)

    def handle_broken(self, pair: str, expected: int, received: int):
        print(pair, expected, received)
        self.broken = True

    def test_two(self):
        parser = CexParser()
        parser._handler_broken_orderbook = self.handle_broken

        book = parser.get_book("BTC:EUR")
        for i, line in enumerate(lines):
            # print(results[i])
            if results[i][0] == 1:
                parser.parse(line)
                self.assertTrue(book.valid())
                self.assertEqual(book.top_bid_price(), results[i][1])
                self.assertEqual(book.top_ask_price(), results[i][2])
                self.assertFalse(self.broken)
            elif results[i][0] == 0:
                parser.parse(line)
                self.assertFalse(book.valid())
                self.assertFalse(self.broken)
            else:
                parser.parse(line)
                self.assertTrue(self.broken)