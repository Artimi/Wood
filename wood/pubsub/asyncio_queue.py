# -*- coding: utf-8 -*-

import asyncio

from .base import BasePublisher, BaseSubscriber


def asyncio_queue_pubsub_factory(loop):
    queue = asyncio.Queue(loop=loop)
    return AsyncioQueueSubscriber(loop, queue), AsyncioQueuePublisher(loop, queue)


class AsyncioQueueSubscriber(BaseSubscriber):
    def __init__(self, loop, queue):
        super().__init__(loop)
        self.subscribed = set()
        self._queue = queue

    def subscribe(self, channel):
        self.subscribed.add(str(channel))

    def unsubscribe(self, channel):
        try:
            self.subscribed.remove(str(channel))
        except KeyError:
            pass

    @asyncio.coroutine
    async def get(self):
        while True:
            channel, message = await self._queue.get()
            if channel in self.subscribed:
                return channel, message


class AsyncioQueuePublisher(BasePublisher):
    def __init__(self, loop, queue):
        super().__init__(loop)
        self._queue = queue

    @asyncio.coroutine
    async def publish(self, channel, message):
        await self._queue.put((str(channel), message))
