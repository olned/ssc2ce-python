#!/usr/bin/env python

from distutils.core import setup
from deribit.VERSION import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='ons-deribit',
      version=__version__,
      description='Simple Deribit API v2 on Websocket',
      author='Oleg Nedbaylo',
      author_email='olned64@gmail.com',
      url='https://github.com/olned/ons-deribit-ws-python',
      packages=['deribit'],
      install_requires=['aiohttp', ],
      classifiers=[
              "Programming Language :: Python :: 3.6",
              "License :: OSI Approved :: MIT License",
              "Operating System :: OS Independent",
          ],
      )
