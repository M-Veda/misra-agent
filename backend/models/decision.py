from dataclasses import dataclass, field
from datetime import datetime, timezone

from models.review_action import ReviewAction


def utc_now():
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Decision:
    """User decision for a single violation in the review queue."""

    violation_id: str
    action: ReviewAction
    patch_id: str = ""
    edited_code: str = ""
    comment: str = ""
    reviewed_at: datetime = field(default_factory=utc_now)

    def __post_init__(self):
        if not isinstance(self.action, ReviewAction):
            self.action = ReviewAction(self.action)

    @property
    def approved(self):
        return self.action in (ReviewAction.ACCEPT, ReviewAction.EDIT)
