# -*- coding: utf-8 -*-
import time
import json
from voluptuous import Schema, Any, Invalid, All, Range
import logging

from .limit_order_book import LimitOrderBook, BidOrder, AskOrder, MarketBidOrder, MarketAskOrder

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
    def __init__(self, private_queue, public_queue):
        self._private_queue = private_queue
        self._public_queue = public_queue
        self.limit_order_book = LimitOrderBook()

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
        return result

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
        return result

    @staticmethod
    def _get_order_book_report(side, price, quantity):
        result = {
            "type": "orderbook",
            "side": side,
            "price": price,
            "quantity": quantity
        }
        return result

    @staticmethod
    def _get_error_report(error):
        result = {
            "error": error
        }
        return result

    def handle_order(self, message, participant):
        order_dict = self.validate_message(message, participant)
        if order_dict is None:
            return
        if order_dict["message"] in ("createOrder", "marketOrder"):
            self._handle_create_order(order_dict, participant)
        elif order_dict["message"] == "cancelOrder":
            self._handle_cancel_order(order_dict, participant)

    def _handle_create_order(self, order_dict, participant):
        order = self.create_order(order_dict, participant)
        try:
            self.limit_order_book.add(order)
        except ValueError as e:
            self._private_queue.put_nowait((participant, self._get_error_report(str(e))))
            return
        new_report = self._get_execution_report(order_dict["orderId"], "NEW")
        self._private_queue.put_nowait((participant, new_report))
        self._public_queue.put_nowait(self._get_order_book_report(order.side, order.price, order.quantity))
        for trade in self.limit_order_book.check_trades():
            bid_fill_report = self._get_fill_report(trade, trade.bid_order)
            self._private_queue.put_nowait((trade.bid_order.participant, bid_fill_report))
            ask_fill_report = self._get_fill_report(trade, trade.ask_order)
            self._private_queue.put_nowait((trade.ask_order.participant, ask_fill_report))
            self._public_queue.put_nowait(self._get_trade_report(trade))
        logging.debug(self.limit_order_book)

    def _handle_cancel_order(self, order_dict, participant):
        if self.limit_order_book.cancel(order_dict["orderId"]):
            cancel_report = self._get_execution_report(order_dict["orderId"], "CANCELLED")
            self._private_queue.put_nowait((participant, cancel_report))
        else:
            error_report = self._get_error_report("OrderId {} was not in our database.".format(order_dict["orderId"]))
            self._private_queue.put_nowait((participant, error_report))

    def validate_message(self, message, participant):
        try:
            order_dict = json.loads(message)
        except ValueError:
            error_report = self._get_error_report("Message '{}' is not valid json.".format(message))
            self._private_queue.put_nowait((participant, error_report))
            return None
        try:
            message_schema(order_dict)
        except Invalid as e:
            error_report = self._get_error_report("Message '{}' is not valid order message because {}.".format(message, e))
            self._private_queue.put_nowait((participant, error_report))
            return None
        return order_dict
