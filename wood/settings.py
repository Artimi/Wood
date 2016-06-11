# -*- coding: utf-8 -*-

import logging

graylog = {
    "host": "172.17.0.1",
    "port": 12222,
}

LOGGING_PROPERTIES = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "level": logging.DEBUG,
}

redis = {
    "host": "localhost",
    "port": 6379,
}

try:
    from .settings_local import *
except ImportError:
    pass
