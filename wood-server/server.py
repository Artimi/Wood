# -*- coding: utf-8 -*-

import asyncio
import logging
LOGGING_PROPERTIES = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # "filename": config.LOG_DELETER,
    "level": logging.DEBUG,
}
logging.basicConfig(**LOGGING_PROPERTIES)

LOCALHOST = '127.0.0.1'


class PublicClients:
    def __init__(self):
        self.clients = []

    def add(self, client):
        self.clients.append(client)

    def remove(self, client):
        self.clients.remove(client)

    def broadcast(self, message):
        for client in self.clients:
            logging.debug("Broadcast %r to %s", message, client.peername)
            client.transport.write(message.encode())

public_clients = PublicClients()


class PublicServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        logging.debug("Connection made %s", self.peername)
        public_clients.add(self)

    def connection_lost(self, exc):
        logging.debug("Connection lost %s", self.peername)
        public_clients.remove(self)


@asyncio.coroutine
async def handle_command(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info("peername")
    logging.debug("Received %r from %r" % (message, addr))

    logging.debug("Send: %r" % message)
    writer.write(data)
    await writer.drain()

    public_clients.broadcast(message)

    logging.debug("Close the client socket")
    writer.close()


def main(port_private=7001, port_public=7002):
    loop = asyncio.get_event_loop()
    public_server_coro = loop.create_server(PublicServerProtocol, port=port_public)
    private_server_coro = asyncio.start_server(handle_command, LOCALHOST, port_private, loop=loop)
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

if __name__ == '__main__':
    main()
