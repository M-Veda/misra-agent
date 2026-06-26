from enum import Enum


class ReviewAction(Enum):

    ACCEPT = "accept"

    REJECT = "reject"

    EDIT = "edit"

    SKIP = "skip"