from enum import Enum


class ServiceCode(str, Enum):
    DASHBOARD = "DASHBOARD"
    VOTERS = "VOTERS"
    DEVELOPMENT = "DEVELOPMENT"
    COMPLAINTS = "COMPLAINTS"
    MEETINGS = "MEETINGS"
    VOLUNTEERS = "VOLUNTEERS"
    NEWS = "NEWS"
    BOOTH_DETAILS = "BOOTH_DETAILS"
    MLALAD_FUND = "MLALAD_FUND"
    JAN_SABHA = "JAN_SABHA"


class Action(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"