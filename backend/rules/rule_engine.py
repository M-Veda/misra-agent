import importlib
import inspect


class RuleEngine:
    """Discovers and executes MISRA rule classes."""

    MODULES = [
        "rules.declarations",
        "rules.expressions",
        "rules.statements",
        "rules.functions",
        "rules.pointers",
        "rules.preprocessing",
        "rules.runtime",
    ]

    def __init__(self):
        self.rule_classes = []
        self.load_rules()

    def load_rules(self):
        self.rule_classes.clear()
        for module_name in self.MODULES:
            module = importlib.import_module(module_name)
            for _, rule_class in inspect.getmembers(module, inspect.isclass):
                if rule_class.__module__ != module.__name__:
                    continue
                if rule_class.__name__ == "RuleGroup":
                    continue
                self.rule_classes.append(rule_class)
        return self.rule_classes

    def get_rules(self):
        return list(self.rule_classes)

    def enabled_rules(self):
        return len(self.rule_classes)

    def execute(self, code, file_path):
        violations = []
        for rule_class in self.rule_classes:
            rule = rule_class()
            result = rule.check(code=code, file_path=file_path)
            if result is None:
                continue
            if isinstance(result, list):
                violations.extend(result)
            else:
                violations.append(result)
        return violations
