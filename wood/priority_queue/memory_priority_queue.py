# -*- coding: utf-8 -*-

import asyncio
import queue
from .base_priority_queue import BasePriorityQueue
from tabulate import tabulate


class MemoryPriorityQueue(BasePriorityQueue):
    """
    Priority queue implemented using in memory queue from stdlib. It uses
    method `__lt__` of each item to order them properly.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._queue = queue.PriorityQueue()
        self._orders = {}

    @asyncio.coroutine
    async def connect(self):
        """ Unnecessary method for keep interface"""
        pass

    @asyncio.coroutine
    def put(self, item):
        if item.order_id in self._orders:
            raise ValueError("Order with order_id %s is already present in queue." % item.order_id)
        self._queue.put(item)
        self._orders[item.order_id] = item

    @asyncio.coroutine
    def peek(self, index):
        return self._queue.queue[index]

    @asyncio.coroutine
    def get(self):
        item = self._queue.get()
        del self._orders[item.order_id]
        return item

    @asyncio.coroutine
    def remove(self, item):
        del self._orders[item.order_id]
        self._queue.queue.remove(item)

    @asyncio.coroutine
    def peek_by_id(self, order_id):
        try:
            return self._orders[order_id]
        except KeyError:
            return

    @asyncio.coroutine
    def empty(self):
        return self._queue.empty()

    @asyncio.coroutine
    async def cardinality(self):
        return len(self)

    def __getattr__(self, item):
        return getattr(self._queue, item)

    def __len__(self):
        return self._queue.qsize()

    def __iter__(self):
        return self._queue.queue.__iter__()

    def __str__(self):
        table = [(order.price, order.participant, order.quantity) for order in self]
        return tabulate(table, headers=["Price", "Participant", "Quantity"])

