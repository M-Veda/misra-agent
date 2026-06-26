import re

from rules.base_rule import BaseRule
from utils.violation_factory import create_violation


class Rule81(BaseRule):
    RULE_ID = "8.1"
    TITLE = "Function shall have prototype"
    CATEGORY = "Declarations"
    SEVERITY = "Required"
    DESCRIPTION = "Detect function declarations or definitions that use an empty parameter list."

    PATTERN = r'^[^\S\n]*[A-Za-z_][\w\s\*]*\s+[A-Za-z_]\w*\s*\(\s*\)\s*$'

    def check(self, code, file_path):
        violations = []

        for match in re.finditer(self.PATTERN, code, re.MULTILINE):
            original = match.group().strip()
            line = code.count("\n", 0, match.start()) + 1
            suggestion = re.sub(r'\(\s*\)', '(void)', original, count=1)

            violations.append(
                create_violation(
                    rule=self,
                    file_path=file_path,
                    line=line,
                    original=original,
                    suggestion=suggestion,
                    explanation="Use an explicit parameter list so the function prototype is fully specified.",
                )
            )

        return violations

    def suggest_fix(self, violation):
        return violation.suggested_code or None


class Rule82(BaseRule):
    RULE_ID = "8.2"
    TITLE = "Reserved"
    CATEGORY = "Declarations"
    SEVERITY = "Required"
    DESCRIPTION = ""

    def check(self, code, file_path):
        return []

    def suggest_fix(self, violation):
        return None


class Rule83(BaseRule):
    RULE_ID = "8.3"
    TITLE = "Reserved"
    CATEGORY = "Declarations"
    SEVERITY = "Required"
    DESCRIPTION = ""

    def check(self, code, file_path):
        return []

    def suggest_fix(self, violation):
        return None


class Rule84(BaseRule):
    RULE_ID = "8.4"
    TITLE = "Compatible declaration shall be visible"
    CATEGORY = "Declarations"
    SEVERITY = "Required"
    DESCRIPTION = ""

    def check(self, code, file_path):
        return []

    def suggest_fix(self, violation):
        return None
