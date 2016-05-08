# -*- coding: utf-8 -*-

import asyncio
import json

import pytest

from wood.server import StockServer


def get_create_order(order_id=1, side="BUY", price=100, quantity=100):
    return json.dumps({
        "message": "createOrder",
        "orderId": order_id,
        "side": side,
        "price": price,
        "quantity": quantity,
    })


@pytest.yield_fixture
def server(event_loop):
    server = StockServer(public_port=7002, private_port=7001, loop=event_loop)
    server.initialize_tasks()
    yield server
    server.shutdown_tasks()


@asyncio.coroutine
async def send_message(port, loop, message, interface='127.0.0.1', messages=1):
    reader, writer = await asyncio.open_connection(interface, port, loop=loop)
    writer.write(message.encode())
    await writer.drain()
    return await (listen(port, loop, interface, messages, reader, writer))

@asyncio.coroutine
async def listen(port, loop, interface='127.0.0.1', messages=1, reader=None, writer=None):
    counter = 0
    responses = []
    if reader is None or writer is None:
        reader, writer = await asyncio.open_connection(interface, port, loop=loop)
    data = True
    while data and counter < messages:
        data = await reader.readline()
        counter += 1
        responses.append(json.loads(data.decode()))
    return responses


def test_accepts_only_json(server):
    loop = server.loop
    responses = loop.run_until_complete(send_message(7001, loop, "Hello World!"))
    response = responses[0]

    assert "error" in response
    assert "is not valid json" in response["error"]


def test_accepts_only_valid_order_message(server):
    loop = server.loop
    message = json.dumps({"message": "cancelOrder"})
    responses = loop.run_until_complete(send_message(7001, loop, message))
    response = responses[0]

    assert "error" in response
    assert "is not valid order message" in response["error"]


def test_respond_with_execution_report(server):
    loop = server.loop
    message = get_create_order()
    responses = loop.run_until_complete(send_message(7001, loop, message))
    response = responses[0]

    assert "error" not in response
    assert response["report"] == "NEW"
    assert response["message"] == "executionReport"
    assert response["orderId"] == 1


def test_order_id_must_be_unique(server):
    loop = server.loop
    message = get_create_order()
    responses1 = loop.run_until_complete(send_message(7001, loop, message))
    responses2 = loop.run_until_complete(send_message(7001, loop, message))

    assert "error" in responses2[0]
    assert responses2[0]["error"] == "Order with order_id 1 is already present in queue."


def test_trade(server):
    loop = server.loop
    message_buy = get_create_order()
    message_sell = get_create_order(order_id=2, side="SELL")
    task_public = loop.create_task(listen(7002,loop))
    task_buy = loop.create_task(send_message(7001, loop, message_buy, messages=2))
    task_sell = loop.create_task(send_message(7001, loop, message_sell, messages=2))
    responses_buy = loop.run_until_complete(task_buy)
    responses_sell = loop.run_until_complete(task_sell)
    responses_public = loop.run_until_complete(task_public)

    assert responses_buy[0]["report"] == "NEW"
    assert responses_buy[1]["report"] == "FILL"

    assert responses_sell[0]["report"] == "NEW"
    assert responses_sell[1]["report"] == "FILL"

    assert responses_public[0]["type"] == "trade"
    assert responses_public[0]["price"] == 100
    assert responses_public[0]["quantity"] == 100
