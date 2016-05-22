# -*- coding: utf-8 -*-

import asyncio

from .base import BasePubSub


class AsyncioQueuePubsub(BasePubSub):
    def __init__(self, loop):
        super().__init__(loop)
        self.subscribed = set()
        self._queue = asyncio.Queue(loop=loop)

    def subscribe(self, channel):
        self.subscribed.add(channel)

    def unsubscribe(self, channel):
        try:
            self.subscribed.remove(channel)
        except KeyError:
            pass

    def publish(self, channel, message):
        self._queue.put_nowait((channel, message))

    @asyncio.coroutine
    async def get(self):
        return await self._queue.get()
