from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def utc_now():
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Violation:
    """
    Represents one MISRA C:2012 violation.

    This object flows through the complete pipeline:

        Rule Engine
            ↓
        Interactive Review
            ↓
        Patch Engine
            ↓
        Validation
            ↓
        Compliance Report
    """

    # ------------------------------------------------------------------
    # Core Rule Information
    # ------------------------------------------------------------------

    violation_id: str

    rule_id: str

    title: str

    description: str

    severity: str

    category: str

    # ------------------------------------------------------------------
    # Source Location
    # ------------------------------------------------------------------

    file_path: str

    line_number: int

    column_number: int = 0

    # ------------------------------------------------------------------
    # Source Code
    # ------------------------------------------------------------------

    original_code: str = ""

    suggested_code: str = ""

    explanation: str = ""

    # ------------------------------------------------------------------
    # Review State
    # ------------------------------------------------------------------

    auto_fixable: bool = False

    approved: Optional[bool] = None

    applied: bool = False

    confidence: float = 1.0

    fix_strategy: str = ""

    patch_id: str = ""

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    tags: list[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=utc_now)

    autofix: Optional[Any] = None

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    @property
    def location(self) -> str:
        """
        Returns source location.

        Example:
            sample.c:24:5
        """

        return (
            f"{self.file_path}:"
            f"{self.line_number}:"
            f"{self.column_number}"
        )

    @property
    def is_confirmed(self) -> bool:
        """
        True once reviewer accepts the violation.
        """

        return self.approved is True

    @property
    def is_rejected(self) -> bool:
        """
        True once reviewer rejects the violation.
        """

        return self.approved is False

    @property
    def has_patch(self) -> bool:
        """
        Returns True if a patch exists.
        """

        return bool(self.patch_id)

    @property
    def review_status(self) -> str:

        if self.approved is True:
            return "accepted"

        if self.approved is False:
            return "rejected"

        return "pending"

    def to_dict(self):
        """
        Serialize violation for API/UI.
        """

        return {
            "violation_id": self.violation_id,
            "rule_id": self.rule_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "category": self.category,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "location": self.location,
            "original_code": self.original_code,
            "suggested_code": self.suggested_code,
            "explanation": self.explanation,
            "auto_fixable": self.auto_fixable,
            "approved": self.approved,
            "applied": self.applied,
            "confidence": self.confidence,
            "fix_strategy": self.fix_strategy,
            "patch_id": self.patch_id,
            "review_status": self.review_status,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
        }

    def __str__(self):

        return (
            f"[{self.rule_id}] "
            f"{self.title} "
            f"({self.location})"
        )