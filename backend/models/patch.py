from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now():
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Patch:
    """
    Represents one source-code modification generated during
    the interactive MISRA review workflow.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    patch_id: str

    violation_id: str

    rule_id: str

    # ------------------------------------------------------------------
    # Source Location
    # ------------------------------------------------------------------

    file_path: str

    line_number: int

    # ------------------------------------------------------------------
    # Patch Content
    # ------------------------------------------------------------------

    original_code: str

    replacement_code: str

    description: str

    strategy: str

    # ------------------------------------------------------------------
    # Patch Status
    # ------------------------------------------------------------------

    confidence: float = 1.0

    applied: bool = False

    created_at: datetime = field(default_factory=utc_now)

    status: str = "queued"

    metadata: dict[str, Any] = field(default_factory=dict)

    conflict_reason: str = ""

    applied_at: datetime | None = None

    rolled_back_at: datetime | None = None

    history: list[dict[str, Any]] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Helper Properties
    # ------------------------------------------------------------------

    @property
    def location(self):
        return f"{self.file_path}:{self.line_number}"

    @property
    def is_pending(self):
        return self.status == "queued"

    @property
    def is_applied(self):
        return self.status == "applied"

    @property
    def is_conflicted(self):
        return self.status == "conflicted"

    @property
    def is_rolled_back(self):
        return self.rolled_back_at is not None

    @property
    def can_apply(self):
        return (
            not self.applied
            and self.status == "queued"
        )

    def add_history(self, action, **details):
        """
        Append an event to the patch history.
        """

        self.history.append(
            {
                "timestamp": utc_now().isoformat(),
                "action": action,
                **details,
            }
        )

    def to_dict(self):
        """
        Serialize Patch for reports/API/UI.
        """

        return {
            "patch_id": self.patch_id,
            "violation_id": self.violation_id,
            "rule_id": self.rule_id,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "location": self.location,
            "original_code": self.original_code,
            "replacement_code": self.replacement_code,
            "description": self.description,
            "strategy": self.strategy,
            "confidence": self.confidence,
            "applied": self.applied,
            "status": self.status,
            "conflict_reason": self.conflict_reason,
            "created_at": self.created_at.isoformat(),
            "applied_at": (
                self.applied_at.isoformat()
                if self.applied_at
                else None
            ),
            "rolled_back_at": (
                self.rolled_back_at.isoformat()
                if self.rolled_back_at
                else None
            ),
            "metadata": dict(self.metadata),
            "history": list(self.history),
        }

    def __str__(self):
        return (
            f"[{self.rule_id}] "
            f"{self.status} "
            f"({self.location})"
        )