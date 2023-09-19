from enum import Enum


class Commitment(Enum):
    ROSTERED = "rostered"
    SUB = "sub"

class Transport(Enum):
    BUS = "bus"
    SELF = "self"
    INVALID = "invalid"

class Attendance(Enum):
    AWAIT = "await"
    YES = "yes"
    NO = "no"
    INVALID = "invalid"

class Date(Enum):
    SEPTEMBER20 = "September 20"
    SEPTEMBER27 = "September 27"
    OCTOBER4 = "October 4"
    OCTOBER25 = "October 25"
    NOVEMBER1 = "November 1"
    NOVEMBER8 = "November 8"
    NOVEMBER15 = "November 15"
    NOVEMBER29 = "November 29"
    DECEMBER6 = "December 6"