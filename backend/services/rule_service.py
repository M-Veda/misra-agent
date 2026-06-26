from rules.rule_engine import RuleEngine


class RuleService:

    def __init__(self):

        self.engine = RuleEngine()

        self.engine.load_rules()

    def get_rules(self):

        return self.engine.get_rules()