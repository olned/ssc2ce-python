class ConfigFlag:
    """
        DEC_AS_STR - 8 - enable all decimals as strings
        TIME_S - 32 - Enable all timestamps as strings
        TIMESTAMP - 32768 - Adds a Timestamp in milliseconds to each received event.
        SEQ_ALL - 65536 - Adds sequence numbers to each event.
        OB_CHECKSUM - 131072 - Enable checksum for every book iteration.

        Oleg Nedbaylo: It seems that some flags does not work. I have not seen influence of DEC_AS_STR and TIME_S.
                      Maybe I have been doing something wrong, I don’t know ...

    """
    DEC_AS_STR: int = 8
    TIME_S: int = 32
    TIMESTAMP: int = 32768
    SEQ_ALL: int = 65536
    OB_CHECKSUM: int = 131072
