# -*- coding: utf-8 -*-

import asyncio
from wood.limit_order_book import LimitOrderBook
from .utils import get_bid_order, get_ask_order, get_market_bid_order, get_market_ask_order


def test_add(event_loop):
    do = event_loop.run_until_complete
    l = LimitOrderBook(event_loop)
    b_order1 = get_bid_order(price=100)
    a_order1 = get_ask_order(price=200)
    do(l.add(b_order1))
    do(l.add(a_order1))
    bid_queue_first = do(l.bid_queue.peek(0))
    ask_queue_first = do(l.ask_queue.peek(0))
    assert bid_queue_first == b_order1
    assert ask_queue_first == a_order1


def test_trade(event_loop):
    do = event_loop.run_until_complete
    l = LimitOrderBook(event_loop)
    b_order1 = get_bid_order(price=100, quantity=50)
    a_order1 = get_ask_order(price=100, quantity=50)
    do(l.add(b_order1))
    do(l.add(a_order1))
    trades = do(l.check_trades())
    assert len(trades) == 1
    assert trades[0].price == 100
    assert trades[0].quantity == 50
    assert trades[0].bid_order == b_order1
    assert trades[0].ask_order == a_order1
    assert len(l.ask_queue) == 0
    assert len(l.bid_queue) == 0


def test_trade_higher_quantity_ask(event_loop):
    do = event_loop.run_until_complete
    l = LimitOrderBook(event_loop)
    b_order1 = get_bid_order(price=100, quantity=50)
    a_order1 = get_ask_order(price=100, quantity=70)
    do(l.add(b_order1))
    do(l.add(a_order1))
    trades = do(l.check_trades())
    assert len(trades) == 1
    assert trades[0].price == 100
    assert trades[0].quantity == 50
    assert trades[0].bid_order == b_order1
    assert trades[0].ask_order == a_order1
    assert len(l.bid_queue) == 0
    assert len(l.ask_queue) == 1
    assert do(l.ask_queue.peek(0)).quantity == 20


def test_trade_highest_price_bid(event_loop):
    do = event_loop.run_until_complete
    l = LimitOrderBook(event_loop)
    b_order1 = get_bid_order(price=120, quantity=50)
    a_order1 = get_ask_order(price=100, quantity=50)
    do(l.add(b_order1))
    do(l.add(a_order1))
    trades = do(l.check_trades())
    assert len(trades) == 1
    assert trades[0].price == 120
    assert trades[0].quantity == 50
    assert trades[0].bid_order == b_order1
    assert trades[0].ask_order == a_order1
    assert len(l.bid_queue) == 0
    assert len(l.ask_queue) == 0


def test_trade_multiple_orders(event_loop):
    do = event_loop.run_until_complete
    l = LimitOrderBook(event_loop)
    b_order1 = get_bid_order(order_id=1, price=100, quantity=100)
    b_order2 = get_bid_order(order_id=2, price=110, quantity=50)
    b_order3 = get_bid_order(order_id=3, price=120, quantity=150)
    a_order1 = get_ask_order(price=100, quantity=350)
    do(l.add(b_order1))
    do(l.add(b_order2))
    do(l.add(b_order3))
    do(l.add(a_order1))
    trades = do(l.check_trades())
    assert len(trades) == 3

    assert trades[0].price == 120
    assert trades[0].bid_order == b_order3

    assert trades[1].price == 110
    assert trades[1].bid_order == b_order2

    assert trades[2].price == 100
    assert trades[2].bid_order == b_order1

    assert len(l.ask_queue) == 1
    assert do(l.ask_queue.peek(0)).quantity == 50
    assert do(l.ask_queue.peek(0)).price == 100


def test_cancel_order(event_loop):
    do = event_loop.run_until_complete
    l = LimitOrderBook(event_loop)
    b_order1 = get_bid_order(order_id=123)
    do(l.add(b_order1))

    assert len(l.bid_queue) == 1
    do(l.cancel(123))
    assert len(l.bid_queue) == 0


def test_market_order(event_loop):
    do = event_loop.run_until_complete
    l = LimitOrderBook(event_loop)
    a_order = get_ask_order(quantity=100, price=100)
    m_order = get_market_bid_order(order_id=2, quantity=150)
    do(l.add(a_order))
    do(l.add(m_order))
    trades = do(l.check_trades())

    assert len(trades) == 1
    assert trades[0].price == 100
    assert trades[0].quantity == 100
    assert trades[0].bid_order == m_order
    assert trades[0].ask_order == a_order
    assert len(l.bid_queue) == 1
    assert len(l.ask_queue) == 0


def test_two_market_orders(event_loop):
    do = event_loop.run_until_complete
    l = LimitOrderBook(event_loop)
    ma_order = get_market_ask_order(quantity=100)
    mb_order = get_market_bid_order(order_id=2, quantity=100)
    do(l.add(ma_order))
    do(l.add(mb_order))
    trades = do(l.check_trades())

    assert len(trades) == 1
    assert trades[0].price == 0
    assert trades[0].quantity == 100
    assert trades[0].bid_order == mb_order
    assert trades[0].ask_order == ma_order
    assert len(l.bid_queue) == 0
    assert len(l.ask_queue) == 0
