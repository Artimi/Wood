# -*- coding: utf-8 -*-

import asyncio

from abc import ABC, abstractmethod


class BaseSubscriber(ABC):
    def __init__(self, loop):
        self.loop = loop

    @asyncio.coroutine
    async def connect(self):
        pass

    @abstractmethod
    def subscribe(self, channel):
        pass

    @abstractmethod
    def unsubscribe(self, channel):
        pass

    @asyncio.coroutine
    @abstractmethod
    async def get(self):
        pass

    def close(self):
        pass


class BasePublisher(ABC):
    def __init__(self, loop):
        self.loop = loop

    @asyncio.coroutine
    def connect(self):
        pass

    @abstractmethod
    def publish(self, channel, message):
        pass

    def close(self):
        pass
