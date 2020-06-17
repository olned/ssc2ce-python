from .deribit import Deribit, DeribitParser, DeribitL2Book
from .common import AuthType
from .bitfinex import Bitfinex, BitfinexL2Book
from .coinbase import Coinbase, CoinbaseParser, CoinbaseL2Book

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass