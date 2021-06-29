__version__ = '0.1.0'

import logging

from .bot import Mirai
from .adapters import Adapter, HTTPAdapter
from .bus import EventBus
from .colorlog import ColoredFormatter
from .exceptions import ApiError, LoginError

__all__ = [
    'Mirai', 'Adapter', 'HTTPAdapter', 'EventBus', 'ApiError', 'LoginError',
    'get_logger'
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = ColoredFormatter('%(asctime)s - %(levelname)-8s %(message)s',
                             datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)

logger.addHandler(ch)


def get_logger() -> logging.Logger:
    return logger