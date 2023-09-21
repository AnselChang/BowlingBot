from enum import Enum


class Commitment(Enum):
    ROSTERED = "rostered"
    SUB = "sub"

class Transport(Enum):
    BUS = "bus"
    SELF = "self"
    INVALID = "invalid"