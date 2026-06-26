from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def utc_now():
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Violation:
    """
    Represents one MISRA-C violation.
    This object is created by the Rule Engine and consumed by review,
    patching, validation, reporting, API, and UI layers.
    """

    violation_id: str
    rule_id: str
    title: str
    description: str
    severity: str
    category: str
    file_path: str
    line_number: int
    column_number: int = 0
    original_code: str = ""
    suggested_code: str = ""
    explanation: str = ""
    auto_fixable: bool = False
    approved: Optional[bool] = None
    applied: bool = False
    confidence: float = 1.0
    fix_strategy: str = ""
    patch_id: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)
