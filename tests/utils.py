# -*- coding: utf-8 -*-

from wood.orders import BidOrder, AskOrder, MarketBidOrder, MarketAskOrder


def get_bid_order(order_id=1, participant=1, time=1, price=100, quantity=50):
    return BidOrder(time, order_id, participant, price, quantity)


def get_ask_order(order_id=1, participant=1, time=1, price=100, quantity=50):
    return AskOrder(time, order_id, participant, price, quantity)


def get_market_bid_order(order_id=1, participant=1, time=1, quantity=50):
    return MarketBidOrder(time, order_id, participant, -1, quantity)


def get_market_ask_order(order_id=1, participant=1, time=1, quantity=50):
    return MarketAskOrder(time, order_id, participant, -1, quantity)
