# -*- coding: utf-8 -*-

import abc


class BasePriorityQueue(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def put(self, item):
        """Insert item to priority queue."""
        pass

    @abc.abstractmethod
    def peek(self, index):
        """Return item on `index` position without poping."""
        pass

    @abc.abstractmethod
    def peek_by_id(self, order_id):
        """Get order with `order_id`"""
        pass

    @abc.abstractmethod
    def get(self):
        """Pop first item."""
        pass

    @abc.abstractmethod
    def remove(self, item):
        """Remove item from queue"""
        pass

