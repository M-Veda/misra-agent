from dataclasses import dataclass, field


@dataclass(slots=True)
class FixReport:

    applied: list[str] = field(default_factory=list)

    skipped: list[str] = field(default_factory=list)

    failed: list[str] = field(default_factory=list)