from enum import Enum


class SessionState(Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    REVIEWING = "reviewing"
    BUILDING = "building"
    VALIDATING = "validating"
    FINISHED = "finished"
