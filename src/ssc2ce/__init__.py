from .deribit import Deribit, DeribitParser, DeribitL2Book, AuthType
from .bitfinex import Bitfinex, BitfinexL2Book
from .coinbase_pro import Coinbase, CoinbaseParser, CoinbaseL2Book
from .cex import Cex, CexParser, CexL2Book
from .factory import create_parser
from .common.exceptions import BrokenOrderbook
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass
