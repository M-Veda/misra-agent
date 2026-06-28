from config.settings import RULE_ENGINE_CONFIG
from models.violation import Violation
from rules.base_rule import BaseRule
from rules.config import RuleEngineConfig
from rules.discovery import discover_rule_classes
from rules.registry import RuleRegistry


class RuleEngine:
    """Plugin-based MISRA C:2012 Rule Engine."""

    def __init__(self, config=None, packages=None, registry=None):
        self.config = self._build_config(config)
        self.packages = tuple(packages or ("rules",))
        self.registry = registry or RuleRegistry()
        self.load_rules()

    def load_rules(self):
        self.registry.clear()
        for package_name in self.packages:
            self._discover_package(package_name)
        return self.get_rule_classes(include_disabled=True)

    def get_rules(self, include_disabled=False):
        return [rule_class.metadata() for rule_class in self.get_rule_classes(include_disabled=include_disabled)]

    def get_rule_classes(self, include_disabled=False):
        classes = self.registry.all()
        if not include_disabled:
            classes = [rule_class for rule_class in classes if self.config.allows(rule_class.metadata())]
        return sorted(classes, key=self._sort_key)

    def get_rule(self, rule_id):
        rule_class = self.registry.get(rule_id)
        if rule_class is None:
            return None
        return rule_class.metadata()

    def rules_by_chapter(self, include_disabled=False):
        grouped = {}
        for rule_class in self.get_rule_classes(include_disabled=include_disabled):
            metadata = rule_class.metadata()
            grouped.setdefault(metadata.chapter, []).append(metadata)
        return grouped

    def enabled_rules(self):
        return len(self.get_rule_classes())

    def registered_rules(self):
        return len(self.registry)

    def execute(self, code, file_path, rule_ids=None, analysis_context=None):
        selected_rule_ids = {str(rule_id) for rule_id in rule_ids} if rule_ids else None
        violations = []

        for rule_class in self.get_rule_classes():
            metadata = rule_class.metadata()
            if selected_rule_ids is not None and metadata.rule_id not in selected_rule_ids:
                continue

            rule = rule_class()
            result = None
            try:
                if hasattr(rule, "check_with_context"):
                    result = rule.check_with_context(code=code, file_path=file_path, analysis_context=analysis_context)
                else:
                    result = rule.check(code=code, file_path=file_path)
            except TypeError:
                result = rule.check(code=code, file_path=file_path)
            if result is None:
                continue

            if isinstance(result, list):
                rule_violations = result
            else:
                rule_violations = [result]

            for violation in rule_violations:
                if not isinstance(violation, Violation):
                    raise TypeError(f"Rule {metadata.rule_id} returned {type(violation).__name__}, expected Violation.")
                if violation.rule_id != metadata.rule_id:
                    raise ValueError(f"Rule {metadata.rule_id} returned violation for rule {violation.rule_id}.")
                violations.append(violation)

        return violations

    def _discover_package(self, package_name):
        for rule_class in discover_rule_classes((package_name,)):
            self.registry.register(rule_class)

    @staticmethod
    def _build_config(config):
        if isinstance(config, RuleEngineConfig):
            return config
        if config is None:
            config = RULE_ENGINE_CONFIG
        return RuleEngineConfig.from_mapping(config)

    @staticmethod
    def _sort_key(rule_class):
        metadata = rule_class.metadata()
        return (metadata.priority, RuleEngine._rule_id_key(metadata.rule_id))

    @staticmethod
    def _rule_id_key(rule_id):
        key = []
        for part in rule_id.split("."):
            try:
                key.append(int(part))
            except ValueError:
                key.append(part)
        return tuple(key)