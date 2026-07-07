from collections import defaultdict

from rules.rule_engine import RuleEngine
from utils.serialization import _json_value


class RuleService:
    """
    High-level service for accessing MISRA rule metadata.

    Responsibilities
    ----------------
    - Expose all rules
    - Group rules by chapter
    - Query rules by severity/category
    - Provide dashboard statistics
    """

    def __init__(self, config=None):
        self.engine = RuleEngine(config=config)

    def get_rules(self, include_disabled=False):
        rules = self.engine.get_rules(
            include_disabled=include_disabled
        )

        return [
            _json_value(rule)
            for rule in rules
        ]

    def get_rules_by_chapter(
        self,
        include_disabled=False,
    ):
        grouped = self.engine.rules_by_chapter(
            include_disabled=include_disabled
        )

        return {
            chapter: [
                _json_value(rule)
                for rule in rules
            ]
            for chapter, rules in grouped.items()
        }

    def get_rule_statistics(
        self,
        include_disabled=False,
    ):
        rules = self.engine.get_rules(
            include_disabled=include_disabled
        )

        stats = {
            "total_rules": 0,
            "enabled_rules": 0,
            "disabled_rules": 0,
            "chapters": defaultdict(int),
            "categories": defaultdict(int),
            "severities": defaultdict(int),
        }

        for rule in rules:
            stats["total_rules"] += 1

            if getattr(rule, "enabled", True):
                stats["enabled_rules"] += 1
            else:
                stats["disabled_rules"] += 1

            chapter = getattr(rule, "chapter", "Unknown")
            category = getattr(rule, "category", "Unknown")
            severity = getattr(rule, "severity", "Unknown")

            stats["chapters"][chapter] += 1
            stats["categories"][category] += 1
            stats["severities"][severity] += 1

        stats["chapters"] = dict(stats["chapters"])
        stats["categories"] = dict(stats["categories"])
        stats["severities"] = dict(stats["severities"])

        return stats

    def get_rule(self, rule_id):
        rules = self.engine.get_rules(
            include_disabled=True
        )

        for rule in rules:
            if getattr(rule, "rule_id", None) == rule_id:
                return _json_value(rule)

        return None

    def search(
        self,
        keyword,
        include_disabled=True,
    ):
        keyword = keyword.lower()

        results = []

        for rule in self.engine.get_rules(
            include_disabled=include_disabled
        ):
            values = [
                getattr(rule, "rule_id", ""),
                getattr(rule, "title", ""),
                getattr(rule, "description", ""),
                getattr(rule, "category", ""),
                getattr(rule, "chapter", ""),
            ]

            text = " ".join(
                str(v)
                for v in values
            ).lower()

            if keyword in text:
                results.append(
                    _json_value(rule)
                )

        return results