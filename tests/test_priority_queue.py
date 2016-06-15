# -*- coding: utf-8 -*-

import pytest

from wood.priority_queue import MemoryPriorityQueue
from wood.priority_queue import RedisPriorityQueue
from .utils import get_bid_order

priority_queues = [MemoryPriorityQueue]
if pytest.config.getoption("--redis"):
    priority_queues.append(RedisPriorityQueue)


@pytest.mark.parametrize("priority_queue", priority_queues)
def test_put(event_loop, priority_queue):
    do = event_loop.run_until_complete
    q = priority_queue(event_loop, reverse=True)
    do(q.connect())
    b_order = get_bid_order()
    do(q.put(b_order))

    assert do(q.get()) == b_order


@pytest.mark.parametrize("priority_queue", priority_queues)
def test_get_lowest(event_loop, priority_queue):
    do = event_loop.run_until_complete
    q = priority_queue(event_loop, reverse=True)
    do(q.connect())
    do(q.put(get_bid_order(order_id=1, price=200)))
    do(q.put(get_bid_order(order_id=2, price=300)))
    do(q.put(get_bid_order(order_id=3, price=100)))

    assert do(q.get()).order_id == 2


@pytest.mark.parametrize("priority_queue", priority_queues)
def test_get_lowest_time(event_loop, priority_queue):
    do = event_loop.run_until_complete
    q = priority_queue(event_loop, reverse=True)
    do(q.connect())
    do(q.put(get_bid_order(time=1, order_id=1, price=100)))
    do(q.put(get_bid_order(time=2, order_id=2, price=100)))

    assert do(q.get()).order_id == 1


@pytest.mark.parametrize("priority_queue", priority_queues)
def test_peek(event_loop, priority_queue):
    do = event_loop.run_until_complete
    q = priority_queue(event_loop, reverse=True)
    do(q.connect())
    do(q.put(get_bid_order(order_id=1, price=200)))
    do(q.put(get_bid_order(order_id=2, price=300)))
    do(q.put(get_bid_order(order_id=3, price=100)))

    assert do(q.peek(0)).order_id == 2
    assert do(q.peek(1)).order_id == 1
    assert do(q.cardinality()) == 3


@pytest.mark.parametrize("priority_queue", priority_queues)
def test_remove(event_loop, priority_queue):
    do = event_loop.run_until_complete
    q = priority_queue(event_loop, reverse=True)
    do(q.connect())
    order1 = get_bid_order(order_id=1)
    order2 = get_bid_order(order_id=2)
    order3 = get_bid_order(order_id=3)

    do(q.put(order1))
    do(q.put(order2))
    do(q.put(order3))

    do(q.remove(order2))
    do(q.remove(order3))
    assert do(q.cardinality()) == 1
    assert do(q.get()).order_id == 1


@pytest.mark.parametrize("priority_queue", priority_queues)
def test_peek_by_id(event_loop, priority_queue):
    do = event_loop.run_until_complete
    q = priority_queue(event_loop, reverse=True)
    do(q.connect())
    for i in range(1, 4):
        do(q.put(get_bid_order(order_id=i, price=i*100)))

    order = do(q.peek_by_id(2))
    assert order.order_id == 2
    assert order.price == 200


@pytest.mark.parametrize("priority_queue", [MemoryPriorityQueue])
def test_non_unique_order_id_raises_exception(event_loop, priority_queue):
    do = event_loop.run_until_complete
    q = priority_queue(event_loop, reverse=True)
    do(q.connect())
    do(q.put(get_bid_order(order_id=1, price=200)))
    with pytest.raises(ValueError):
        do(q.put(get_bid_order(order_id=1, price=100)))

