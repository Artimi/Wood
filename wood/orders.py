# -*- coding: utf-8 -*-
from collections import namedtuple


class BidOrder(namedtuple('BidOrder', 'time order_id participant price quantity')):
    """BUY Order"""
    __slots__ = ()
    side = "bid"

    def __lt__(self, other):
        return (self.price > other.price) or (self.price == other.price and self.time < other.time)


class AskOrder(namedtuple('AskOrder', 'time order_id participant price quantity')):
    """SELL Order"""
    __slots__ = ()
    side = "ask"

    def __lt__(self, other):
        return (self.price, self.time) < (other.price, other.time)


class MarketBidOrder(BidOrder):
    def __lt__(self, other):
        if isinstance(other, MarketBidOrder):
            return self.time < other.time
        else:
            return True


class MarketAskOrder(AskOrder):
    def __lt__(self, other):
        if isinstance(other, MarketAskOrder):
            return self.time < other.time
        else:
            return True


class Trade(namedtuple('Trade', 'time price quantity bid_order ask_order')):
    __slots__ = ()

    def __str__(self):
        return "{} - {} @ {}".format(self.time, self.quantity, self.price)