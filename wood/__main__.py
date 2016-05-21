# -*- coding: utf-8 -*-

import argparse

from .server import StockServer
from .random_client import start_clients


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", default=False, action="store_true")
    parser.add_argument("-c", "--client", default=False, action="store_true")
    parser.add_argument("-n", "--number-of-clients", type=int, default=1)
    args = parser.parse_args()

    if args.server:
        stock_server = StockServer()
        stock_server.run()
    elif args.client:
        start_clients(args.number_of_clients)
