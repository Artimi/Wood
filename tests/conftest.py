# -*- coding: utf-8 -*-


def pytest_addoption(parser):
    parser.addoption("--redis", action="store_true", help="Use redis for tests")
