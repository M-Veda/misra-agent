from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionContext:
    """
    Shared execution state for a single analysis run.
    """

    profile: str = "full"

    enabled_rules: set[str] | None = None

    disabled_rules: set[str] = field(default_factory=set)

    metrics: dict[str, Any] = field(default_factory=dict)

    cache: dict[str, Any] = field(default_factory=dict)

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    def rule_enabled(self, rule_id: str) -> bool:

        if self.enabled_rules is not None:
            return rule_id in self.enabled_rules

        return rule_id not in self.disabled_rules

    def put(self, key, value):

        self.cache[key] = value

    def get(self, key, default=None):

        return self.cache.get(key, default)

    def warning(self, text):

        self.warnings.append(text)

    def error(self, text):

        self.errors.append(text)
