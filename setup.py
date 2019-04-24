#!/usr/bin/env python

import setuptools

from deribit.VERSION import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ons-deribit',
    version=__version__,
    author='Oleg Nedbaylo',
    author_email='olned64@gmail.com',
    description='Simple Deribit API v2 on Websocket',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/olned/ons-deribit-ws-python',
    packages=['deribit'],
    install_requires=['aiohttp'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
