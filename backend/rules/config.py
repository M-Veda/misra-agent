from dataclasses import dataclass, field
from typing import Optional, Set


def _normalize(values):
    if values is None:
        return None
    normalized = {str(value).strip() for value in values if str(value).strip()}
    return normalized or None


def _normalize_required(values):
    normalized = _normalize(values)
    return normalized or set()


@dataclass(frozen=True, slots=True)
class RuleEngineConfig:
    enabled_rules: Optional[Set[str]] = None
    disabled_rules: Set[str] = field(default_factory=set)
    enabled_chapters: Optional[Set[str]] = None
    disabled_chapters: Set[str] = field(default_factory=set)
    enabled_categories: Optional[Set[str]] = None
    disabled_categories: Set[str] = field(default_factory=set)
    minimum_priority: Optional[int] = None

    def __post_init__(self):
        object.__setattr__(self, "enabled_rules", _normalize(self.enabled_rules))
        object.__setattr__(self, "disabled_rules", _normalize_required(self.disabled_rules))
        object.__setattr__(self, "enabled_chapters", _normalize(self.enabled_chapters))
        object.__setattr__(self, "disabled_chapters", _normalize_required(self.disabled_chapters))
        object.__setattr__(self, "enabled_categories", _normalize(self.enabled_categories))
        object.__setattr__(self, "disabled_categories", _normalize_required(self.disabled_categories))

    @classmethod
    def from_mapping(cls, data):
        data = data or {}
        return cls(
            enabled_rules=set(data.get("enabled_rules") or []) or None,
            disabled_rules=set(data.get("disabled_rules") or []),
            enabled_chapters=set(data.get("enabled_chapters") or []) or None,
            disabled_chapters=set(data.get("disabled_chapters") or []),
            enabled_categories=set(data.get("enabled_categories") or []) or None,
            disabled_categories=set(data.get("disabled_categories") or []),
            minimum_priority=data.get("minimum_priority"),
        )

    def allows(self, rule_metadata):
        if not rule_metadata.enabled_by_default:
            return False
        if self.enabled_rules is not None and rule_metadata.rule_id not in self.enabled_rules:
            return False
        if rule_metadata.rule_id in self.disabled_rules:
            return False
        if self.enabled_chapters is not None and rule_metadata.chapter not in self.enabled_chapters:
            return False
        if rule_metadata.chapter in self.disabled_chapters:
            return False
        if self.enabled_categories is not None and rule_metadata.category not in self.enabled_categories:
            return False
        if rule_metadata.category in self.disabled_categories:
            return False
        if self.minimum_priority is not None and rule_metadata.priority < self.minimum_priority:
            return False
        return True