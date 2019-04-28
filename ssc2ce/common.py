from enum import IntEnum


class AuthType(IntEnum):
    NONE = 0
    PASSWORD = 1
    CREDENTIALS = 2
    SIGNATURE = 3
