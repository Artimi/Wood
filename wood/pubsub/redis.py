# -*- coding: utf-8 -*-

import asyncio

import aioredis

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
        self._redis = await aioredis.create_redis((settings.redis["host"], settings.redis["port"]),
                                                  loop=self.loop)
        channels = await self._redis.psubscribe("*")
        self._channel = channels[0]


    def subscribe(self, channel):
        self.subscribed.add(str(channel))

    def unsubscribe(self, channel):
        self.subscribed.remove(str(channel))

    @asyncio.coroutine
    async def get(self):
        async for reply in self._channel.iter():
            channel, message = reply
            channel = channel.decode()
            message = message.decode()
            if channel in self.subscribed:
                return channel, message

    def close(self):
        self._redis.close()


class RedisPublisher(BasePublisher):
    """ Publisher using Redis. """
    def __init__(self, loop):
        super().__init__(loop)

    @asyncio.coroutine
    async def connect(self):
        self._redis = await aioredis.create_redis((settings.redis["host"], settings.redis["port"]),
                                                       loop=self.loop)

    @asyncio.coroutine
    async def publish(self, channel, message):
        await self._redis.publish(str(channel), message)

    def close(self):
        self._redis.close()
