from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from models.review_action import ReviewAction


def utc_now():
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Decision:
    """
    Represents a user's review decision for a single MISRA violation.
    """

    violation_id: str

    action: ReviewAction

    patch_id: str = ""

    edited_code: str = ""

    comment: str = ""

    reviewed_at: datetime = field(default_factory=utc_now)

    def __post_init__(self):
        if not isinstance(self.action, ReviewAction):
            self.action = ReviewAction(self.action)

        self.edited_code = self.edited_code.rstrip()
        self.comment = self.comment.strip()

    @property
    def approved(self):
        """
        Returns True when the decision approves
        the suggested fix.
        """

        return self.action in (
            ReviewAction.ACCEPT,
            ReviewAction.EDIT,
        )

    @property
    def rejected(self):
        return self.action == ReviewAction.REJECT

    @property
    def skipped(self):
        return self.action == ReviewAction.SKIP

    @property
    def requires_patch(self):
        """
        ACCEPT and EDIT decisions create patches.
        """

        return self.action in (
            ReviewAction.ACCEPT,
            ReviewAction.EDIT,
        )

    @property
    def action_name(self):
        return self.action.value

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize decision for reports,
        APIs and UI.
        """

        return {
            "violation_id": self.violation_id,
            "action": self.action.value,
            "approved": self.approved,
            "rejected": self.rejected,
            "skipped": self.skipped,
            "requires_patch": self.requires_patch,
            "patch_id": self.patch_id,
            "edited_code": self.edited_code,
            "comment": self.comment,
            "reviewed_at": self.reviewed_at.isoformat(),
        }

    def __str__(self):
        return (
            f"{self.violation_id} : "
            f"{self.action.value}"
        )