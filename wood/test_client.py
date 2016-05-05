# -*- coding: utf-8 -*-

import asyncio
import sys


@asyncio.coroutine
def public_tcp_echo_client(loop, port):
    reader, writer = yield from asyncio.open_connection('127.0.0.1', port, loop=loop)
    data = True
    while data:
        data = yield from reader.read(100)
        print("Received: %r" % data.decode())


@asyncio.coroutine
def tcp_echo_client(message, loop, port):
    reader, writer = yield from asyncio.open_connection('127.0.0.1', port, loop=loop)

    print("Send: %r" % message)
    writer.write(message.encode())

    data = yield from reader.read(100)
    print("Received: %r" % data.decode())

    print("Close the socket")
    writer.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int)
    parser.add_argument("--public", action='store_true')
    parser.add_argument("-m", "--message", default="Hello World!")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    try:
        if args.public:
            loop.run_until_complete(public_tcp_echo_client(loop, args.port))
        else:
            loop.run_until_complete(tcp_echo_client(args.message, loop, args.port))
    except KeyboardInterrupt:
        pass
    loop.close()
