# -*- coding: utf-8 -*-

from .utils import get_ask_order, get_bid_order


def test_bid_order_comparison():
    order1 = get_bid_order(price=100)
    order2 = get_bid_order(price=120)
    assert order1 > order2


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


