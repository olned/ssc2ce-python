from .deribit import Deribit, DeribitParser, DeribitL2Book
from .common import AuthType
from .bitfinex import Bitfinex, BitfinexL2Book
from .coinbase_pro import Coinbase, CoinbaseParser, CoinbaseL2Book
from .factory import create_parser
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass
