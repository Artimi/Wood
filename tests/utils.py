# -*- coding: utf-8 -*-

from wood.limit_order_book import BidOrder, AskOrder


def get_bid_order(order_id=1, participant=1, time=1, price=100, quantity=50):
    return BidOrder(order_id, participant, time, price, quantity)


def get_ask_order(order_id=1, participant=1, time=1, price=100, quantity=50):
    return AskOrder(order_id, participant, time, price, quantity)
