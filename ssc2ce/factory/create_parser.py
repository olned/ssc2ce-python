import logging

logger = logging.getLogger(__name__)


def create_parser(exchange: str, is_cpp: bool):
    if is_cpp:
        from importlib import util

        ssc2ce_cpp_spec = util.find_spec("ssc2ce_cpp")
        if ssc2ce_cpp_spec is None:
            logger.error("You must install the ssc2ce_cpp module to use its features.\n pip install ssc2ce_cpp")
            return None

        if exchange == 'deribit':
            from ssc2ce_cpp import DeribitParser as Parser
        elif exchange == 'coinbase':
            from ssc2ce_cpp import CoinbaseParser as Parser
        elif exchange == 'cex':
            from ssc2ce_cpp import CexParser as Parser
        else:
            logger.error(f"Unknown exchange {exchange}")
            return None
    else:
        if exchange == 'deribit':
            from ssc2ce.deribit.parser import DeribitParser as Parser
        elif exchange == 'coinbase':
            from ssc2ce.coinbase_pro.parser import CoinbaseParser as Parser
        elif exchange == 'cex':
            from ssc2ce.cex.parser import CexParser as Parser
        else:
            logger.error(f"Unknown exchange {exchange}")
            return None

    return Parser()
