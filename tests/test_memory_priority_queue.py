# -*- coding: utf-8 -*-

from wood.limit_order_book import BidOrder
from wood.priority_queue import MemoryPriorityQueue
from .utils import get_bid_order


def test_put():
    q = MemoryPriorityQueue()
    q.put(1)

    assert q.get() == 1


def test_get_lowest():
    q = MemoryPriorityQueue()
    q.put(2)
    q.put(1)
    q.put(3)

    assert q.get() == 1


def test_peek():
    q = MemoryPriorityQueue()
    q.put(2)
    q.put(1)
    q.put(3)

    assert q.peek(0) == 1
    assert q.peek(1) == 2
    assert len(q) == 3


def test_remove():
    q = MemoryPriorityQueue()
    q.put(2)
    q.put(1)
    q.put(3)

    q.remove(2)
    q.remove(3)
    assert len(q) == 1
    assert q.get() == 1


def test_remove_by_id():
    q = MemoryPriorityQueue()
    for i in range(1, 4):
        q.put(get_bid_order(order_id=i, price=i*100))

    q.remove_by_id(2)
    assert q.get().order_id == 3
    assert q.get().order_id == 1
