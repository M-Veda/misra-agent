import re

from utils.violation_factory import create_violation


class RuleUtils:

    @staticmethod
    def regex_rule(
        rule,
        code,
        file_path,
        pattern,
        explanation=""
    ):

        violations = []

        for match in re.finditer(pattern, code, re.MULTILINE):

            line = code.count("\n", 0, match.start()) + 1

            violations.append(

                create_violation(

                    rule=rule,

                    file_path=file_path,

                    line=line,

                    original=match.group(),

                    explanation=explanation

                )

            )

        return violations
