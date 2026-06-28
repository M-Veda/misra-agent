class RuleExecutor:
    def execute(self, rules, code, file_path="<memory>"):
        violations = []
        for rule in rules:
            result = rule.check(code=code, file_path=file_path)
            if result is None:
                continue
            if isinstance(result, list):
                violations.extend(result)
            else:
                violations.append(result)
        return violations