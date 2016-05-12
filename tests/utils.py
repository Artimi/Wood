# -*- coding: utf-8 -*-

from wood.limit_order_book import BidOrder, AskOrder, MarketBidOrder, MarketAskOrder


def get_bid_order(order_id=1, participant=1, time=1, price=100, quantity=50):
    return BidOrder(order_id, participant, time, price, quantity)


def get_ask_order(order_id=1, participant=1, time=1, price=100, quantity=50):
    return AskOrder(order_id, participant, time, price, quantity)


def get_market_bid_order(order_id=1, participant=1, time=1, quantity=50):
    return MarketBidOrder(order_id, participant, time, -1, quantity)


def get_market_ask_order(order_id=1, participant=1, time=1, quantity=50):
    return MarketAskOrder(order_id, participant, time, -1, quantity)
