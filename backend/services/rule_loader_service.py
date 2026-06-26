from rules.rule_engine import RuleEngine


class RuleLoaderService:

    def __init__(self):

        self.engine = RuleEngine()

    def load(self):

        self.engine.load_rules()

        return self.engine.get_rules()