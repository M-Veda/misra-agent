from collections import OrderedDict, defaultdict

from rules.base_rule import BaseRule


class RuleRegistry:
    """Stores discovered rule plugin classes and exposes metadata indexes."""

    def __init__(self):
        self._rules = OrderedDict()

    def clear(self):
        self._rules.clear()

    def register(self, rule_class):
        if not isinstance(rule_class, type) or not issubclass(rule_class, BaseRule):
            raise TypeError("Only BaseRule subclasses can be registered.")
        metadata = rule_class.metadata()
        existing = self._rules.get(metadata.rule_id)
        if existing is not None and existing is not rule_class:
            raise ValueError(f"Duplicate rule id registered: {metadata.rule_id}")
        self._rules[metadata.rule_id] = rule_class
        return rule_class

    def all(self):
        return list(self._rules.values())

    def get(self, rule_id):
        return self._rules.get(rule_id)

    def metadata(self):
        return [rule_class.metadata() for rule_class in self._rules.values()]

    def by_chapter(self):
        grouped = defaultdict(list)
        for rule_class in self._rules.values():
            metadata = rule_class.metadata()
            grouped[metadata.chapter].append(rule_class)
        return dict(grouped)

    def __len__(self):
        return len(self._rules)


RULE_REGISTRY = RuleRegistry()
