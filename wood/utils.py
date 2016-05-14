import asyncio
import logging
import graypy

from functools import lru_cache

from . import settings


@lru_cache(maxsize=None)
def get_logger():
    logging.basicConfig(**settings.LOGGING_PROPERTIES)
    logger = logging.getLogger('wood')
    logger.setLevel(logging.DEBUG)
    if settings.graylog:
        handler = graypy.GELFHandler(settings.graylog["host"], settings.graylog["port"])
        logger.addHandler(handler)
    return logger
