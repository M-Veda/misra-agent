from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Patch:
    """Represents one source-code modification."""

    patch_id: str
    violation_id: str
    rule_id: str
    file_path: str
    line_number: int
    original_code: str
    replacement_code: str
    description: str
    strategy: str
    confidence: float = 1.0
    applied: bool = False
    created_at: datetime = field(default_factory=utc_now)
