# -*- coding: utf-8 -*-

import json
import asyncio
import logging


class Clients:
    def __init__(self):
        self._clients = {}

    def add(self, client):
        self._clients[client.peername] = client

    def remove(self, client):
        del self._clients[client.peername]

    def broadcast(self, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        for participant, client in self._clients.items():
            logging.debug("Broadcast %r to %s", message, participant)
            client.transport.write(message.encode())

    def send(self, participant, message):
        """
        Send message to participant. May raise `KeyError` if participant already left.
        """
        client = self._clients[participant]
        if isinstance(message, dict):
            message = json.dumps(message)
        logging.debug("Send %r to %s", message, participant)
        client.transport.write(message.encode())


class PublicServerProtocol(asyncio.Protocol):
    def __init__(self, clients):
        self._clients = clients

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        logging.debug("Connection made %s", self.peername)
        self._clients.add(self)

    def connection_lost(self, exc):
        logging.debug("Connection lost %s", self.peername)
        self._clients.remove(self)


class PrivateServerProtocol(PublicServerProtocol):
    def __init__(self, clients, stock_exchange):
        super().__init__(clients)
        self._stock_exchange = stock_exchange

    def data_received(self, data):
        message = data.decode()
        logging.debug("Received %r from %r" % (message, self.peername))
        self._stock_exchange.handle_order(message, self.peername)

