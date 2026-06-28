from dataclasses import dataclass, field
from typing import Any, Dict, Tuple


def _normalize_capabilities(values):
    if values is None:
        return ("text",)
    if isinstance(values, str):
        values = (values,)

    normalized = []
    for value in values:
        if not isinstance(value, str):
            raise TypeError("Rule capabilities must be strings.")
        capability = value.strip().lower()
        if capability not in {"text", "ast", "hybrid"}:
            raise ValueError(f"Unsupported rule capability: {value}")
        if capability == "hybrid":
            if "text" not in normalized:
                normalized.append("text")
            if "ast" not in normalized:
                normalized.append("ast")
            continue
        if capability not in normalized:
            normalized.append(capability)

    return tuple(normalized or ("text",))


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
    capabilities: Tuple[str, ...] = ("text",)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "references", tuple(self.references))
        object.__setattr__(self, "capabilities", _normalize_capabilities(self.capabilities))
        if self.fixable and not self.auto_fixable:
            object.__setattr__(self, "auto_fixable", True)