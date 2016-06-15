# -*- coding: utf-8 -*-

import asyncio
import time

from .orders import BidOrder, AskOrder, MarketBidOrder, MarketAskOrder, Trade
from .priority_queue import MemoryPriorityQueue
from .utils import get_logger


class LimitOrderBook:
    """ Structure that where matching of orders happens. """
    def __init__(self, loop, priority_queue=MemoryPriorityQueue):
        self.bid_queue = priority_queue(loop, reverse=True)
        loop.run_until_complete(self.bid_queue.connect())
        self.ask_queue = priority_queue(loop)
        loop.run_until_complete(self.ask_queue.connect())
        self._logger = get_logger()

    @asyncio.coroutine
    async def close(self):
        await self.bid_queue.close()
        await self.ask_queue.close()

    @asyncio.coroutine
    async def add(self, order):
        """ Add new order to limit order book. """
        if isinstance(order, BidOrder):
            await self.bid_queue.put(order)
        elif isinstance(order, AskOrder):
            await self.ask_queue.put(order)
        self._logger.info("Added new order %s", order, extra=order._asdict())

    @asyncio.coroutine
    async def cancel(self, order_id):
        """ Remove order with `order_id` from limit order book. """
        cancel_bid = await self._cancel_from_queue(self.bid_queue, order_id)
        cancel_ask = await self._cancel_from_queue(self.ask_queue, order_id)
        return cancel_bid or cancel_ask

    @asyncio.coroutine
    async def _cancel_from_queue(self, queue, order_id):
        self._logger.debug("Cancelling order %s", order_id)
        order = await queue.peek_by_id(order_id)
        if order is None:
            return False
        # Here could be some test to check that participant has right to cancel order
        await queue.remove(order)
        return True

    @staticmethod
    def can_trade(bid_order, ask_order):
        """ Return True if `bid_order` and `ask_order` can be traded. """
        if isinstance(bid_order, MarketBidOrder) or isinstance(ask_order, MarketAskOrder):
            return True
        else:
            return bid_order.price >= ask_order.price

    @staticmethod
    def get_price(bid_order, ask_order):
        """ Return price of trade between `bid_order` and `ask_order`. """
        if isinstance(bid_order, MarketBidOrder) and isinstance(ask_order, MarketAskOrder):
            return 0  # was not specified, participants exchange stock for free
        elif isinstance(bid_order, MarketBidOrder):
            return ask_order.price
        elif isinstance(ask_order, MarketAskOrder):
            return bid_order.price
        else:
            return bid_order.price

    @asyncio.coroutine
    async def check_trades(self):
        """ Main function that trades all orders until it cannot continue. """
        trades = []
        while not await self.bid_queue.empty() and not await self.ask_queue.empty() and \
                self.can_trade(await self.bid_queue.peek(0), await self.ask_queue.peek(0)):
            bid_order = await self.bid_queue.get()
            ask_order = await self.ask_queue.get()
            price = self.get_price(bid_order, ask_order)
            quantity_difference = bid_order.quantity - ask_order.quantity
            if quantity_difference < 0:
                changed_ask_order = ask_order._replace(quantity=abs(quantity_difference))
                await self.ask_queue.put(changed_ask_order)
                quantity = bid_order.quantity
                self._logger.info("Reinsert %s as %s", ask_order, changed_ask_order)
            elif quantity_difference > 0:
                changed_bid_order = bid_order._replace(quantity=quantity_difference)
                await self.bid_queue.put(changed_bid_order)
                quantity = ask_order.quantity
                self._logger.info("Reinsert %s as %s", bid_order, changed_bid_order)
            else:
                quantity = bid_order.quantity
            trade = Trade(time.time(), price, quantity, bid_order, ask_order)
            self._logger.info("Traded %s with %s", bid_order, ask_order, extra={"bid": bid_order._asdict(),
                                                                                "ask": ask_order._asdict(),
                                                                                "price": price, "quantity": quantity})
            trades.append(trade)
        return trades

    def __str__(self):
        return "BID\n{}\n\nASK\n{}\n".format(self.bid_queue, self.ask_queue)
