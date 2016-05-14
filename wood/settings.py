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

try:
    from .settings_local import *
except ImportError:
    pass
