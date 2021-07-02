# -*- coding: utf-8 -*-
__version__ = '0.1.0'

import logging

from YiriMirai.adapters import Adapter, Method, HTTPAdapter
from YiriMirai.bot import Mirai, SimpleMirai
from YiriMirai.bus import EventBus
from YiriMirai.colorlog import ColoredFormatter
from YiriMirai.exceptions import ApiError, LoginError

__all__ = [
    'Mirai', 'SimpleMirai', 'Adapter', 'Method', 'HTTPAdapter', 'EventBus',
    'ApiError', 'LoginError', 'get_logger'
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = ColoredFormatter(
    '%(asctime)s - %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)
ch.setFormatter(formatter)

logger.addHandler(ch)


def get_logger() -> logging.Logger:
    return logger
