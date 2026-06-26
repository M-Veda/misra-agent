from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class Rule:
    """
    Represents a MISRA rule definition.
    """

    rule_id: str
    title: str
    category: str
    severity: str
    description: str

    auto_fixable: bool = False

    enabled: bool = True

    fix_strategy: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)