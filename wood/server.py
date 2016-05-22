# -*- coding: utf-8 -*-

import asyncio

from functools import partial
from .stock_exchange import StockExchange
from .utils import get_logger
from .clients import PrivateClients, PublicClients
from .pubsub import AsyncioQueuePubsub


class StockServer:
    def __init__(self, private_port=7001, public_port=7002, loop=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.public_pubsub = AsyncioQueuePubsub(self.loop)
        self.private_pubsub = AsyncioQueuePubsub(self.loop)
        self.public_clients = PublicClients(self.public_pubsub)
        self.private_clients = PrivateClients(self.private_pubsub)
        self.public_port = public_port
        self.private_port = private_port
        self.stock_exchange = StockExchange(self.private_pubsub, self.public_pubsub)
        self._logger = get_logger()

    def initialize_tasks(self):
        public_protocol = partial(PublicServerProtocol, self.public_clients)
        private_protocol = partial(PrivateServerProtocol, self.private_clients, self.stock_exchange)
        public_server_coro = self.loop.create_server(public_protocol, port=self.public_port)
        private_server_coro = self.loop.create_server(private_protocol, port=self.private_port)
        self.public_server = self.loop.run_until_complete(public_server_coro)
        self.private_server = self.loop.run_until_complete(private_server_coro)
        self.send_public_coro = self.loop.create_task(self.public_clients.consume())
        self.send_private_coro = self.loop.create_task(self.private_clients.consume())

        self._logger.info("Serving public on %s.", self.public_server.sockets[0].getsockname())
        self._logger.info("Serving private on %s.", self.private_server.sockets[0].getsockname())

    def shutdown_tasks(self):
        self.public_server.close()
        self.private_server.close()
        self.send_public_coro.cancel()
        self.send_private_coro.cancel()
        self.loop.run_until_complete(self.public_server.wait_closed())
        self.loop.run_until_complete(self.private_server.wait_closed())
        self.loop.close()
        self._logger.info("Server shutdown.")

    def run(self):
        self.initialize_tasks()
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown_tasks()

class PublicServerProtocol(asyncio.Protocol):
    def __init__(self, clients):
        self._clients = clients
        self._logger = get_logger()

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        self._logger.debug("Connection made %s", self.peername)
        self._clients.add(self)

    def connection_lost(self, exc):
        self._logger.debug("Connection lost %s", self.peername)
        self._clients.remove(self)


class PrivateServerProtocol(PublicServerProtocol):
    def __init__(self, clients, stock_exchange):
        super().__init__(clients)
        self._stock_exchange = stock_exchange

    def data_received(self, data):
        message = data.decode()
        self._logger.debug("Received %r from %r" % (message, self.peername))
        self._stock_exchange.handle_order(message, self.peername)