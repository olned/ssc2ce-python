#!/usr/bin/env python

import setuptools

from ssc2ce.VERSION import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ssc2ce',
    version=__version__,
    author='Oleg Nedbaylo',
    author_email='olned64@gmail.com',
    description='A Set of Simple Connectors for access To Cryptocurrency Exchanges',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/olned/ssc2ce-python',
    packages=setuptools.find_packages(),
    install_requires=['aiohttp'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
