# -*- coding: utf-8 -*-

import asyncio

import asyncio_redis

import wood.settings as settings
from .base import BasePublisher, BaseSubscriber


def redis_pubsub_factory(loop):
    return RedisSubscriber(loop), RedisPublisher(loop)


class RedisSubscriber(BaseSubscriber):
    """ Subscriber that uses redis PubSub functionality. """
    def __init__(self, loop):
        super().__init__(loop)
        self.subscribed = set()

    @asyncio.coroutine
    async def connect(self):
        """
        Connect to redis and subscribe to everything. This is necessary because
        we need to subscribe to certain channel before we call `get`.
        """
        self._connection = await asyncio_redis.Connection.create(host=settings.redis["host"],
                                                                 port=settings.redis["port"],
                                                                 loop=self.loop)
        self._subscriber = await self._connection.start_subscribe()
        await self._subscriber.psubscribe(["*"])

    def subscribe(self, channel):
        self.subscribed.add(str(channel))

    def unsubscribe(self, channel):
        self.subscribed.remove(str(channel))

    @asyncio.coroutine
    async def get(self):
        while True:
            reply = await self._subscriber.next_published()
            if reply.channel in self.subscribed:
                return reply.channel, reply.value

    def close(self):
        self._connection.close()


class RedisPublisher(BasePublisher):
    """ Publisher using Redis. """
    def __init__(self, loop):
        super().__init__(loop)

    @asyncio.coroutine
    async def connect(self):
        self._connection = await asyncio_redis.Connection.create(host='localhost', port=6379, loop=self.loop)

    @asyncio.coroutine
    async def publish(self, channel, message):
        await self._connection.publish(str(channel), message)

    def close(self):
        self._connection.close()
