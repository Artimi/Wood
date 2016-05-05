# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name="wood_server",
    version="1.0.0",
    description="Wood stock server",
    author="Petr Šebek",
    author_email="petrsebek1@gmail.com",
    tests_require=[
        "pytest",
        "pytest-cov",
    ],
    packages=find_packages(),
)