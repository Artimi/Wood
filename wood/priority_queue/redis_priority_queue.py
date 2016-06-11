# -*- coding: utf-8 -*-

import asyncio
import asyncio_redis
import uuid
from .base_priority_queue import BasePriorityQueue

from wood.orders import BidOrder, AskOrder, MarketBidOrder, MarketAskOrder


class RedisPriorityQueue(BasePriorityQueue):
    def __init__(self, loop, reverse=False, name=None):
        super().__init__()
        self.loop = loop
        self.reverse = reverse
        self.zset_name = str(uuid.uuid4()) if name is None else name
        self._orders = {}

    def str_to_item(self, s):
        # http://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
        # eval can be really dangerous but this is just toy application
        return eval(s, {"AskOrder": AskOrder,
                        "BidOrder": BidOrder,
                        "MarketAskOrder": MarketAskOrder,
                        "MarketBidOrder": MarketBidOrder})

    @asyncio.coroutine
    async def connect(self):
        self._redis = await asyncio_redis.Connection.create(host='localhost', port=6379, loop=self.loop)

    @asyncio.coroutine
    async def put(self, item):
        if item.order_id in self._orders:
            raise ValueError("Order with order_id %s is already present in queue." % item.order_id)
        record = str(item)
        self._orders[item.order_id] = item
        await self._redis.zadd(self.zset_name, {record: item.price})

    @asyncio.coroutine
    async def peek(self, index):
        if self.reverse:
            records = await self._redis.zrevrange(self.zset_name, index, index)
        else:
            records = await self._redis.zrange(self.zset_name, index, index)
        records = await records.asdict()
        record = list(records.keys())[0]
        return self.str_to_item(record)

    @asyncio.coroutine
    async def get(self):
        while True:
            if self.reverse:
                records = await self._redis.zrevrange(self.zset_name, 0, 0)
            else:
                records = await self._redis.zrange(self.zset_name, 0, 0)
            records = await records.asdict()
            record = list(records.keys())[0]
            # removal is not atomic so it may happen that somebody takes this before I can delete it
            if await self._redis.zrem(self.zset_name, [record]) == 1:
                item = self.str_to_item(record)
                del self._orders[item.order_id]
                return item

    @asyncio.coroutine
    async def remove(self, item):
        record = str(item)
        del self._orders[item.order_id]
        await self._redis.zrem(self.zset_name, [record])

    @asyncio.coroutine
    async def peek_by_id(self, order_id):
        try:
            return self._orders[order_id]
        except KeyError:
            return

    @asyncio.coroutine
    async def cardinality(self):
        return await self._redis.zcard(self.zset_name)

    @asyncio.coroutine
    async def empty(self):
        return await self.cardinality() == 0


