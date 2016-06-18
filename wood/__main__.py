# -*- coding: utf-8 -*-

import argparse

from .server import StockServer
from .random_client import start_clients


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    server_group = parser.add_argument_group("server")
    server_group.add_argument("-s", "--server", default=False, action="store_true")
    server_group.add_argument("-m", "--multiple-servers", default=False, action="store_true")
    server_group.add_argument("--private", default=7001, type=int)
    server_group.add_argument("--public", default=7002, type=int)
    server_group.add_argument("--persist", default=False, action="store_true")

    client_group = parser.add_argument_group("client")
    client_group.add_argument("-c", "--client", default=False, action="store_true")
    client_group.add_argument("-n", "--number-of-clients", type=int, default=1)
    client_group.add_argument("-p", "--port", type=int, default=7001)
    args = parser.parse_args()

    if args.server:
        stock_server = StockServer(private_port=args.private,
                                   public_port=args.public,
                                   multiple_servers=args.multiple_servers,
                                   persist=args.persist)
        stock_server.run()
    elif args.client:
        start_clients(args.number_of_clients,
                      port=args.port)
