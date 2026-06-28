import re

from rules.base_rule import BaseRule


class Rule81(BaseRule):
    RULE_ID = "8.1"
    TITLE = "Function shall have prototype"
    CHAPTER = "8"
    CATEGORY = "Declarations and definitions"
    SEVERITY = "Required"
    DESCRIPTION = "Functions shall have prototype-form declarations with explicit parameter lists."
    RATIONALE = "Explicit parameter lists prevent implicit function interfaces and make type checking reliable."
    FIXABLE = True
    REFERENCES = ("MISRA C:2012 Rule 8.1",)
    PRIORITY = 30
    FIX_STRATEGY = "prototype_void_parameter"
    METADATA = {"chapter_title": "Declarations and definitions", "analysis": "regex"}

    PATTERN = r'^[^\S\n]*[A-Za-z_][\w\s\*]*\s+[A-Za-z_]\w*\s*\(\s*\)\s*$'

    def check(self, code, file_path):
        violations = []

        for match in re.finditer(self.PATTERN, code, re.MULTILINE):
            original = match.group().strip()
            line = code.count("\n", 0, match.start()) + 1
            suggestion = re.sub(r'\(\s*\)', '(void)', original, count=1)

            violations.append(
                self.create_violation(
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