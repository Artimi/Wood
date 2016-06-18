# -*- coding: utf-8 -*-

from .utils import get_ask_order, get_bid_order, get_market_bid_order


def test_bid_order_comparison():
    order1 = get_bid_order(price=100)
    order2 = get_bid_order(price=120)
    assert order2 < order1


def test_bid_order_comparison_same_price():
    order1 = get_bid_order(time=2.5)
    order2 = get_bid_order(time=2.7)
    assert order1 < order2


def test_ask_order_comparison():
    order1 = get_ask_order(price=100)
    order2 = get_ask_order(price=120)
    assert order1 < order2


def test_ask_order_comparison_same_price():
    order1 = get_ask_order(time=2.5)
    order2 = get_ask_order(time=2.7)
    assert order1 < order2


def test_market_bid_order_comparison():
    market_order = get_market_bid_order()
    order = get_bid_order()
    assert market_order < order


def test_two_market_bids_ordered_by_time():
    order1 = get_market_bid_order(time=1)
    order2 = get_market_bid_order(time=2)
    assert order1 < order2
    assert not(order2 < order1)
