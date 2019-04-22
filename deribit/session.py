import asyncio
import logging

import aiohttp

logger = logging.getLogger(__name__)


class SessionWrapper:
    __internal_session: bool = True
    __is_session: bool = False
    __session: aiohttp.ClientSession = None
    _timeout: aiohttp.ClientTimeout = None

    def __init__(self, timeout: aiohttp.ClientTimeout = None, session: aiohttp.ClientSession = None):
        if session:
            self._session = session
            self.__internal_session = False

        if timeout:
            self._timeout = timeout
        else:
            self._timeout = aiohttp.ClientTimeout(total=20)

    @property
    def _session(self):
        if not self.__is_session:
            self.__check_session()
        return self.__session

    @_session.setter
    def _session(self, value):
        self.__is_session = True
        self.__internal_session = False
        self.__session = value

    def __check_session(self):
        if not self.__is_session:
            self.__is_session = True
            self.__internal_session = True
            self.__session = aiohttp.ClientSession(timeout=self._timeout)

    def __del__(self):
        self._close()

    def __enter__(self):
        self.__check_session()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._close()

    def _close(self):
        if self.__internal_session and self.__session:
            asyncio.ensure_future(self.__session.close())
            self.__is_session = False
