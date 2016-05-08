# -*- coding: utf-8 -*-

from .server import StockServer


def main():
    stock_server = StockServer()
    stock_server.run()

if __name__ == '__main__':
    main()
