# -*- coding: utf-8 -*-

from wood.limit_order_book import LimitOrderBook
from .utils import get_bid_order, get_ask_order


def test_add():
    l = LimitOrderBook()
    b_order1 = get_bid_order(price=100)
    a_order1 = get_ask_order(price=200)
    l.add(b_order1)
    l.add(a_order1)
    assert l.bid_queue.peek(0) == b_order1
    assert l.ask_queue.peek(0) == a_order1


def test_trade():
    l = LimitOrderBook()
    b_order1 = get_bid_order(price=100, quantity=50)
    a_order1 = get_ask_order(price=100, quantity=50)
    l.add(b_order1)
    l.add(a_order1)
    for trade in l.check_trades():
        pass
    assert len(l.trades) == 1
    assert l.trades[0].price == 100
    assert l.trades[0].quantity == 50
    assert l.trades[0].bid_order == b_order1
    assert l.trades[0].ask_order == a_order1
    assert len(l.ask_queue) == 0
    assert len(l.bid_queue) == 0


def test_trade_higher_quantity_ask():
    l = LimitOrderBook()
    b_order1 = get_bid_order(price=100, quantity=50)
    a_order1 = get_ask_order(price=100, quantity=70)
    l.add(b_order1)
    l.add(a_order1)
    for trade in l.check_trades():
        pass
    assert len(l.trades) == 1
    assert l.trades[0].price == 100
    assert l.trades[0].quantity == 50
    assert l.trades[0].bid_order == b_order1
    assert l.trades[0].ask_order == a_order1
    assert len(l.bid_queue) == 0
    assert len(l.ask_queue) == 1
    assert l.ask_queue.peek(0).quantity == 20


def test_trade_highest_price_bid():
    l = LimitOrderBook()
    b_order1 = get_bid_order(price=120, quantity=50)
    a_order1 = get_ask_order(price=100, quantity=50)
    l.add(b_order1)
    l.add(a_order1)
    for trade in l.check_trades():
        pass
    assert len(l.trades) == 1
    assert l.trades[0].price == 120
    assert l.trades[0].quantity == 50
    assert l.trades[0].bid_order == b_order1
    assert l.trades[0].ask_order == a_order1
    assert len(l.bid_queue) == 0
    assert len(l.ask_queue) == 0


def test_trade_multiple_orders():
    l = LimitOrderBook()
    b_order1 = get_bid_order(order_id= 1, price=100, quantity=100)
    b_order2 = get_bid_order(order_id=2, price=110, quantity=50)
    b_order3 = get_bid_order(order_id=3, price=120, quantity=150)
    a_order1 = get_ask_order(price=100, quantity=350)
    l.add(b_order1)
    l.add(b_order2)
    l.add(b_order3)
    l.add(a_order1)
    for trade in l.check_trades():
        pass
    assert len(l.trades) == 3

    assert l.trades[0].price == 120
    assert l.trades[0].bid_order == b_order3

    assert l.trades[1].price == 110
    assert l.trades[1].bid_order == b_order2

    assert l.trades[2].price == 100
    assert l.trades[2].bid_order == b_order1

    assert len(l.ask_queue) == 1
    assert l.ask_queue.peek(0).quantity == 50
    assert l.ask_queue.peek(0).price == 100


def test_cancel_order():
    l = LimitOrderBook()
    b_order1 = get_bid_order(order_id=123, participant=1)
    l.add(b_order1)

    assert len(l.bid_queue) == 1
    l.cancel(123, 1)
    assert len(l.bid_queue) == 0
