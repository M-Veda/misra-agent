"""MISRA C:2012 expression rule plugins."""

import re

from rules.base_rule import BaseRule


class Rule71(BaseRule):
    RULE_ID = "7.1"
    TITLE = "Octal constants shall not be used"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "Octal constants shall not be used."
    RATIONALE = "Octal literals are easy to misread and can create ambiguity in expressions."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.1",)
    PRIORITY = 25
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            cleaned_line = self._strip_strings_and_char_literals(line)
            for match in re.finditer(r"(?<![0-9A-Za-z_\\.])0[0-7]+(?![0-9A-Za-z_])", cleaned_line):
                literal = match.group(0)
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation=(
                            f"Octal constant '{literal}' is not permitted; use a decimal or hexadecimal literal instead."
                        ),
                    )
                )
                break
        return violations

    @staticmethod
    def _strip_strings_and_char_literals(line):
        result = []
        index = 0
        in_string = None
        while index < len(line):
            char = line[index]
            if in_string is None:
                if char in {'"', "'"}:
                    in_string = char
                    result.append(" ")
                    index += 1
                    continue
                result.append(char)
                index += 1
                continue

            if char == "\\" and index + 1 < len(line):
                result.append(" ")
                result.append(" ")
                index += 2
                continue

            if char == in_string:
                in_string = None
                result.append(" ")
                index += 1
                continue

            result.append(" ")
            index += 1

        return "".join(result)
