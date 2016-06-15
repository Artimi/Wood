# -*- coding: utf-8 -*-

import abc
import asyncio


class BasePriorityQueue(abc.ABC):
    """
    Priority queue stores orders of one group (bid or ask).
    """
    def __init__(self):
        pass

    @asyncio.coroutine
    def close(self):
        """ Close potentional connection. """
        pass

    @abc.abstractmethod
    @asyncio.coroutine
    def put(self, item):
        """ Insert item to priority queue. """
        pass

    @abc.abstractmethod
    @asyncio.coroutine
    def peek(self, index):
        """ Return item on `index` position without poping. """
        pass

    @abc.abstractmethod
    @asyncio.coroutine
    def peek_by_id(self, order_id):
        """ Get order with `order_id`. """
        pass

    @abc.abstractmethod
    @asyncio.coroutine
    def get(self):
        """ Pop first item. """
        pass

    @abc.abstractmethod
    @asyncio.coroutine
    def remove(self, item):
        """ Remove item from queue. """
        pass

    @abc.abstractmethod
    @asyncio.coroutine
    def empty(self):
        """ Return True if queue is empty. """
        pass

    @asyncio.coroutine
    async def cardinality(self):
        """ Return length of priority queue. """
        pass
