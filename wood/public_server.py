# -*- coding: utf-8 -*-

import asyncio
import logging


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


class PublicServerProtocol(asyncio.Protocol):
    def __init__(self, public_clients):
        self.public_clients = public_clients

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        logging.debug("Connection made %s", self.peername)
        self.public_clients.add(self)

    def connection_lost(self, exc):
        logging.debug("Connection lost %s", self.peername)
        self.public_clients.remove(self)

