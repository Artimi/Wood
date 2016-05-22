# -*- coding: utf-8 -*-

import asyncio

from abc import ABC, abstractmethod


class BasePubSub(ABC):
    def __init__(self, loop):
        self.loop = loop

    @abstractmethod
    def subscribe(self, channel):
        pass

    @abstractmethod
    def unsubscribe(self, channel):
        pass

    @abstractmethod
    def publish(self, channel, message):
        pass

    @asyncio.coroutine
    @abstractmethod
    async def get(self):
        pass
