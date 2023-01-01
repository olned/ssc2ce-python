#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ssc2ce',
    version="0.14.4",
    author='Oleg Nedbaylo',
    author_email='olned64@gmail.com',
    description='A Set of Simple Connectors for access To Cryptocurrency Exchanges',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/olned/ssc2ce-python',
    packages=setuptools.find_packages(),
    install_requires=['aiohttp', 'sortedcontainers'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
