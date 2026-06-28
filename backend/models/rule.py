from dataclasses import dataclass, field
from typing import Any, Dict, Tuple


@dataclass(frozen=True, slots=True)
class Rule:
    """Static metadata for one MISRA C:2012 rule plugin."""

    rule_id: str
    title: str
    chapter: str
    category: str
    severity: str
    description: str
    rationale: str = ""
    fixable: bool = False
    auto_fixable: bool = False
    references: Tuple[str, ...] = ()
    priority: int = 100
    enabled_by_default: bool = True
    fix_strategy: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "references", tuple(self.references))
        if self.fixable and not self.auto_fixable:
            object.__setattr__(self, "auto_fixable", True)