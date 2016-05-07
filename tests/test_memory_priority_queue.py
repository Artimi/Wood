# -*- coding: utf-8 -*-

from wood.limit_order_book import BidOrder
from wood.priority_queue import MemoryPriorityQueue


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
    order1 = BidOrder(1, 1, 2.5, 100, 50)
    order2 = BidOrder(2, 1, 2.5, 200, 50)
    order3 = BidOrder(3, 1, 2.5, 300, 50)
    q.put(order1)
    q.put(order2)
    q.put(order3)

    q.remove_by_id(2)
    assert q.get() == order1
    assert q.get() == order3
