from enum import IntEnum


class ConfigFlag(IntEnum):
    """
        DEC_AS_STR - 8 - enable all decimals as strings
        TIME_S - 32 - Enable all timestamps as strings
        TIMESTAMP - 32768 - Adds a Timestamp in milliseconds to each received event.
        SEQ_ALL - 65536 - Adds sequence numbers to each event.
        OB_CHECKSUM - 131072 - Enable checksum for every book iteration.

        Oleg Nedbaylo: It seems that some flags does not work. I have not seen influence of DEC_AS_STR and TIME_S.
                      Maybe I have been doing something wrong, I don’t know ...

    """
    NONE = 0,
    DEC_AS_STR = 8
    TIME_S = 32
    TIMESTAMP = 32768
    SEQ_ALL = 65536
    OB_CHECKSUM = 131072


class StatusFlag(IntEnum):
    MAINTENANCE = 0
    OPERATIVE = 1