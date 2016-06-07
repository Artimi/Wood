# -*- coding: utf-8 -*-

import pytest

from wood.priority_queue import MemoryPriorityQueue
from .utils import get_bid_order


def test_put(event_loop):
    do = event_loop.run_until_complete
    q = MemoryPriorityQueue()
    b_order = get_bid_order()
    do(q.put(b_order))

    assert do(q.get()) == b_order


def test_get_lowest(event_loop):
    do = event_loop.run_until_complete
    q = MemoryPriorityQueue()
    do(q.put(get_bid_order(order_id=1, price=200)))
    do(q.put(get_bid_order(order_id=2, price=300)))
    do(q.put(get_bid_order(order_id=3, price=100)))

    assert do(q.get()).order_id == 2


def test_peek(event_loop):
    do = event_loop.run_until_complete
    q = MemoryPriorityQueue()
    do(q.put(get_bid_order(order_id=1, price=200)))
    do(q.put(get_bid_order(order_id=2, price=300)))
    do(q.put(get_bid_order(order_id=3, price=100)))

    assert do(q.peek(0)).order_id == 2
    assert do(q.peek(1)).order_id == 1
    assert len(q) == 3


def test_remove(event_loop):
    do = event_loop.run_until_complete
    q = MemoryPriorityQueue()
    order1 = get_bid_order(order_id=1)
    order2 = get_bid_order(order_id=2)
    order3 = get_bid_order(order_id=3)

    do(q.put(order1))
    do(q.put(order2))
    do(q.put(order3))

    do(q.remove(order2))
    do(q.remove(order3))
    assert len(q) == 1
    assert do(q.get()).order_id == 1


def test_peek_by_id(event_loop):
    do = event_loop.run_until_complete
    q = MemoryPriorityQueue()
    for i in range(1, 4):
        do(q.put(get_bid_order(order_id=i, price=i*100)))

    order = do(q.peek_by_id(2))
    assert order.order_id == 2
    assert order.price == 200


def test_non_unique_order_id_raises_exception(event_loop):
    do = event_loop.run_until_complete
    q = MemoryPriorityQueue()
    do(q.put(get_bid_order(order_id=1, price=200)))
    with pytest.raises(ValueError):
        do(q.put(get_bid_order(order_id=1, price=100)))
