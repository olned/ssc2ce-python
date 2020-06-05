from .deribit import Deribit
from .common import AuthType
from .bitfinex import Bitfinex

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass