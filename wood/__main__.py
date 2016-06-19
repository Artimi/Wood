# -*- coding: utf-8 -*-

import argparse

from .server import StockServer
from .random_client import start_clients


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    server_group = parser.add_argument_group("server")
    server_group.add_argument("-s", "--server", default=False, action="store_true", help="Run server.")
    server_group.add_argument("-m", "--multiple-servers", default=False, action="store_true", help="Run multiple server environment (needs redis).")
    server_group.add_argument("--private", default=7001, type=int, help="Private port.")
    server_group.add_argument("--public", default=7002, type=int, help="Public port.")
    server_group.add_argument("--persist", default=False, action="store_true", help="Whether to persist limit order book. Only for multiple server environment.")

    client_group = parser.add_argument_group("client")
    client_group.add_argument("-c", "--client", default=False, action="store_true", help="Run random client.")
    client_group.add_argument("-n", "--number-of-clients", type=int, default=1, help="Number of connected clients.")
    client_group.add_argument("-p", "--port", type=int, default=7001, help="Private port of the server.")
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
