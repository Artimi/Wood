# -*- coding: utf-8 -*-

import functools
import queue
from collections import namedtuple


class BidOrder(namedtuple('BidOrder', 'order_id participant time price quantity')):
    __slots__ = ()

    def __lt__(self, other):
        return (self.price, self.time) < (other.price, other.time)

    def __le__(self, other):
        return (self.price, self.time) <= (other.price, other.time)

    def __eq__(self, other):
        return (self.price, self.time) == (other.price, other.time)

    def __ge__(self, other):
        return (self.price, self.time) >= (other.price, other.time)

    def __gt__(self, other):
        return (self.price, self.time) > (other.price, other.time)


class AskOrder(namedtuple('AskOrder', 'order_id participant time price quantity')):
    __slots__ = ()

    def __lt__(self, other):
        return (self.price > other.price) or (self.price == other.price and self.time < other.time)

    def __le__(self, other):
        return (self.price > other.price) or (self.price == other.price and self.time < other.time) or self.__eq__(other)

    def __eq__(self, other):
        return (self.price, self.time) == (other.price, other.time)

    def __ge__(self, other):
        return (self.price < other.price) or (self.price == other.price and self.time > other.time) or self.__eq__(other)

    def __gt__(self, other):
        return (self.price < other.price) or (self.price == other.price and self.time > other.time)


class LimitOrderBook:
    def __init__(self):
        self.bid_queue = queue.PriorityQueue()
        self.ask_queue = queue.PriorityQueue()

    def add(self, order):
        if isinstance(order, BidOrder):
            self.bid_queue.put(order)
        elif isinstance(order, AskOrder):
            self.ask_queue.put(order)
