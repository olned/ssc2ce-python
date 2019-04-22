#!/usr/bin/env python

from distutils.core import setup
from deribit.VERSION import __version__

setup(name='tcc-deribit',
      version=__version__,
      description='Simple Deribit API v2 on Websocket',
      author='Oleg Nedbaylo',
      author_email='olned64@gmail.com',
      url='https://github.com/olned/ons-deribit-ws-python',
      packages=['deribit'],
      )
