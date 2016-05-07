# -*- coding: utf-8 -*-

from collections import namedtuple
from .priority_queue import BasePriorityQueue


class BidOrder(namedtuple('BidOrder', 'order_id participant time price quantity')):
    __slots__ = ()

    def __lt__(self, other):
        return (self.price, self.time) < (other.price, other.time)

    def __le__(self, other):
        return (self.price, self.time) <= (other.price, other.time)

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

    def __ge__(self, other):
        return (self.price < other.price) or (self.price == other.price and self.time > other.time) or self.__eq__(other)

    def __gt__(self, other):
        return (self.price < other.price) or (self.price == other.price and self.time > other.time)


class LimitOrderBook:
    def __init__(self, PriorityQueue):
        self.bid_queue = PriorityQueue()
        self.ask_queue = PriorityQueue()

    def add(self, order):
        if isinstance(order, BidOrder):
            self.bid_queue.put(order)
        elif isinstance(order, AskOrder):
            self.ask_queue.put(order)
