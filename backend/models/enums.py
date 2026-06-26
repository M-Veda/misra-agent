from enum import Enum


class Severity(Enum):

    REQUIRED = "Required"

    MANDATORY = "Mandatory"

    ADVISORY = "Advisory"


class ReviewStatus(Enum):

    PENDING = "Pending"

    ACCEPTED = "Accepted"

    REJECTED = "Rejected"

    APPLIED = "Applied"


class FixType(Enum):

    REGEX = "Regex"

    AST = "AST"

    AI = "AI"