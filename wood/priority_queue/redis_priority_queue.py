# -*- coding: utf-8 -*-

import asyncio
import aioredis
import uuid
from .base_priority_queue import BasePriorityQueue

import wood.settings as settings
from wood.orders import BidOrder, AskOrder, MarketBidOrder, MarketAskOrder


class RedisPriorityQueue(BasePriorityQueue):
    def __init__(self, loop, reverse=False, name=None):
        super().__init__()
        self.loop = loop
        self.reverse = reverse
        self.zset_name = str(uuid.uuid4()) if name is None else name

    def str_to_item(self, s):
        # http://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
        # eval can be really dangerous but this is just toy application
        return eval(s, {"AskOrder": AskOrder,
                        "BidOrder": BidOrder,
                        "MarketAskOrder": MarketAskOrder,
                        "MarketBidOrder": MarketBidOrder})

    @asyncio.coroutine
    async def connect(self):
        self._redis = await aioredis.create_redis((settings.redis["host"], settings.redis["port"]),
                                                  loop=self.loop)

    def close(self):
        self._redis.close()

    @asyncio.coroutine
    async def put(self, item):
        record = str(item)
        await self._redis.zadd(self.zset_name, item.price, record)

    @asyncio.coroutine
    async def peek(self, index):
        if self.reverse:
            records = await self._redis.zrevrange(self.zset_name, index, index)
        else:
            records = await self._redis.zrange(self.zset_name, index, index)
        return self.str_to_item(records[0])

    @asyncio.coroutine
    async def get(self):
        while True:
            # reverse need a little hack because items
            if self.reverse:
                records = await self._redis.zrevrange(self.zset_name, 0, 0, withscores=True)
                # records are list of [key1, score1, key2, score2, ...]
                best_score = records[1]
                records = await self._redis.zrangebyscore(self.zset_name, best_score, best_score)
                # choose first because it has lowest time
                record = records[0]
            else:
                records = await self._redis.zrange(self.zset_name, 0, 0)
                record = records[0]
            # removal is not atomic so it may happen that somebody takes this before I can delete it
            if await self._redis.zrem(self.zset_name, record) == 1:
                item = self.str_to_item(record)
                return item

    @asyncio.coroutine
    async def remove(self, item):
        record = str(item)
        await self._redis.zrem(self.zset_name, record)

    @asyncio.coroutine
    async def peek_by_id(self, order_id):
        records = await self._redis.zrange(self.zset_name, 0, -1)
        for record in records:
            item = self.str_to_item(record)
            if item.order_id == order_id:
                return item
        return None

    @asyncio.coroutine
    async def cardinality(self):
        return await self._redis.zcard(self.zset_name)

    @asyncio.coroutine
    async def empty(self):
        return await self.cardinality() == 0


