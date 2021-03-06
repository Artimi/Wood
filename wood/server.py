# -*- coding: utf-8 -*-

import asyncio

from functools import partial
from .stock_exchange import StockExchange
from .utils import get_logger
from .clients import PrivateClients, PublicClients
from .pubsub import asyncio_queue_pubsub_factory, redis_pubsub_factory


class StockServer:
    """
    Public and private server that handles client orders. Main class of this
    program that uses all other parts. You can run it in `multiple_servers`
    mode that uses redis publisher, subscriber and priority queue. Without
    `multiple_servers` in memory solution is used.
    """
    def __init__(self, private_port=7001, public_port=7002, loop=None, multiple_servers=False, persist=False):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.mutliple_servers = multiple_servers
        if self.mutliple_servers:
            self.public_subscriber, self.public_publisher = redis_pubsub_factory(self.loop)
            self.private_subscriber, self.private_publisher = redis_pubsub_factory(self.loop)
        else:
            self.public_subscriber, self.public_publisher = asyncio_queue_pubsub_factory(self.loop)
            self.private_subscriber, self.private_publisher = asyncio_queue_pubsub_factory(self.loop)
        self.public_clients = PublicClients(self.public_subscriber)
        self.private_clients = PrivateClients(self.private_subscriber)
        self.public_port = public_port
        self.private_port = private_port
        self.stock_exchange = StockExchange(self.private_publisher, self.public_publisher, self.loop, multiple_servers)
        self._logger = get_logger()
        self._persist = persist

    def initialize_tasks(self):
        """
        Initialize all tasks that should be done (servers, consumers for client communication).
        Connect to redis potentially.
         """
        public_protocol = partial(PublicServerProtocol, self.public_clients, self.loop)
        private_protocol = partial(PrivateServerProtocol, self.private_clients, self.stock_exchange, self.loop)
        public_server_coro = self.loop.create_server(public_protocol, port=self.public_port)
        private_server_coro = self.loop.create_server(private_protocol, port=self.private_port)
        self.public_server = self.loop.run_until_complete(public_server_coro)
        self.private_server = self.loop.run_until_complete(private_server_coro)
        self.loop.run_until_complete(self.public_subscriber.connect())
        self.loop.run_until_complete(self.public_publisher.connect())
        self.loop.run_until_complete(self.private_subscriber.connect())
        self.loop.run_until_complete(self.private_publisher.connect())
        self.public_clients_consume = self.loop.create_task(self.public_clients.consume())
        self.private_clients_consume = self.loop.create_task(self.private_clients.consume())

        self._logger.info("Serving public on %s.", self.public_server.sockets[0].getsockname())
        self._logger.info("Serving private on %s.", self.private_server.sockets[0].getsockname())

    def shutdown_tasks(self):
        """Clean up all running tasks, shutdown server."""
        self.public_server.close()
        self.private_server.close()

        if self.mutliple_servers and not self._persist:
            self.loop.run_until_complete(self.public_publisher._redis.flushdb())
        self.public_subscriber.close()
        self.public_publisher.close()
        self.private_subscriber.close()
        self.private_publisher.close()
        self.public_clients_consume.cancel()
        self.private_clients_consume.cancel()
        self.stock_exchange.close()
        self.loop.run_until_complete(self.public_server.wait_closed())
        self.loop.run_until_complete(self.private_server.wait_closed())
        self.loop.close()
        self._logger.info("Server shutdown.")

    def run(self):
        """Run server and serve requests until `KeyboardInterrupt` is raised."""
        self.initialize_tasks()
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown_tasks()


class PublicServerProtocol(asyncio.Protocol):
    """
    Protocol that handles incoming and outcoming clients so app can send messages
    to them later.
    """
    def __init__(self, clients: PublicClients, loop):
        self._clients = clients
        self._logger = get_logger()
        self._loop = loop

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        self._logger.debug("Connection made %s", self.peername)
        self._clients.add(self)

    def connection_lost(self, exc):
        self._logger.debug("Connection lost %s", self.peername)
        self._clients.remove(self)


class PrivateServerProtocol(PublicServerProtocol):
    """
    Protocal for private server that differs only in that it handles incoming
    requests too.
    """
    def __init__(self, clients: PrivateClients, stock_exchange: StockExchange, loop):
        super().__init__(clients, loop)
        self._stock_exchange = stock_exchange

    def data_received(self, data):
        message = data.decode()
        self._logger.debug("Received %r from %r" % (message, self.peername))
        asyncio.ensure_future(self._stock_exchange.handle_order(message, self.peername), loop=self._loop)
