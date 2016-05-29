# -*- coding: utf-8 -*-

import asyncio
import json

from .utils import get_logger


class Clients:
    def __init__(self, subscriber):
        self._clients = {}
        self._logger = get_logger()
        self.subscriber = subscriber

    def add(self, client):
        self._clients[str(client.peername)] = client

    def remove(self, client):
        del self._clients[str(client.peername)]

    def broadcast(self, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        message += "\n"
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
        message += "\n"
        self._logger.debug("Send %r to %s", message, participant)
        client.transport.write(message.encode())


class PublicClients(Clients):
    @asyncio.coroutine
    async def consume(self):
        self.subscriber.subscribe("public")
        while True:
            channel, message = await self.subscriber.get()
            self.broadcast(message)


class PrivateClients(Clients):
    def add(self, client):
        super().add(client)
        self.subscriber.subscribe(str(client.peername))

    def remove(self, client):
        super().remove(client)
        self.subscriber.unsubscribe(str(client.peername))

    @asyncio.coroutine
    async def consume(self):
        while True:
            participant, message = await self.subscriber.get()
            self.send(participant, message)
