from enum import IntEnum


class ConfigFlag(IntEnum):
    DEC_AS_STR = 8
    TIME_S = 32
    TIMESTAMP = 32768
    SEQ_ALL = 65536
    OB_CHECKSUM = 131072


class StatusFlag(IntEnum):
    MAINTENANCE = 0
    OPERATIVE = 1