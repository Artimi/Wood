# -*- coding: utf-8 -*-

import asyncio
import json

import pytest

from wood.server import StockServer

use_multiple_servers = [False]
if pytest.config.getoption("--redis"):
    use_multiple_servers.append(True)


def get_create_order(order_id=1, side="BUY", price=100, quantity=100):
    return json.dumps({
        "message": "createOrder",
        "orderId": order_id,
        "side": side,
        "price": price,
        "quantity": quantity,
    })


@pytest.yield_fixture(params=use_multiple_servers)
def server(request, event_loop, unused_tcp_port_factory):
    _server = StockServer(public_port=unused_tcp_port_factory(),
                          private_port=unused_tcp_port_factory(),
                          loop=event_loop,
                          multiple_servers=request.param)
    _server.initialize_tasks()
    yield _server
    _server.shutdown_tasks()


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
        data = await asyncio.wait_for(reader.readline(), .1)
        counter += 1
        responses.append(json.loads(data.decode()))
    return responses


def test_accepts_only_json(server):
    loop = server.loop
    responses = loop.run_until_complete(send_message(server.private_port, loop, "Hello World!"))
    response = responses[0]

    assert "error" in response
    assert "is not valid json" in response["error"]


def test_accepts_only_valid_order_message(server):
    loop = server.loop
    message = json.dumps({"message": "cancelOrder"})
    responses = loop.run_until_complete(send_message(server.private_port, loop, message))
    response = responses[0]

    assert "error" in response
    assert "is not valid order message" in response["error"]


def test_respond_with_execution_report(server):
    loop = server.loop
    message = get_create_order()
    responses = loop.run_until_complete(send_message(server.private_port, loop, message))
    response = responses[0]

    assert "error" not in response
    assert response["report"] == "NEW"
    assert response["message"] == "executionReport"
    assert response["orderId"] == 1


@pytest.mark.skip
def test_order_id_must_be_unique(server):
    loop = server.loop
    message = get_create_order()
    responses1 = loop.run_until_complete(send_message(server.private_port, loop, message))
    responses2 = loop.run_until_complete(send_message(server.private_port, loop, message))

    assert "error" in responses2[0]
    assert responses2[0]["error"] == "Order with order_id 1 is already present in queue."


def test_cancel_order(server):
    loop = server.loop
    message = get_create_order()
    response_new = loop.run_until_complete(send_message(server.private_port, loop, message))
    cancel_message = json.dumps(dict(message="cancelOrder", orderId=1))
    response_cancel = loop.run_until_complete(send_message(server.private_port, loop, cancel_message))

    assert "error" not in response_cancel
    assert response_cancel[0]["message"] == "executionReport"
    assert response_cancel[0]["orderId"] == 1
    assert response_cancel[0]["report"] == "CANCELLED"


def test_trade(server):
    loop = server.loop
    message_buy = get_create_order(price=110, quantity=110)
    message_sell = get_create_order(order_id=2, side="SELL", price=100, quantity=100)
    task_public = loop.create_task(listen(server.public_port, loop, messages=3))
    task_buy = loop.create_task(send_message(server.private_port, loop, message_buy, messages=2))
    task_sell = loop.create_task(send_message(server.private_port, loop, message_sell, messages=2))
    responses_buy = loop.run_until_complete(task_buy)
    responses_sell = loop.run_until_complete(task_sell)
    responses_public = loop.run_until_complete(task_public)

    assert responses_buy[0]["report"] == "NEW"
    assert responses_buy[1]["report"] == "FILL"

    assert responses_sell[0]["report"] == "NEW"
    assert responses_sell[1]["report"] == "FILL"

    assert responses_public[0]["type"] == "orderbook"
    assert responses_public[0]["side"] == "bid"
    assert responses_public[0]["price"] == 110
    assert responses_public[0]["quantity"] == 110

    assert responses_public[1]["type"] == "orderbook"
    assert responses_public[1]["side"] == "ask"
    assert responses_public[1]["price"] == 100
    assert responses_public[1]["quantity"] == 100

    assert responses_public[2]["type"] == "trade"
    assert responses_public[2]["price"] == 110
    assert responses_public[2]["quantity"] == 100
