from enum import IntEnum, unique


@unique
class IotErr(IntEnum):
    CONFIRMED = 0
    UNCONFIRMED = 1
    FAILED = 2
    EXISTING = 3
    DEVICE_FENCED = 4
    WEATHER_FENCED = 5


@unique
class StateMachineErr(IntEnum):
    SUCCESS = 0
    FAIL = 1
    ALARM = 2
