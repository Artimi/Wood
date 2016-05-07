# -*- coding: utf-8 -*-

import asyncio
import json
import logging

from functools import partial
from public_server import PublicClients, PublicServerProtocol
from voluptuous import Schema, Invalid, Any

LOGGING_PROPERTIES = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # "filename": config.LOG_DELETER,
    "level": logging.DEBUG,
}
logging.basicConfig(**LOGGING_PROPERTIES)

LOCALHOST = '127.0.0.1'

message_schema = Schema(Any(
    {
        "message": "createOrder",
        "orderId": int,
        "side": Any("BUY", "SELL"),
        "price": int,
        "quantity": int
    },
    {
        "message": "cancelOrder",
        "orderId": int,
    }, required=True))


class StockServer:
    def __init__(self, public_clients, private_port=7001, public_port=7002):
        self.public_clients = public_clients
        self.private_port = private_port
        self.public_port = public_port

    @asyncio.coroutine
    async def handle_request(self, reader, writer):
        while True:
            data = await reader.read(100)
            if not data:
                break
            message = data.decode()
            addr = writer.get_extra_info("peername")
            logging.debug("Received %r from %r" % (message, addr))
            try:
                json_message = json.loads(message)
            except ValueError:
                response = "Message '{}' is not valid json.".format(message)
                await self.respond(writer, response)
                continue
            try:
                message_schema(json_message)
            except Invalid as e:
                response = "Message '{}' is not valid order message because {}.".format(message, e)
                await self.respond(writer, response)
                continue

            response = "OK"
            await self.respond(writer, response)

            self.public_clients.broadcast(response)

        logging.debug("Close the client socket")
        writer.close()

    async def respond(self, writer, response):
        logging.debug("Send: %r" % response)
        writer.write(response.encode())
        await writer.drain()

    def run(self):
        loop = asyncio.get_event_loop()
        public_server_coro = loop.create_server(partial(PublicServerProtocol, self.public_clients), port=self.public_port)
        private_server_coro = asyncio.start_server(self.handle_request, LOCALHOST, self.private_port, loop=loop)
        public_server = loop.run_until_complete(public_server_coro)
        private_server = loop.run_until_complete(private_server_coro)

        logging.info("Serving on {}".format(public_server.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        public_server.close()
        private_server.close()
        loop.run_until_complete(public_server.wait_closed())
        loop.run_until_complete(private_server.wait_closed())
        loop.close()


def main():
    public_clients = PublicClients()
    stock_server = StockServer(public_clients)
    stock_server.run()

if __name__ == '__main__':
    main()
