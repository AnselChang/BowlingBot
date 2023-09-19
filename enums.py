from enum import Enum


class Commitment(Enum):
    ROSTERED = "rostered"
    SUB = "sub"

class Transport(Enum):
    BUS = "bus"
    SELF = "self"

class Attendance(Enum):
    AWAIT = "await"
    YES = "yes"
    NO = "no"