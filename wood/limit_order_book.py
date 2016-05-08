# -*- coding: utf-8 -*-

import logging

import time
from wood.priority_queue import MemoryPriorityQueue
from collections import namedtuple


class BidOrder(namedtuple('BidOrder', 'order_id participant time price quantity')):
    """BUY Order"""
    __slots__ = ()

    def __lt__(self, other):
        return (self.price > other.price) or (self.price == other.price and self.time < other.time)

    def __le__(self, other):
        return (self.price > other.price) or (self.price == other.price and self.time < other.time) or self.__eq__(
            other)

    def __ge__(self, other):
        return (self.price < other.price) or (self.price == other.price and self.time > other.time) or self.__eq__(
            other)

    def __gt__(self, other):
        return (self.price < other.price) or (self.price == other.price and self.time > other.time)



class AskOrder(namedtuple('AskOrder', 'order_id participant time price quantity')):
    """SELL Order"""
    __slots__ = ()

    def __lt__(self, other):
        return (self.price, self.time) < (other.price, other.time)

    def __le__(self, other):
        return (self.price, self.time) <= (other.price, other.time)

    def __ge__(self, other):
        return (self.price, self.time) >= (other.price, other.time)

    def __gt__(self, other):
        return (self.price, self.time) > (other.price, other.time)


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

    def cancel(self, order_id, participant):
        self._cancel_from_queue(self.bid_queue, order_id, participant)
        self._cancel_from_queue(self.ask_queue, order_id, participant)

    @staticmethod
    def _cancel_from_queue(queue, order_id, participant):
        order = queue.peek_by_id(order_id)
        if order is None:
            return
        if order.participant == participant:
            queue.remove(order)
        else:
            logging.warning("Attempt to remove order %s of other participant by participant %s", order, participant)

    def check_trades(self):
        while not self.bid_queue.empty() and \
              not self.ask_queue.empty() and\
              self.bid_queue.peek(0).price >= self.ask_queue.peek(0).price:
            bid_order = self.bid_queue.get()
            ask_order = self.ask_queue.get()
            price = bid_order.price
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
