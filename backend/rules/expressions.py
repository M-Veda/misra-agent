"""MISRA C:2012 expression rule plugins."""

import re

from rules.base_rule import BaseRule
from rules.rule_helpers import strip_comments, strip_string_literals

_OCTAL_LITERAL_PATTERN = re.compile(r"(?<![0-9A-Za-z_\\.])0[0-7]+(?![0-9A-Za-z_])")
_HEX_OR_OCTAL_LITERAL_PATTERN = re.compile(
    r"(?<![0-9A-Za-z_\\.])(?:0[xX][0-9A-Fa-f]+|0[0-7]+)(?![0-9A-Za-z_\\.])"
)
_INTEGER_LITERAL_PATTERN = re.compile(
    r"(?<![0-9A-Za-z_\\.])(?:0[xX][0-9A-Fa-f]+|0[0-7]+|[0-9]+)([uUlL]+)?(?![0-9A-Za-z_\\.])"
)
_STRING_LITERAL_PATTERN = re.compile(r'"(?:\\.|[^"\\])*"')
_CHARACTER_LITERAL_PATTERN = re.compile(r"'(?:\\.|[^'\\])'")


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

            cleaned_line = strip_string_literals(strip_comments(line))
            for match in _OCTAL_LITERAL_PATTERN.finditer(cleaned_line):
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


class Rule72(BaseRule):
    RULE_ID = "7.2"
    TITLE = "A u suffix shall be applied to all octal or hexadecimal constants that are represented in an unsigned form"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "Octal and hexadecimal constants should use an unsigned suffix when represented as unsigned values."
    RATIONALE = "Unsigned suffixes make the intended type of octal and hexadecimal literals explicit and avoid accidental sign-related behavior."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.2",)
    PRIORITY = 26
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            cleaned_line = strip_string_literals(strip_comments(line))
            for match in _HEX_OR_OCTAL_LITERAL_PATTERN.finditer(cleaned_line):
                literal = match.group(0)
                if re.search(r"[uU]", literal):
                    continue
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation=(
                            f"Hexadecimal or octal literal '{literal}' should include an unsigned suffix such as 'u' or 'U'."
                        ),
                    )
                )
                break
        return violations


class Rule73(BaseRule):
    RULE_ID = "7.3"
    TITLE = "The lowercase character l shall not be used in a literal suffix"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "Literal suffixes should use uppercase 'L' rather than lowercase 'l'."
    RATIONALE = "Lowercase suffix letters are easy to confuse with the digit '1' and reduce readability."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.3",)
    PRIORITY = 27
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            cleaned_line = strip_string_literals(strip_comments(line))
            for match in _INTEGER_LITERAL_PATTERN.finditer(cleaned_line):
                literal = match.group(0)
                suffix = match.group(1) or ""
                if not suffix or "l" not in suffix:
                    continue
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation=(
                            f"Literal suffix '{suffix}' uses lowercase 'l'; use uppercase 'L' instead."
                        ),
                    )
                )
                break
        return violations


class Rule74(BaseRule):
    RULE_ID = "7.4"
    TITLE = "A string literal shall not be assigned to an object unless the object is const-qualified"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "String literals should not be assigned to non-const objects."
    RATIONALE = "Assigning string literals to non-const objects can lead to undefined behavior and violates the intended immutability of string literals."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.4",)
    PRIORITY = 28
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            candidate_line = strip_comments(line)
            if not _STRING_LITERAL_PATTERN.search(candidate_line):
                continue
            if re.search(r"\bconst\b", candidate_line):
                continue
            if re.search(r"\b(?:char|wchar_t)\b\s*\*", candidate_line) and "=" in candidate_line:
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation="A string literal is assigned to a non-const object; make the object const-qualified or use a different initialization approach.",
                    )
                )
        return violations


class Rule75(BaseRule):
    RULE_ID = "7.5"
    TITLE = "A character literal shall not be assigned to an object unless the object is const-qualified"
    CHAPTER = "7"
    CATEGORY = "Expressions"
    SEVERITY = "Required"
    DESCRIPTION = "Character literals should not be assigned to non-const objects."
    RATIONALE = "Assigning character literals to non-const objects can lead to undefined behavior and violates the intended immutability of character literals."
    FIXABLE = False
    REFERENCES = ("MISRA C:2012 Rule 7.5",)
    PRIORITY = 29
    CAPABILITIES = ("text",)
    METADATA = {"chapter_title": "Expressions", "analysis": "text"}

    def check(self, code, file_path):
        violations = []
        for line_number, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            candidate_line = strip_comments(line)
            if not _CHARACTER_LITERAL_PATTERN.search(candidate_line):
                continue
            if re.search(r"\bconst\b", candidate_line):
                continue
            if re.search(r"\bchar\b", candidate_line) and "=" in candidate_line:
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line_number,
                        original=line,
                        explanation="A character literal is assigned to a non-const object; make the object const-qualified or use a different initialization approach.",
                    )
                )
        return violations

