from rules.rule_engine import RuleEngine


class RuleLoaderService:
    def __init__(self, config=None):
        self.engine = RuleEngine(config=config)

    def load(self):
        self.engine.load_rules()
        return self.engine.get_rules(include_disabled=True)