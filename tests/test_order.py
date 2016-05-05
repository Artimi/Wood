# -*- coding: utf-8 -*-

from wood.limit_order_book import BidOrder, AskOrder


def test_bid_order_comparison():
    order1 = BidOrder(1, 1, 2.5, 100, 50)
    order2 = BidOrder(2, 1, 2.7, 120, 50)
    assert order1 < order2


def test_bid_order_comparison_same_price():
    order1 = BidOrder(1, 1, 2.5, 100, 50)
    order2 = BidOrder(2, 1, 2.7, 100, 50)
    assert order1 < order2


def test_ask_order_comparison():
    order1 = AskOrder(1, 1, 2.5, 100, 50)
    order2 = AskOrder(2, 1, 2.7, 120, 50)
    assert order1 > order2


def test_ask_order_comparison_same_price():
    order1 = AskOrder(1, 1, 2.5, 100, 50)
    order2 = AskOrder(2, 1, 2.7, 100, 50)
    assert order1 < order2


