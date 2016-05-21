# -*- coding: utf-8 -*-

import asyncio
import argparse
import json
import random
import time

from .utils import get_logger

logger = get_logger()

MU = {
    "BUY": 95,
    "SELL": 105,
}
QUANTITY_MU = 100
SIGMA = 10

SIDES = ["BUY", "SELL"]

ORDER_ID_BIT_LEN = 64

LAMBDA_SLEEP = 1.0


def get_time_to_sleep():
    return random.expovariate(LAMBDA_SLEEP)


def get_order_id():
    return random.getrandbits(ORDER_ID_BIT_LEN)


def generate_random_order():
    order_id = get_order_id()
    side = random.choice(SIDES)
    price = round(random.gauss(MU[side], SIGMA))
    quantity = round(random.gauss(QUANTITY_MU, SIGMA))
    return get_order(order_id, side, price, quantity)


def get_order(order_id=1, side="BUY", price=100, quantity=100):
    return json.dumps({
        "message": "createOrder",
        "orderId": order_id,
        "side": side,
        "price": price,
        "quantity": quantity,
    })


@asyncio.coroutine
async def client_task(client_id, host, port):
    logger.info("Starting client #%s", client_id)
    reader, writer = await asyncio.open_connection(host, port)
    try:
        while True:
            order = generate_random_order()
            order_bytes = (order.encode() + b'\n')
            start = time.time()
            writer.write(order_bytes)
            await writer.drain()
            await reader.read(1000)
            duration = time.time() - start
            logger.info("Client received response #%s: %s took %s s", client_id, order, duration, extra={"duration": duration})
            await asyncio.sleep(get_time_to_sleep())
    finally:
        writer.close()


def start_clients(number_of_clients=1, host='127.0.0.1', port=7001):
    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(*[loop.create_task(client_task(i, host, port)) for i in range(number_of_clients)])
    try:
        loop.run_until_complete(tasks)
    except KeyboardInterrupt:
        tasks.cancel()
        loop.run_forever()
        tasks.exception()
    finally:
        loop.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number-of-clients", default=1, type=int)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("-p", "--port", default=7001, type=int)
    args = parser.parse_args()

    start_clients(args.number_of_clients, args.host, args.port)
