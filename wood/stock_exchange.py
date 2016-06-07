# -*- coding: utf-8 -*-
import asyncio
import time
import json
from voluptuous import Schema, Any, Invalid, All, Range

from .limit_order_book import LimitOrderBook, BidOrder, AskOrder, MarketBidOrder, MarketAskOrder
from .utils import get_logger


message_schema = Schema(Any(
    {
        "message": "createOrder",
        "orderId": int,
        "side": Any("BUY", "SELL"),
        "price": All(int, Range(min=0)),
        "quantity": All(int, Range(min=0)),
    },
    {
        "message": "cancelOrder",
        "orderId": int,
    },
    {
        "message": "marketOrder",
        "orderId": int,
        "side": Any("BUY", "SELL"),
        "quantity": All(int, Range(min=0)),
    },
    required=True))


class StockExchange:
    def __init__(self, private_publisher, public_publisher):
        self._private_publisher = private_publisher
        self._public_publisher = public_publisher
        self.limit_order_book = LimitOrderBook()
        self._logger = get_logger()

    def create_order(self, order_dict, participant):
        order_types = {
            "BUY": {
                "createOrder": BidOrder,
                "marketOrder": MarketBidOrder,
            },
            "SELL": {
                "createOrder": AskOrder,
                "marketOrder": MarketAskOrder,
            }
        }
        Order = order_types[order_dict["side"]][order_dict["message"]]
        price = -1 if order_dict["message"] == "marketOrder" else order_dict["price"]
        return Order(order_dict["orderId"],
                     participant,
                     time.time(),
                     price,
                     order_dict["quantity"])

    @staticmethod
    def _get_execution_report(order_id, report, **kwargs):
        result = {
            "message": "executionReport",
            "orderId": order_id,
            "report": report
        }
        result.update(kwargs)
        return json.dumps(result)

    def _get_fill_report(self, trade, order):
        return self._get_execution_report(order.order_id, "FILL", price=trade.price, quantity=trade.quantity)

    @staticmethod
    def _get_trade_report(trade):
        result = {
            "type": "trade",
            "time": trade.time,
            "price": trade.price,
            "quantity": trade.quantity,
        }
        return json.dumps(result)

    @staticmethod
    def _get_order_book_report(side, price, quantity):
        result = {
            "type": "orderbook",
            "side": side,
            "price": price,
            "quantity": quantity
        }
        return json.dumps(result)

    @staticmethod
    def _get_error_report(error):
        result = {
            "error": error
        }
        return json.dumps(result)

    @asyncio.coroutine
    async def handle_order(self, message, participant):
        order_dict = await self.validate_message(message, participant)
        if order_dict is None:
            return
        if order_dict["message"] in ("createOrder", "marketOrder"):
            await self._handle_create_order(order_dict, participant)
        elif order_dict["message"] == "cancelOrder":
            await self._handle_cancel_order(order_dict, participant)

    @asyncio.coroutine
    async def _handle_create_order(self, order_dict, participant):
        order = self.create_order(order_dict, participant)
        try:
            await self.limit_order_book.add(order)
        except ValueError as e:
            await self._private_publisher.publish(participant, self._get_error_report(str(e)))
            return
        new_report = self._get_execution_report(order_dict["orderId"], "NEW")
        await self._private_publisher.publish(participant, new_report)
        await self._public_publisher.publish("public", self._get_order_book_report(order.side, order.price, order.quantity))
        trades = await self.limit_order_book.check_trades()
        for trade in trades:
            bid_fill_report = self._get_fill_report(trade, trade.bid_order)
            await self._private_publisher.publish(trade.bid_order.participant, bid_fill_report)
            ask_fill_report = self._get_fill_report(trade, trade.ask_order)
            await self._private_publisher.publish(trade.ask_order.participant, ask_fill_report)
            await self._public_publisher.publish("public", self._get_trade_report(trade))

    @asyncio.coroutine
    async def _handle_cancel_order(self, order_dict, participant):
        cancelled = await self.limit_order_book.cancel(order_dict["orderId"])
        if cancelled:
            cancel_report = self._get_execution_report(order_dict["orderId"], "CANCELLED")
            await self._private_publisher.publish(participant, cancel_report)
        else:
            error_report = self._get_error_report("OrderId {} was not in our database.".format(order_dict["orderId"]))
            await self._private_publisher.publish(participant, error_report)

    @asyncio.coroutine
    async def validate_message(self, message, participant):
        try:
            order_dict = json.loads(message)
        except ValueError:
            error_report = self._get_error_report("Message '{}' is not valid json.".format(message))
            await self._private_publisher.publish(participant, error_report)
            return None
        try:
            message_schema(order_dict)
        except Invalid as e:
            error_report = self._get_error_report("Message '{}' is not valid order message because {}.".format(message, e))
            await self._private_publisher.publish(participant, error_report)
            return None
        return order_dict
