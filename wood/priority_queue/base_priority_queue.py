# -*- coding: utf-8 -*-

import abc


class BasePriorityQueue(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def put(self, item):
        """Insert item to priority queue."""

    @abc.abstractmethod
    def peek(self, index):
        """Return item on `index` position without poping."""

    @abc.abstractmethod
    def get(self):
        """Pop first item."""

    @abc.abstractmethod
    def remove(self, item):
        """Remove item from queue"""

    @abc.abstractmethod
    def remove_by_id(self, order_id):
        """Remove order with `order_id`"""
