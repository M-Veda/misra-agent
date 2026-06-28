from rules.rule_engine import RuleEngine
from utils.serialization import _json_value


class RuleService:
    def __init__(self, config=None):
        self.engine = RuleEngine(config=config)

    def get_rules(self, include_disabled=False):
        return [_json_value(rule) for rule in self.engine.get_rules(include_disabled=include_disabled)]

    def get_rules_by_chapter(self, include_disabled=False):
        return {
            chapter: [_json_value(rule) for rule in rules]
            for chapter, rules in self.engine.rules_by_chapter(include_disabled=include_disabled).items()
        }