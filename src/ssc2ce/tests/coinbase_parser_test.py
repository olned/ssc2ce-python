import os

from unittest import TestCase

from ssc2ce import CoinbaseParser
from .coinbase_expected_result import results

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, "coinbase_dump.jsonl")
with open(path) as f:
    lines = f.readlines()


class TestCexParser(TestCase):
    broken = False

    def test_one(self):
        parser = CoinbaseParser()
        book = parser.get_book("BTC-EUR")
        for i, line in enumerate(lines):
            # print(results[i])
            if results[i][0] == 1:
                parser.parse(line)
                self.assertTrue(book.valid())
                self.assertEqual(book.top_bid_price(), results[i][1])
                self.assertEqual(book.top_ask_price(), results[i][2])
            else:
                parser.parse(line)
                self.assertFalse(book.valid())
