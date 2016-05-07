# -*- coding: utf-8 -*-

import pytest

from wood.priority_queue import MemoryPriorityQueue
from .utils import get_bid_order


def test_put():
    q = MemoryPriorityQueue()
    b_order = get_bid_order()
    q.put(b_order)

    assert q.get() == b_order


def test_get_lowest():
    q = MemoryPriorityQueue()
    q.put(get_bid_order(order_id=1, price=200))
    q.put(get_bid_order(order_id=2, price=300))
    q.put(get_bid_order(order_id=3, price=100))

    assert q.get().order_id == 2


def test_peek():
    q = MemoryPriorityQueue()
    q.put(get_bid_order(order_id=1, price=200))
    q.put(get_bid_order(order_id=2, price=300))
    q.put(get_bid_order(order_id=3, price=100))

    assert q.peek(0).order_id == 2
    assert q.peek(1).order_id == 1
    assert len(q) == 3


def test_remove():
    q = MemoryPriorityQueue()
    order1 = get_bid_order(order_id=1)
    order2 = get_bid_order(order_id=2)
    order3 = get_bid_order(order_id=3)

    q.put(order1)
    q.put(order2)
    q.put(order3)

    q.remove(order2)
    q.remove(order3)
    assert len(q) == 1
    assert q.get().order_id == 1


def test_peek_by_id():
    q = MemoryPriorityQueue()
    for i in range(1, 4):
        q.put(get_bid_order(order_id=i, price=i*100))

    order = q.peek_by_id(2)
    assert order.order_id == 2
    assert order.price == 200


def test_non_unique_order_id_raises_exception():
    q = MemoryPriorityQueue()
    q.put(get_bid_order(order_id=1, price=200))
    with pytest.raises(ValueError):
        q.put(get_bid_order(order_id=1, price=100))
