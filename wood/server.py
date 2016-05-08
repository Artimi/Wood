# -*- coding: utf-8 -*-

import asyncio
import logging

from functools import partial
from public_server import Clients, PublicServerProtocol, PrivateServerProtocol
from stock_exchange import StockExchange

LOGGING_PROPERTIES = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # "filename": config.LOG_DELETER,
    "level": logging.DEBUG,
}
logging.basicConfig(**LOGGING_PROPERTIES)

LOCALHOST = '127.0.0.1'


class StockServer:
    def __init__(self, private_port=7001, public_port=7002):
        self.public_clients = Clients()
        self.private_clients = Clients()
        self.public_port = public_port
        self.private_port = private_port
        self.loop = asyncio.get_event_loop()
        self.public_queue = asyncio.Queue(loop=self.loop)
        self.private_queue = asyncio.Queue(loop=self.loop)
        self.stock_exchange = StockExchange(self.private_queue, self.public_queue)

    @asyncio.coroutine
    def send_public(self):
        while True:
            message = yield from self.public_queue.get()
            self.public_clients.broadcast(message)

    @asyncio.coroutine
    def send_private(self):
        while True:
            participant, message = yield from self.private_queue.get()
            self.private_clients.send(participant, message)

    def run(self):
        public_protocol = partial(PublicServerProtocol, self.public_clients)
        private_protocol = partial(PrivateServerProtocol, self.private_clients, self.stock_exchange)
        public_server_coro = self.loop.create_server(public_protocol, port=self.public_port)
        private_server_coro = self.loop.create_server(private_protocol, port=self.private_port)
        public_server = self.loop.run_until_complete(public_server_coro)
        private_server = self.loop.run_until_complete(private_server_coro)
        send_public = self.loop.create_task(self.send_public())
        send_private = self.loop.create_task(self.send_private())

        logging.info("Serving public on %s.", public_server.sockets[0].getsockname())
        logging.info("Serving private on %s.", private_server.sockets[0].getsockname())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        public_server.close()
        private_server.close()
        send_public.cancel()
        send_private.cancel()
        self.loop.run_until_complete(public_server.wait_closed())
        self.loop.run_until_complete(private_server.wait_closed())
        self.loop.close()


def main():
    stock_server = StockServer()
    stock_server.run()

if __name__ == '__main__':
    main()
