class RuleExecutor:

    def execute(

        self,

        rules,

        code

    ):

        violations = []

        for rule in rules:

            result = rule.check(code)

            violations.extend(result)

        return violations