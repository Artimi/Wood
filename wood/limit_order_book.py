# -*- coding: utf-8 -*-

import logging

import time
from .priority_queue import MemoryPriorityQueue
from collections import namedtuple


class BidOrder(namedtuple('BidOrder', 'order_id participant time price quantity')):
    """BUY Order"""
    __slots__ = ()
    side = "bid"

    def __lt__(self, other):
        return (self.price > other.price) or (self.price == other.price and self.time < other.time)


class AskOrder(namedtuple('AskOrder', 'order_id participant time price quantity')):
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


class LimitOrderBook:
    def __init__(self, PriorityQueue=MemoryPriorityQueue):
        self.bid_queue = PriorityQueue()
        self.ask_queue = PriorityQueue()
        self.trades = []

    def add(self, order):
        if isinstance(order, BidOrder):
            self.bid_queue.put(order)
        elif isinstance(order, AskOrder):
            self.ask_queue.put(order)

    def cancel(self, order_id):
        return self._cancel_from_queue(self.bid_queue, order_id) or self._cancel_from_queue(self.ask_queue, order_id)

    @staticmethod
    def _cancel_from_queue(queue, order_id):
        logging.debug("Cancelling order %s", order_id)
        order = queue.peek_by_id(order_id)
        if order is None:
            return False
        # Here could be some test to check that participant has right to cancel order
        queue.remove(order)
        return True

    @staticmethod
    def can_trade(bid_order, ask_order):
        if isinstance(bid_order, MarketBidOrder) or isinstance(ask_order, MarketAskOrder):
            return True
        else:
            return bid_order.price >= ask_order.price

    @staticmethod
    def get_price(bid_order, ask_order):
        if isinstance(bid_order, MarketBidOrder) and isinstance(ask_order, MarketAskOrder):
            return 0  # was not specified, participants exchange stock for free
        elif isinstance(bid_order, MarketBidOrder):
            return ask_order.price
        elif isinstance(ask_order, MarketAskOrder):
            return bid_order.price
        else:
            return bid_order.price

    def check_trades(self):
        while not self.bid_queue.empty() and \
              not self.ask_queue.empty() and \
              self.can_trade(self.bid_queue.peek(0), self.ask_queue.peek(0)):
            bid_order = self.bid_queue.get()
            ask_order = self.ask_queue.get()
            price = self.get_price(bid_order, ask_order)
            quantity_difference = bid_order.quantity - ask_order.quantity
            if quantity_difference < 0:
                changed_ask_order = ask_order._replace(quantity=abs(quantity_difference))
                self.ask_queue.put(changed_ask_order)
                quantity = bid_order.quantity
                logging.info("Reinsert %s as %s", ask_order, changed_ask_order)
            elif quantity_difference > 0:
                changed_bid_order = bid_order._replace(quantity=quantity_difference)
                self.bid_queue.put(changed_bid_order)
                quantity = ask_order.quantity
                logging.info("Reinsert %s as %s", bid_order, changed_bid_order)
            else:
                quantity = bid_order.quantity
            logging.info("Traded %s with %s", bid_order, ask_order)
            trade = Trade(time.time(), price, quantity, bid_order, ask_order)
            self.trades.append(trade)
            yield trade

    def __str__(self):
        trades = "\n".join(map(str, self.trades))
        return "BID\n{}\n\nASK\n{}\nTRADES\n{}".format(self.bid_queue, self.ask_queue, trades)
