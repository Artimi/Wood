# -*- coding: utf-8 -*-

import abc
import asyncio


class BasePriorityQueue(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    @asyncio.couroutine
    def put(self, item):
        """Insert item to priority queue."""
        pass

    @abc.abstractmethod
    @asyncio.couroutine
    def peek(self, index):
        """Return item on `index` position without poping."""
        pass

    @abc.abstractmethod
    @asyncio.couroutine
    def peek_by_id(self, order_id):
        """Get order with `order_id`"""
        pass

    @abc.abstractmethod
    @asyncio.couroutine
    def get(self):
        """Pop first item."""
        pass

    @abc.abstractmethod
    @asyncio.couroutine
    def remove(self, item):
        """Remove item from queue"""
        pass

    @abc.abstractmethod
    @asyncio.couroutine
    def empty(self):
        """Return True if queue is empty"""
        pass
