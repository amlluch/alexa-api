from enum import IntEnum, unique


@unique
class IotErr(IntEnum):
    CONFIRMED = 0
    UNCONFIRMED = 1
    FAILED = 2
    EXISTING = 3
    FENCED = 4
