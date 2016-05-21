# -*- coding: utf-8 -*-

import asyncio
import json

from functools import partial
from .stock_exchange import StockExchange
from .utils import get_logger


class StockServer:
    def __init__(self, private_port=7001, public_port=7002, loop=None):
        self.public_clients = Clients()
        self.private_clients = Clients()
        self.public_port = public_port
        self.private_port = private_port
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.public_queue = asyncio.Queue(loop=self.loop)
        self.private_queue = asyncio.Queue(loop=self.loop)
        self.stock_exchange = StockExchange(self.private_queue, self.public_queue)
        self._logger = get_logger()

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

    def initialize_tasks(self):
        public_protocol = partial(PublicServerProtocol, self.public_clients)
        private_protocol = partial(PrivateServerProtocol, self.private_clients, self.stock_exchange)
        public_server_coro = self.loop.create_server(public_protocol, port=self.public_port)
        private_server_coro = self.loop.create_server(private_protocol, port=self.private_port)
        self.public_server = self.loop.run_until_complete(public_server_coro)
        self.private_server = self.loop.run_until_complete(private_server_coro)
        self.send_public_coro = self.loop.create_task(self.send_public())
        self.send_private_coro = self.loop.create_task(self.send_private())

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


class Clients:
    def __init__(self):
        self._clients = {}
        self._logger = get_logger()

    def add(self, client):
        self._clients[client.peername] = client

    def remove(self, client):
        del self._clients[client.peername]

    def broadcast(self, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        message = message + "\n"
        for participant, client in self._clients.items():
            self._logger.debug("Broadcast %r to %s", message, participant)
            client.transport.write(message.encode())

    def send(self, participant, message):
        """
        Send message to participant. May raise `KeyError` if participant already left.
        """
        client = self._clients[participant]
        if isinstance(message, dict):
            message = json.dumps(message)
        message = message + "\n"
        self._logger.debug("Send %r to %s", message, participant)
        client.transport.write(message.encode())


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